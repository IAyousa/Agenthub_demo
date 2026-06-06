/**
 * Conversation API — 会话管理接口封装
 *
 * 对照 API 契约文档 v1.0 第 2.2 节（会话管理）+ 2.2.7（历史消息）+ 2.2.8（置顶消息）。
 * 所有请求/响应字段使用 camelCase，与后端 Spring Boot DTO 对齐。
 *
 * 技术栈说明：
 *   - axios：基于 Promise 的 HTTP 客户端，替代原生 fetch。
 *     优势：自动 JSON 序列化/反序列化、请求/响应拦截器、超时控制、取消请求。
 *   - TypeScript 泛型：`apiClient.get<T>(url)` 指定响应体的类型，
 *     编辑器和 CI 阶段即可发现字段拼写错误，避免运行时调试。
 */

import apiClient from './index'

// ============================================================================
// TypeScript 接口 — API 层数据形状（与 store 层的 Message/Conversation 不同，此处只描述 HTTP 传输格式）
// ============================================================================

/** 会话列表项（GET /conversations 响应中单个元素） */
export interface ConversationListItem {
  id: string
  title: string
  type: 'direct' | 'group'
  lastMessage: string
  updatedAt: string
  agentNames: string[]
  isArchived: boolean
}

/** 会话详情中的 Agent 摘要（GET /conversations/{id} 响应） */
export interface AgentBrief {
  id: string
  name: string
  type: string
  avatarUrl: string
}

/** 会话详情（GET /conversations/{id} 响应） */
export interface ConversationDetail {
  id: string
  title: string
  type: 'direct' | 'group'
  agents: AgentBrief[]
  createdAt: string
  updatedAt: string
}

/** 创建会话的请求体（POST /conversations） */
export interface CreateConversationRequest {
  title: string
  type: 'direct' | 'group'
  agentIds: string[]
}

/** 创建会话的响应体 */
export interface CreateConversationResponse {
  id: string
  title: string
  type: 'direct' | 'group'
  agentIds: string[]
  createdAt: string
}

/** 更新会话的请求体（PATCH /conversations/{id}），所有字段可选 */
export interface UpdateConversationRequest {
  title?: string
  isArchived?: boolean
}

/** 更新会话的响应体 */
export interface UpdateConversationResponse {
  id: string
  title: string
  isArchived: boolean
  updatedAt: string
}

/** 删除会话的响应体 */
export interface DeleteConversationResponse {
  message: string
  deletedId: string
}

/** 修改会话 Agent 的请求体（PUT /conversations/{id}/agents） */
export interface UpdateAgentsRequest {
  agentIds: string[]
}

/** 修改会话 Agent 的响应体 */
export interface UpdateAgentsResponse {
  id: string
  agentIds: string[]
  updatedAt: string
}

/**
 * 消息内容结构 — 当 messageType 为 "code" 时的 content JSON 形状。
 * 注意：API 契约中 content 字段在 messageType="text" 时是纯字符串，
 * 在 messageType="code"/"diff"/"preview_card" 时是结构化 JSON 对象。
 */
export interface CodeContent {
  type: 'code'
  language: string
  code: string
  filename?: string
}

export interface DiffContent {
  type: 'diff'
  originalCode: string
  modifiedCode: string
  language: string
  filename?: string
}

export interface PreviewCardContent {
  type: 'preview_card'
  title: string
  description: string
  previewUrl: string
  fileType: string
}

/** 消息内容：text 类型时为字符串，其他类型时为结构化对象 */
export type MessageContent = string | CodeContent | DiffContent | PreviewCardContent

/** 历史消息项（GET /conversations/{id}/messages 响应中单个元素） */
export interface MessageItem {
  id: string
  senderType: 'user' | 'agent'
  content: MessageContent
  messageType: 'text' | 'code' | 'diff' | 'preview_card'
  createdAt: string
  agentName?: string
}

/** 历史消息分页响应 */
export interface MessagePage {
  messages: MessageItem[]
  page: number
  size: number
  total: number
}

/** 置顶消息的请求体（PUT /messages/{id}/pin） */
export interface PinRequest {
  pinned: boolean
}

/** 置顶消息的响应体 */
export interface PinResponse {
  id: string
  pinned: boolean
}

// ============================================================================
// API 函数
// ============================================================================

/**
 * 获取会话列表。
 *
 * GET /conversations?archived=false
 *
 * 技术细节：
 *   - `params` 选项自动拼接查询字符串（axios 处理 URL 编码）。
 *   - 泛型 `<{ conversations: ConversationListItem[] }>` 指定 response.data 的类型。
 *   - 这个形状与 API 契约文档 2.2.1 节完全对齐。
 */
export function getConversations(archived = false) {
  return apiClient.get<{ conversations: ConversationListItem[] }>('/conversations', {
    params: { archived },
  })
}

/**
 * 创建新会话。
 *
 * POST /conversations
 *
 * 技术细节：
 *   - 第二个参数是请求体，axios 自动设置 Content-Type: application/json。
 *   - 201 Created 也被 axios 视为成功（2xx 范围内），不需要额外配置。
 */
export function createConversation(data: CreateConversationRequest) {
  return apiClient.post<CreateConversationResponse>('/conversations', data)
}

/**
 * 获取会话详情（含参与的 Agent 列表）。
 *
 * GET /conversations/{id}
 */
export function getConversationDetail(id: string) {
  return apiClient.get<ConversationDetail>(`/conversations/${id}`)
}

/**
 * 更新会话（标题、归档状态）。
 *
 * PATCH /conversations/{id}
 *
 * 技术细节：
 *   - 使用 PATCH 而非 PUT：只发送需要修改的字段（partial update），减少网络负载。
 *   - `UpdateConversationRequest` 所有字段标记为可选 `?`。
 */
export function updateConversation(id: string, data: UpdateConversationRequest) {
  return apiClient.patch<UpdateConversationResponse>(`/conversations/${id}`, data)
}

/**
 * 删除会话。
 *
 * DELETE /conversations/{id}
 */
export function deleteConversation(id: string) {
  return apiClient.delete<DeleteConversationResponse>(`/conversations/${id}`)
}

/**
 * 修改会话关联的 Agent 列表（整体替换）。
 *
 * PUT /conversations/{id}/agents
 *
 * 技术细节：
 *   - 用 PUT 而非 PATCH：语义是"替换整个 Agent 列表"，传空数组表示移除所有 Agent。
 */
export function updateConversationAgents(id: string, data: UpdateAgentsRequest) {
  return apiClient.put<UpdateAgentsResponse>(`/conversations/${id}/agents`, data)
}

/**
 * 获取会话历史消息（分页）。
 *
 * GET /conversations/{id}/messages?page=0&size=50
 *
 * 技术细节：
 *   - 页码从 0 开始，对齐 Spring Data JPA 的 Pageable 默认行为。
 *   - 消息按创建时间倒序（最新在前），符合聊天 UI 常见需求。
 */
export function getConversationMessages(id: string, page = 0, size = 50) {
  return apiClient.get<MessagePage>(`/conversations/${id}/messages`, {
    params: { page, size },
  })
}

/**
 * 置顶/取消置顶消息。
 *
 * PUT /messages/{id}/pin
 *
 * 技术细节：
 *   - 这是一个消息级别的操作，放在 conversation.ts 中是因为前端 ChatView 调用时
 *     通常在会话上下文内操作消息，放在一起减少 import 路径。
 *   - 函数名用 camelCase（TypeScript 惯例），路由参数用 URL path（REST 惯例）。
 */
export function pinMessage(messageId: string, pinned: boolean) {
  return apiClient.put<PinResponse>(`/messages/${messageId}/pin`, { pinned })
}

export interface ArtifactItem {
  id: string
  filename: string
  fileSize: number
  conversationId: string
  messageId: string
  createdAt: string
}

export interface ArtifactListResponse {
  artifacts: ArtifactItem[]
}

/** GET /conversations/{id}/artifacts */
export function getConversationArtifacts(conversationId: string) {
  return apiClient.get<ArtifactListResponse>(`/conversations/${conversationId}/artifacts`)
}
