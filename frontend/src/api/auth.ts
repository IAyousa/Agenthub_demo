/**
 * Auth API — JWT 认证接口封装
 *
 * 对齐 API 契约文档 v1.1 第 2.3 节（JWT 认证）。
 * 后端 SecurityConfig: /auth/** permitAll，无需预先携带 Token。
 */

import apiClient from './index'

// ============================================================================
// TypeScript 接口
// ============================================================================

/** 登录/注册请求体（POST /auth/login + /auth/register） */
export interface AuthRequest {
  username: string
  password: string
}

/** 登录/注册成功响应 */
export interface AuthResponse {
  token: string
  userId: string
  username: string
}

// ============================================================================
// API 函数
// ============================================================================

/** 用户注册 — POST /auth/register */
export function register(data: AuthRequest) {
  return apiClient.post<AuthResponse>('/auth/register', data)
}

/** 用户登录 — POST /auth/login */
export function login(data: AuthRequest) {
  return apiClient.post<AuthResponse>('/auth/login', data)
}

/** 用户登出 — POST /auth/logout（后端 P2 Redis Token 黑名单，当前占位） */
export function logout() {
  return apiClient.post('/auth/logout')
}
