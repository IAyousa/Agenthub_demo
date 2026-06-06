/**
 * AgentHub — 聊天核心 Store（Pinia）
 *
 * C5 重构：从 mock 数据切换到真实 API 调用。
 *
 * 架构决策：
 *   - REST API（C2/C3）：会话列表、历史消息、Agent 列表的"拉"取。
 *   - WebSocket（C4）：实时消息的"推"送和发送。
 *   - 流式 token 累积：isComplete=false → 追加到占位消息；isComplete=true → 固化。
 *   - Store 不直接 import wsClient 类，通过 getWsClient() 工厂获取。
 *
 * 技术栈：
 *   - Pinia：Vue 3 官方状态管理，composition API 风格（setup store）。
 *   - ref / computed：Vue 3 响应式原语。
 *   - 调用方的 ChatList/ChatWindow/ChatMessage 组件接口保持不变。
 */

import { defineStore } from 'pinia'
import { ref, computed } from 'vue'
import {
  getConversations,
  getConversationMessages,
  createConversation as apiCreateConversation,
  deleteConversation as apiDeleteConversation,
  getConversationArtifacts,
  type ConversationListItem,
  type MessageItem,
} from '../api/conversation'
import { getAgents, type AgentListItem } from '../api/agent'
import {
  getWsClient,
  destroyWsClient,
  type WsCallbacks,
  type MessageChunk,
  type AgentSwitchEvent,
} from '../websocket/wsClient'

// ============================================================================
// 类型定义（公开，供组件使用）
// ============================================================================

export interface Message {
  id: string
  role: 'user' | 'assistant' | 'system'
  type: 'text' | 'code' | 'diff' | 'artifact_preview'
  content: string
  created_at: string
  metadata?: Record<string, any>
}

export interface Conversation {
  id: string
  title: string
  messages: Message[]
}

export interface ConversationSummary {
  id: string
  title: string
  type: 'direct' | 'group'
  lastMessage: string
  updatedAt: string
  agentNames: string[]
  isArchived?: boolean
}

export interface OfficeMember {
  id: string
  name: string
  avatar: string
  role: 'owner' | 'admin' | 'member'
  status: 'online' | 'away' | 'offline'
  lastActive?: string
  seatIndex?: number
  isInviting?: boolean
  isRemoving?: boolean
}

export interface Office {
  id: string
  name: string
  description?: string
  theme: string
  maxMembers: number
  members: OfficeMember[]
  availableUsers: OfficeMember[]
  createdAt: string
  ownerId: string
}

export type AppView = 'chat' | 'office'

// ============================================================================
// 工具函数 — API 类型 → Store 类型映射
// ============================================================================

/**
 * 解码 API messageType 为前端展示用的 type 字段。
 *
 * API: "text" | "code" | "diff" | "preview_card"
 * Store: "text" | "code" | "diff" | "artifact_preview"
 */
function decodeMessageType(apiType: string): Message['type'] {
  if (apiType === 'preview_card') return 'artifact_preview'
  if (apiType === 'text' || apiType === 'code' || apiType === 'diff') return apiType
  return 'text'
}

/**
 * 提取 content 的纯文本表示。
 * API 中 code/diff/preview_card 类型的 content 是结构化 JSON 对象，
 * text 类型是纯字符串。前端渲染组件期望 content 始终为 string。
 */
function extractContentText(content: unknown): string {
  if (typeof content === 'string') return content
  if (content && typeof content === 'object') {
    const obj = content as Record<string, unknown>
    if (obj.type === 'code') return (obj.code as string) || ''
    if (obj.type === 'diff') return (obj.modifiedCode as string) || (obj.originalCode as string) || ''
    if (obj.type === 'preview_card') return (obj.description as string) || (obj.title as string) || ''
    return JSON.stringify(obj)
  }
  return ''
}

/** API MessageItem → Store Message */
function mapApiMessage(api: MessageItem): Message {
  return {
    id: api.id,
    role: api.senderType === 'user' ? 'user' : 'assistant',
    type: decodeMessageType(api.messageType),
    content: extractContentText(api.content),
    created_at: api.createdAt,
    metadata: {
      language: typeof api.content === 'object' ? (api.content as any).language : undefined,
      filename: typeof api.content === 'object' ? (api.content as any).filename : undefined,
      agentName: api.agentName,
    },
  }
}

// ============================================================================
// Store 定义
// ============================================================================

export const useChatStore = defineStore('chat', () => {
  // ---- 基础状态 ----
  const currentConversationId = ref<string>('conv_frontend_001')
  const mobileView = ref<'list' | 'chat'>('list')
  const currentView = ref<AppView>('chat')

  // ---- 连接与错误状态 ----
  const wsConnected = ref(false)
  const isLoading = ref(false)
  const isMessagesLoading = ref(false)
  const error = ref<string | null>(null)
  const agents = ref<AgentListItem[]>([])

  // ---- 数据状态（保留 mock 默认值，API 成功时覆盖）----
  const conversations = ref<Record<string, Conversation>>({
    'conv_frontend_001': {
      id: 'conv_frontend_001',
      title: '前端博客开发',
      messages: [
        {
          id: 'welcome-frontend',
          role: 'assistant',
          type: 'text',
          content: '你好！我是 Claude Code，我会协助你完成前端博客的开发任务。让我们开始吧！',
          created_at: new Date().toISOString()
        }
      ]
    },
    'conv_backend_001': {
      id: 'conv_backend_001',
      title: '后端接口重构',
      messages: [
        {
          id: 'welcome-backend',
          role: 'assistant',
          type: 'text',
          content: '你好！我是 Codex，我会协助你重构后端接口。请告诉我需要重构哪些接口？',
          created_at: new Date().toISOString()
        }
      ]
    },
    'conv_review_001': {
      id: 'conv_review_001',
      title: '代码审查',
      messages: [
        {
          id: 'welcome-review',
          role: 'assistant',
          type: 'text',
          content: '你好！代码审查已准备就绪。请提交需要审查的代码。',
          created_at: new Date().toISOString()
        }
      ]
    }
  })

  const conversationList = ref<ConversationSummary[]>([
    {
      id: 'conv_frontend_001',
      title: '前端博客开发',
      type: 'direct',
      lastMessage: '已生成 App.jsx 组件',
      updatedAt: new Date(Date.now() - 3600000).toISOString(),
      agentNames: ['Claude Code'],
    },
    {
      id: 'conv_backend_001',
      title: '后端接口重构',
      type: 'direct',
      lastMessage: '完成了 User API 和 Message API 的重构',
      updatedAt: new Date(Date.now() - 7200000).toISOString(),
      agentNames: ['Codex'],
    },
    {
      id: 'conv_review_001',
      title: '代码审查',
      type: 'direct',
      lastMessage: '发现 3 处潜在性能问题，建议优化',
      updatedAt: new Date(Date.now() - 86400000).toISOString(),
      agentNames: ['Claude Code', 'Codex'],
    },
  ])

  // ---- 流式消息状态 ----
  /** 当前正在流式接收的消息的临时 ID */
  const streamingMessageId = ref<string | null>(null)
  /** 流过过程中当前发言的 Agent */
  const currentAgentId = ref<string>('')
  const currentAgentName = ref<string>('')
  /** 用户选择的 Agent（用于下一条消息的路由） */
  const selectedAgentId = ref<string>('agent_claude_001')

  // ---- WebSocket 回调（定义在 setup 闭包中，捕获 store 方法）----

  const handleToken = (chunk: MessageChunk) => {
    const convId = currentConversationId.value
    if (!convId) return

    const msgs = conversations.value[convId]?.messages
    if (!msgs) return

    let streamMsg: Message | undefined

    if (streamingMessageId.value) {
      streamMsg = msgs.find(m => m.id === streamingMessageId.value)
    }

    if (!streamMsg) {
      // 第一条 token 到达时创建占位消息
      const newId = `streaming_${Date.now()}`
      streamMsg = {
        id: newId,
        role: 'assistant',
        type: 'text',
        content: '',
        created_at: new Date().toISOString(),
        metadata: { agentId: chunk.agentId, agentName: chunk.agentName },
      }
      msgs.push(streamMsg)
      streamingMessageId.value = newId
    }

    if (chunk.isComplete) {
      streamMsg.id = chunk.messageId || streamMsg.id
      if (chunk.content && chunk.content !== streamMsg.content) {
        streamMsg.content = chunk.content
      }
      streamMsg.type = chunk.messageType === 'preview_card' ? 'artifact_preview'
        : (chunk.messageType as Message['type']) || 'text'
      if (chunk.messageType !== 'text' && streamMsg.metadata) {
        streamMsg.metadata.agentId = chunk.agentId
        streamMsg.metadata.agentName = chunk.agentName
      }
      streamingMessageId.value = null
      isLoading.value = false
    } else {
      streamMsg.content += chunk.content
      currentAgentId.value = chunk.agentId
      currentAgentName.value = chunk.agentName
      if (streamMsg.metadata) {
        streamMsg.metadata.agentId = chunk.agentId
        streamMsg.metadata.agentName = chunk.agentName
      }
    }
  }

  const handleAgentSwitch = (event: AgentSwitchEvent) => {
    currentAgentId.value = event.agentId
    currentAgentName.value = event.agentName
  }

  const handleConnectionChange = (connected: boolean) => {
    wsConnected.value = connected
    if (connected && currentConversationId.value) {
      const ws = getWsClient(wsCallbacks)
      const ok = ws.subscribe(currentConversationId.value)
      if (!ok) {
        console.warn('[chat] subscribe failed on reconnect for', currentConversationId.value)
      }
    }
  }

  const handleWsError = (err: string) => {
    error.value = err
    isLoading.value = false
  }

  const wsCallbacks: WsCallbacks = {
    onToken: handleToken,
    onAgentSwitch: handleAgentSwitch,
    onConnectionChange: handleConnectionChange,
    onError: handleWsError,
  }

  // ---- 派生状态（计算属性，接口与重构前完全兼容）----

  const currentMessages = computed(() => {
    return conversations.value[currentConversationId.value]?.messages || []
  })

  const currentTitle = computed(() => {
    return conversations.value[currentConversationId.value]?.title || 'Chat'
  })

  // ==========================================================================
  // 聊天相关操作
  // ==========================================================================

  /** 从 API 加载会话列表，成功时覆盖 mock 数据 */
  async function loadConversationList() {
    try {
      const res = await getConversations(false)
      // API 成功 → 用真实数据替换 mock
      conversationList.value = res.data.conversations.map(c => ({
        ...c,
        isArchived: c.isArchived ?? false,
      }))
      error.value = null
    } catch {
      // API 不可用时保留 mock 数据，不报错
    }
  }

  /** 从 API 加载 Agent 列表 */
  async function loadAgents() {
    try {
      const res = await getAgents()
      agents.value = res.data.agents
    } catch {
      // Agent 列表加载失败不阻塞 UI，保留空数组
    }
  }

  /**
   * 加载指定会话的历史消息，成功时覆盖本地数据。
   * 如果 conversation 不在 map 中，从 conversationList 推断标题。
   */
  async function loadMessages(conversationId: string) {
    isMessagesLoading.value = true
    try {
      const [msgRes, artRes] = await Promise.all([
        getConversationMessages(conversationId, 0, 50),
        getConversationArtifacts(conversationId).catch(() => ({ data: { artifacts: [] } })),
      ])
      const messages: Message[] = msgRes.data.messages.map(mapApiMessage).reverse()
      // API returns newest-first (DESC); reverse to display oldest-first in chat UI

      // Merge artifacts as preview_card messages
      const artifacts = artRes.data.artifacts || []
      for (const a of artifacts) {
        const ext = (a.filename || '').split('.').pop()?.toLowerCase() || 'plaintext'
        messages.push({
          id: `artifact-${a.id}`,
          role: 'assistant' as const,
          type: 'artifact_preview' as const,
          content: a.filename,
          created_at: a.createdAt,
          metadata: {
            title: a.filename,
            language: ext,
            previewUrl: `/artifacts/${a.id}`,
            artifactId: a.id,
          },
        })
      }
      // Sort by created_at to interleave artifacts with messages
      messages.sort((a, b) => new Date(a.created_at).getTime() - new Date(b.created_at).getTime())

      if (!conversations.value[conversationId]) {
        conversations.value[conversationId] = {
          id: conversationId,
          title: conversationList.value.find(c => c.id === conversationId)?.title || '',
          messages: [],
        }
      }
      conversations.value[conversationId].messages = messages
      error.value = null
    } catch {
      // API 不可用时保留已有消息（mock 或之前加载的），不覆盖
    } finally {
      isMessagesLoading.value = false
    }
  }

  /** 初始化 WebSocket 连接并订阅当前会话 */
  function initWebSocket() {
    const ws = getWsClient(wsCallbacks)
    ws.connect()
    // 订阅由 handleConnectionChange 在 STOMP 连接就绪后自动完成，
    // 不能在这里同步调用 subscribe()——v7 要求连接已建立。
  }

  /**
   * 选择/切换会话。
   *
   * 切换时：取消旧 topic 订阅 → 更新 currentConversationId →
   * 加载新会话历史消息 → 订阅新 topic。
   *
   * 接口签名兼容旧版本（组件无需修改）。
   */
  function selectConversation(id: string) {
    if (currentConversationId.value === id) return

    // 取消旧订阅
    if (wsConnected.value && currentConversationId.value) {
      const ws = getWsClient(wsCallbacks)
      ws.unsubscribe(currentConversationId.value)
    }

    const prevId = currentConversationId.value
    currentConversationId.value = id
    closeArtifact()
    isLoading.value = false
    streamingMessageId.value = null
    error.value = null

    // 加载新会话消息
    if (id) {
      loadMessages(id)
      if (wsConnected.value) {
        const ws = getWsClient(wsCallbacks)
        const ok = ws.subscribe(id)
        if (!ok) {
          console.warn('[chat] subscribe failed for', id, '- will retry on reconnect')
        }
      }
    }
  }

  /**
   * 发送消息（WebSocket 路径）。
   *
   * 数据流：
   *   1. 用户消息追加到本地 messages 数组（立即渲染）
   *   2. wsClient.sendMessage() → /app/chat.send → Java → Python → SSE
   *   3. handleToken 回调逐 token 追加到占位消息
   *   4. isComplete=true 时固化消息、解除 isLoading
   *
   * 注意：仅发送 conversationId + content，不传 agentType/systemPrompt。
   */
  function sendMessage(content: string) {
    const convId = currentConversationId.value
    if (!convId || !content.trim()) return

    // 1. 先添加用户消息（确保无论后端是否可用，用户输入始终有反馈）
    const userMsg: Message = {
      id: `temp_user_${Date.now()}`,
      role: 'user',
      type: 'text',
      content: content.trim(),
      created_at: new Date().toISOString(),
    }

    if (!conversations.value[convId]) {
      conversations.value[convId] = { id: convId, title: '', messages: [] }
    }
    conversations.value[convId].messages.push(userMsg)

    // 2. 仅在 WebSocket 已连接时发送；未连接则提示用户
    const ws = getWsClient(wsCallbacks)
    if (!ws.connected) {
      error.value = '服务端连接出现问题，请稍后重试'
      return
    }

    isLoading.value = true
    error.value = null
    ws.sendMessage({ conversationId: convId, content: content.trim(), agentId: selectedAgentId.value })
  }

  /**
   * 创建新会话，返回新会话的 ID。
   *
   * 优先调用 REST API；API 不可用时回退到本地创建（维持 UI 可用）。
   * 调用方（ChatList）应在拿到 ID 后执行 router.push('/chat/' + id) 完成导航。
   */
  async function createConversation(title: string): Promise<string> {
    try {
      const res = await apiCreateConversation({ title, type: 'direct', agentIds: [] })
      const id = res.data.id
      conversationList.value.unshift({
        id,
        title: res.data.title,
        type: res.data.type,
        lastMessage: '新会话已创建',
        updatedAt: res.data.createdAt,
        agentNames: [],
      })
      conversations.value[id] = { id, title: res.data.title, messages: [] }
      mobileView.value = 'chat'
      error.value = null
      return id
      // currentConversationId is set by selectConversation() via router watch
    } catch {
      // API 不可用 → 本地 fallback
      const id = `conv_${Date.now()}`
      conversationList.value.unshift({
        id,
        title,
        type: 'direct',
        lastMessage: '新会话已创建',
        updatedAt: new Date().toISOString(),
        agentNames: [],
      })
      conversations.value[id] = {
        id,
        title,
        messages: [{
          id: `welcome-${id}`,
          role: 'assistant',
          type: 'text',
          content: '新会话已创建，你可以选择参与的 Agent 并开始对话。',
          created_at: new Date().toISOString()
        }]
      }
      currentConversationId.value = id
      mobileView.value = 'chat'
      return id
    }
  }

  /**
   * 仅本地添加消息（兼容旧接口，ChatWindow 不再直接调用此方法，
   * 改为调用 sendMessage()）。
   */
  function addMessage(message: Message) {
    if (conversations.value[currentConversationId.value]) {
      conversations.value[currentConversationId.value].messages.push(message)
    }
  }

  async function deleteConversation(id: string) {
    try {
      await apiDeleteConversation(id)
    } catch {
      // API 失败也继续删除本地数据
    }
    conversationList.value = conversationList.value.filter(c => c.id !== id)
    delete conversations.value[id]
    if (currentConversationId.value === id) {
      const remaining = conversationList.value
      if (remaining.length > 0) {
        selectConversation(remaining[0].id)
      } else {
        currentConversationId.value = ''
      }
    }
  }

  // ==========================================================================
  // 办公室管理（保持 mock 不变，P2 阶段迁至 API）
  // ==========================================================================

  const offices = ref<Office[]>([
    {
      id: 'office-1',
      name: '默认办公室',
      description: '团队协作空间',
      theme: 'modern',
      maxMembers: 8,
      createdAt: new Date().toISOString(),
      ownerId: '1',
      members: [
        { id: '1', name: '你', avatar: 'https://api.dicebear.com/7.x/avataaars/svg?seed=Felix', role: 'owner', status: 'online', lastActive: '刚刚' },
        { id: '2', name: '张小明', avatar: 'https://api.dicebear.com/7.x/avataaars/svg?seed=xiaoming', role: 'admin', status: 'online', lastActive: '2分钟前', seatIndex: 0 },
        { id: '3', name: '李小红', avatar: 'https://api.dicebear.com/7.x/avataaars/svg?seed=xiaohong', role: 'member', status: 'away', lastActive: '15分钟前', seatIndex: 1 },
        { id: '4', name: '王大伟', avatar: 'https://api.dicebear.com/7.x/avataaars/svg?seed=dawei', role: 'member', status: 'offline', lastActive: '1小时前', seatIndex: 2 },
      ],
      availableUsers: [
        { id: 'u100', name: '陈静静', avatar: 'https://api.dicebear.com/7.x/avataaars/svg?seed=jingjing', role: 'member', status: 'online' },
        { id: 'u101', name: '刘先生', avatar: 'https://api.dicebear.com/7.x/avataaars/svg?seed=liu', role: 'member', status: 'online' },
        { id: 'u102', name: '产品经理', avatar: 'https://api.dicebear.com/7.x/avataaars/svg?seed=pm', role: 'member', status: 'away' },
      ],
    },
  ])

  const currentOfficeId = ref<string>('office-1')

  const currentOffice = computed(() => offices.value.find(o => o.id === currentOfficeId.value))

  const officeMembers = computed(() => currentOffice.value?.members || [])

  const availableUsersToInvite = computed(() => currentOffice.value?.availableUsers || [])

  function switchOffice(officeId: string) {
    if (offices.value.find(o => o.id === officeId)) {
      currentOfficeId.value = officeId
    }
  }

  function createOffice(data: { name: string; description: string; maxMembers: number; theme: string }) {
    const newOffice: Office = {
      id: `office-${Date.now()}`,
      name: data.name,
      description: data.description,
      theme: data.theme,
      maxMembers: data.maxMembers,
      createdAt: new Date().toISOString(),
      ownerId: '1',
      members: [
        { id: '1', name: '你', avatar: 'https://api.dicebear.com/7.x/avataaars/svg?seed=Felix', role: 'owner', status: 'online', lastActive: '刚刚' },
      ],
      availableUsers: [
        { id: 'u100', name: '陈静静', avatar: 'https://api.dicebear.com/7.x/avataaars/svg?seed=jingjing', role: 'member', status: 'online' },
        { id: 'u101', name: '刘先生', avatar: 'https://api.dicebear.com/7.x/avataaars/svg?seed=liu', role: 'member', status: 'online' },
        { id: 'u102', name: '产品经理', avatar: 'https://api.dicebear.com/7.x/avataaars/svg?seed=pm', role: 'member', status: 'away' },
        { id: 'u103', name: '数据分析师', avatar: 'https://api.dicebear.com/7.x/avataaars/svg?seed=data', role: 'member', status: 'offline' },
      ],
    }
    offices.value.push(newOffice)
    currentOfficeId.value = newOffice.id
    return newOffice
  }

  function deleteOffice(officeId: string) {
    const index = offices.value.findIndex(o => o.id === officeId)
    if (index > -1) {
      offices.value.splice(index, 1)
      if (currentOfficeId.value === officeId && offices.value.length > 0) {
        currentOfficeId.value = offices.value[0].id
      }
    }
  }

  function findEmptySeat(): number {
    const used = officeMembers.value.filter(m => m.seatIndex !== undefined).map(m => m.seatIndex!)
    for (let i = 0; i < 8; i++) {
      if (!used.includes(i)) return i
    }
    return 0
  }

  function inviteMember(userId: string, targetSeatIdx?: number) {
    if (!currentOffice.value) return
    const user = currentOffice.value.availableUsers.find(u => u.id === userId)
    if (user) {
      const emptySeat = targetSeatIdx !== undefined ? targetSeatIdx : findEmptySeat()
      currentOffice.value.members.push({ ...user, lastActive: '刚刚', seatIndex: emptySeat })
      currentOffice.value.availableUsers = currentOffice.value.availableUsers.filter(u => u.id !== userId)
    }
  }

  function removeMember(memberId: string) {
    if (!currentOffice.value) return
    const member = currentOffice.value.members.find(m => m.id === memberId)
    if (member && member.role !== 'owner') {
      currentOffice.value.members = currentOffice.value.members.filter(m => m.id !== memberId)
      currentOffice.value.availableUsers.push({ ...member, isInviting: false, isRemoving: false })
    }
  }

  // ==========================================================================
  // Artifact 状态（不变）
  // ==========================================================================

  const currentArtifact = ref<{
    id: string
    title: string
    code: string
    language: string
  } | null>(null)
  const isArtifactVisible = ref(false)

  function showArtifact(artifact: { id: string; title: string; code: string; language: string }) {
    currentArtifact.value = artifact
    isArtifactVisible.value = true
  }

  function closeArtifact() {
    isArtifactVisible.value = false
  }

  // ==========================================================================
  // 公开接口（对外导出，组件通过 useChatStore() 访问）
  // ==========================================================================

  return {
    // 基础状态
    currentConversationId,
    mobileView,
    currentView,
    // 数据
    conversations,
    conversationList,
    agents,
    // 连接与加载
    wsConnected,
    isLoading,
    isMessagesLoading,
    error,
    // 流式状态
    streamingMessageId,
    currentAgentId,
    currentAgentName,
    selectedAgentId,
    // 派生
    currentMessages,
    currentTitle,
    // 聊天操作
    loadConversationList,
    loadAgents,
    loadMessages,
    initWebSocket,
    selectConversation,
    sendMessage,
    createConversation,
    deleteConversation,
    addMessage,
    // 办公室
    offices,
    currentOfficeId,
    currentOffice,
    officeMembers,
    availableUsersToInvite,
    switchOffice,
    createOffice,
    deleteOffice,
    inviteMember,
    removeMember,
    // Artifact
    currentArtifact,
    isArtifactVisible,
    showArtifact,
    closeArtifact,
  }
})
