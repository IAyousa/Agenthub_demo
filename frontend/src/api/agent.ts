/**
 * Agent API — Agent 管理接口封装
 *
 * 对照 API 契约文档 v1.0 第 2.3 节（Agent 管理）。
 * 所有请求/响应字段使用 camelCase，与后端 Spring Boot DTO 对齐。
 *
 * 技术栈说明：
 *   - 复用 C1 配置的 axios 实例（apiClient），统一的 baseURL + 超时 + 拦截器。
 *   - 与 C2 conversation.ts 采用相同的 TypeScript 泛型模式：`apiClient.get<T>()`。
 *   - 内置 Agent（Claude Code、Codex）通过 data.sql 种子数据预置，isBuiltin=true。
 *   - 自定义 Agent 通过 POST /agents 创建，isBuiltin=false。
 */

import apiClient from './index'

// ============================================================================
// TypeScript 接口 — API 层数据形状
// ============================================================================

/** 可用 Agent 列表项（GET /agents 响应中单个元素） */
export interface AgentListItem {
  id: string
  name: string
  type: 'claude_code' | 'codex' | 'custom'
  avatarUrl: string
  capabilities: string[]
  isBuiltin: boolean
}

/** 创建自定义 Agent 的请求体（POST /agents） */
export interface CreateAgentRequest {
  name: string
  type: string
  systemPrompt: string
  capabilities: string[]
}

/** 创建自定义 Agent 的响应体 */
export interface CreateAgentResponse {
  id: string
  name: string
  type: string
  systemPrompt: string
  capabilities: string[]
  createdAt: string
}

/** Agent 详情（GET /agents/{id} 响应，含 systemPrompt） */
export interface AgentDetail {
  id: string
  name: string
  type: 'claude_code' | 'codex' | 'custom'
  avatarUrl: string
  systemPrompt: string
  capabilities: string[]
  isBuiltin: boolean
  createdAt: string
}

// ============================================================================
// API 函数
// ============================================================================

/**
 * 获取可用 Agent 列表。
 *
 * GET /agents
 *
 * 响应包含内置 Agent（Claude Code、Codex，由 data.sql 预置）和用户创建的自定义 Agent。
 * `isBuiltin` 字段用于前端区分内置与自定义 Agent（内置不可编辑/删除）。
 */
export function getAgents() {
  return apiClient.get<{ agents: AgentListItem[] }>('/agents')
}

/**
 * 创建自定义 Agent。
 *
 * POST /agents
 *
 * 技术细节：
 *   - `systemPrompt` 是 Agent 的系统提示词，会覆盖适配器默认值。
 *   - `capabilities` 是 JSON 数组（如 ["React 开发", "组件设计"]），存储为 agents 表的 TEXT 字段。
 *   - 内置 Agent（isBuiltin=true）的 systemPrompt 通常由 data.sql 或 prompts/ 模块提供默认值。
 */
export function createAgent(data: CreateAgentRequest) {
  return apiClient.post<CreateAgentResponse>('/agents', data)
}

/**
 * 获取单个 Agent 的详细信息（含 systemPrompt）。
 *
 * GET /agents/{id}
 *
 * 与列表接口不同，此接口返回完整的 systemPrompt 文本，用于 Agent 编辑页面。
 */
export function getAgentDetail(id: string) {
  return apiClient.get<AgentDetail>(`/agents/${id}`)
}
