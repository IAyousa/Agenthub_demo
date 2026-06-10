/**
 * WebSocket STOMP 客户端 — 实时消息收发
 *
 * 对照 API 契约文档 v1.0 第 3 节（WebSocket 协议）。
 *
 * 技术栈说明：
 *   - STOMP（Simple Text Oriented Messaging Protocol）：运行在 WebSocket 之上的
 *     消息子协议，提供"目的地"（destination）和"订阅"（subscribe）语义，
 *     比裸 WebSocket 更适合聊天应用。
 *
 *   - @stomp/stompjs：STOMP 客户端库，连接/订阅/发送/心跳/重连一站式处理。
 *     不需要手动管理 WebSocket 生命周期。
 *
 *   - SockJS：WebSocket 不可用时（企业代理/旧浏览器）自动降级为
 *     HTTP long-polling。Spring Boot 的 /ws-chat 端点同时接受
 *     原生 WebSocket 和 SockJS 连接。
 *
 *   - 设计模式：回调模式（callbacks）。wsClient 负责传输层，
 *     Store 层通过回调接收 token，更新 Pinia state。两层解耦。
 *
 * 数据流：
 *   用户键入 → ChatWindow 调用 sendMessage()
 *     → wsClient.publish('/app/chat.send', { conversationId, content })
 *       → Spring Boot WebSocketController
 *         → AgentGatewayService → Python → SSE → Java 逐 token 推送
 *           → wsClient 收到 STOMP 消息 → onToken 回调 → Store 追加 token → UI 打字机效果
 */

import { Client, type IMessage } from '@stomp/stompjs'

// ============================================================================
// 连接配置
// ============================================================================

/**
 * WebSocket 连接端点。
 *
 * 注意：实际代码使用 /ws-chat，与 API 契约文档中的 /ws 不一致。
 * 文档写的是 `http://localhost:8080/ws`，但 WebSocketConfig.java 中
 * registerStompEndpoints 注册的路径为 "/ws-chat"。
 * 此处以实际代码为准，后续统一改文档。
 */
const WS_ENDPOINT = 'http://localhost:8080/ws-chat'

/** 断线重连间隔（毫秒），STOMP 客户端内置重连机制 */
const RECONNECT_DELAY = 5000

/** 心跳间隔（毫秒），双向心跳保持连接活跃 */
const HEARTBEAT_MS = 10000

// ============================================================================
// TypeScript 接口 — WebSocket 消息传输格式
// ============================================================================

/**
 * 流式消息块（后端 → 前端）。
 *
 * 对照 API 契约文档 3.3.2 节 MessageChunk 格式。
 * 每次 SSE token 到达时，Java 后端通过 STOMP 推送到订阅的 conversation topic。
 */
export interface MessageChunk {
  content: string
  isComplete: boolean
  agentId: string
  agentName: string
  messageType: 'text' | 'code' | 'diff' | 'preview_card' | 'project_bundle' | 'error'
  messageId?: string   // 仅在 isComplete=true 时存在
  metadata?: Record<string, any>  // 额外元数据（如 project_bundle 的 files 列表）
}

/**
 * Agent 切换事件（后端 → 前端）。
 *
 * 对照 API 契约文档 3.3.2 节 agent_switch 事件。
 * Orchestrator 切换调用的 Agent 时推送，前端据此切换头像和发送者名称。
 * 当前 P0 阶段 Orchestrator 未实现，此事件由后端直接发送。
 */
export interface AgentSwitchEvent {
  type: 'agent_switch'
  agentId: string
  agentName: string
}

/**
 * 发送消息的请求体（前端 → 后端）。
 *
 * 对照 API 契约文档 3.3.1 节。
 * 仅传 conversationId + content，不传 agentType/systemPrompt。
 * Agent 调度由 Python Orchestrator 自动完成。
 */
export interface SendMessagePayload {
  conversationId: string
  content: string
  agentId?: string
}

/**
 * wsClient 对外暴露的回调接口。
 *
 * 每个回调对应一种 STOMP 消息类型，Store 层通过传入回调来响应传输层事件。
 * 这种"回调注入"模式避免 wsClient 直接依赖 Pinia store。
 */
export interface WsCallbacks {
  /** 收到流式 token 时触发，每次一条 SSE chunk */
  onToken: (chunk: MessageChunk) => void

  /** 收到 Agent 切换事件时触发 */
  onAgentSwitch: (event: AgentSwitchEvent) => void

  /** 连接状态变化时触发，UI 可据此显示/隐藏连接指示器 */
  onConnectionChange: (connected: boolean) => void

  /** STOMP 协议层错误时触发（非业务错误） */
  onError: (error: string) => void
}

// ============================================================================
// WebSocket 客户端实现
// ============================================================================

class WsClient {
  private client: Client
  private callbacks: WsCallbacks
  /** 当前活跃的订阅，key = topic 路径，value = 订阅引用 */
  private subscriptions: Map<string, { unsubscribe: () => void }> = new Map()

  constructor(callbacks: WsCallbacks) {
    this.callbacks = callbacks

    this.client = new Client({
      /**
       * webSocketFactory：STOMP 客户端不直接创建 WebSocket，而是通过
       * 这个工厂函数获取。这里返回 SockJS 实例，使得不支持 WebSocket
       * 的环境能降级为 HTTP long-polling。
       */
      // 使用原生 WebSocket 替代 SockJS，避免 SockJS 帧缓冲导致流式消息被批量延迟投递
      // 注意：/ws-chat 端点同时支持 SockJS 和原生 WebSocket（Spring 自动协商）
      brokerURL: 'ws://localhost:8080/ws-chat',

      /** 断线后自动重连，首次延迟 5 秒 */
      reconnectDelay: RECONNECT_DELAY,

      /**
       * 双向心跳：客户端每 10 秒发一次心跳，同时期望服务端也每 10 秒
       * 回一个心跳。如果 3 次心跳没收到回复，视为断线并触发重连。
       *
       * 在 @stomp/stompjs v7 中，只要 heartbeatOutgoing > 0 就会自动启用心跳，
       * 不需要额外的 enabled 开关。
       */
      heartbeatIncoming: HEARTBEAT_MS,
      heartbeatOutgoing: HEARTBEAT_MS,

      // ---- 生命周期回调 ----

      /**
       * 连接成功时触发（STOMP CONNECTED 帧收到后）。
       *
       * 注意：此时可以开始订阅和发送消息。在 onConnect 之前调用 publish/subscribe
       * 会失败（client.connected === false）。
       */
      onConnect: () => {
        this.callbacks.onConnectionChange(true)
        // 重连后自动恢复之前的订阅
        // 注意：需要由外部（Store）在 onConnectionChange 回调中重新订阅
      },

      onDisconnect: () => {
        this.callbacks.onConnectionChange(false)
      },

      /**
       * STOMP 协议层错误（非 HTTP 层，如目的地不存在、帧格式错误）。
       *
       * 技术细节：STOMP ERROR 帧由服务端主动发送，包含错误描述。
       * 不同于 WebSocket 连接断开——连接可能正常，但消息路由出错。
       */
      onStompError: (frame) => {
        const errorMsg = frame.headers['message'] || 'STOMP 协议错误'
        this.callbacks.onError(errorMsg)
      },
    })
  }

  // ---- 生命周期管理 ----

  /** 建立 WebSocket 连接并执行 STOMP 握手 */
  connect(): void {
    if (this.client.active) return
    this.client.activate()
  }

  /** 断开连接，清理所有订阅 */
  disconnect(): void {
    this.subscriptions.forEach((sub) => {
      try { sub.unsubscribe() } catch { /* ignore */ }
    })
    this.subscriptions.clear()

    if (this.client.active) {
      this.client.deactivate()
    }
  }

  /** 是否处于连接状态 */
  get connected(): boolean {
    return this.client.connected
  }

  // ---- 消息收发 ----

  /**
   * 订阅指定会话的实时消息。
   *
   * 对齐 API 契约 3.2 节：后端 → 前端 /topic/conversation.{conversationId}
   *
   * 实现细节：
   *   - 每次收到 STOMP 消息时解析 JSON body，根据 type 字段分发到
   *     onToken 或 onAgentSwitch 回调。
   *   - 如果已订阅同一 topic，先取消旧订阅（避免重复回调）。
   *   - 订阅返回值存入 Map，用于 disconnect() 时批量清理。
   */
  subscribe(conversationId: string): boolean {
    if (!this.client.connected) {
      console.warn('[wsClient] Cannot subscribe: STOMP not connected')
      return false
    }

    const topic = `/topic/conversation.${conversationId}`

    // 避免同一 topic 重复订阅
    const existing = this.subscriptions.get(topic)
    if (existing) {
      existing.unsubscribe()
    }

    const subscription = this.client.subscribe(topic, (message: IMessage) => {
      try {
        const data = JSON.parse(message.body)

        // agent_switch 事件：Orchestrator 切换 Agent
        if (data.type === 'agent_switch') {
          this.callbacks.onAgentSwitch({
            type: 'agent_switch',
            agentId: data.agentId,
            agentName: data.agentName,
          })
          return
        }

        // 普通流式 token（含 isComplete 标识）
        // 跳过空内容的心跳/空帧消息（后台标签页可能收到浏览器发送的空 PONG 帧）
        if (data.content === undefined && data.isComplete === undefined) return

        this.callbacks.onToken({
          content: data.content,
          isComplete: data.isComplete ?? false,
          agentId: data.agentId ?? '',
          agentName: data.agentName ?? '',
          messageType: data.messageType ?? 'text',
          messageId: data.messageId,
          metadata: data.metadata,
        })
      } catch {
        // 静默丢弃无效消息（后台标签页时浏览器可能收到空帧/心跳帧），
        // 不弹红色 toast——只有真正的连接断开才提示用户
        console.warn('[wsClient] Skip invalid message:', message.body?.substring(0, 100))
      }
    })

    this.subscriptions.set(topic, subscription)
    return true
  }

  /**
   * 取消订阅指定会话。
   *
   * 切换会话时调用，避免收到不需要的会话消息。
   */
  unsubscribe(conversationId: string): void {
    const topic = `/topic/conversation.${conversationId}`
    const sub = this.subscriptions.get(topic)
    if (sub) {
      sub.unsubscribe()
      this.subscriptions.delete(topic)
    }
  }

  /**
   * 发送聊天消息。
   *
   * 对齐 API 契约 3.3.1 节：前端 → 后端 /app/chat.send
   *
   * 只发送 conversationId + content，不传 agentType/systemPrompt。
   * Agent 调度由 Python Orchestrator 自动完成。
   *
   * 使用 JSON.stringify 序列化发送体，body 为 string 类型。
   */
  sendMessage(payload: SendMessagePayload): void {
    if (!this.client.connected) {
      this.callbacks.onError('未连接到服务器，请稍后重试')
      return
    }

    this.client.publish({
      destination: '/app/chat.send',
      body: JSON.stringify(payload),
    })
  }
}

// ============================================================================
// 模块单例 — 整个前端只需一个 WebSocket 连接
// ============================================================================

/** 全局单例。使用时先调用 setCallbacks() 注入回调，再 connect() */
let instance: WsClient | null = null

/**
 * 获取或创建 wsClient 单例。
 *
 * 为什么用单例：
 *   - 浏览器通常只维护一个 WebSocket 连接（多连接浪费资源）
 *   - 多个组件（ChatView、OfficeView）共享同一个 STOMP 连接
 *   - 订阅/取消订阅只改变 topic 列表，不创建新连接
 */
export function getWsClient(callbacks: WsCallbacks): WsClient {
  if (!instance) {
    instance = new WsClient(callbacks)
  }
  return instance
}

/**
 * 销毁当前 wsClient 实例并断开连接。
 * 用于登出或强制重置连接状态。
 */
export function destroyWsClient(): void {
  if (instance) {
    instance.disconnect()
    instance = null
  }
}
