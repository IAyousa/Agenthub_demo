/**
 * Auth Store — JWT 认证状态管理（Pinia）
 *
 * 职责：
 *   - 管理 token / userId / username 状态
 *   - 登录、注册、登出操作
 *   - token 持久化到 localStorage，刷新不丢失
 *
 * 使用方式：
 *   import { useAuthStore } from '@/stores/auth'
 *   const auth = useAuthStore()
 *   await auth.login('username', 'password')
 */

import { defineStore } from 'pinia'
import { ref, computed } from 'vue'
import { login as apiLogin, register as apiRegister, logout as apiLogout } from '../api/auth'

// localStorage key
const TOKEN_KEY = 'agenthub_token'
const USER_KEY = 'agenthub_user'

// 从 localStorage 恢复登录态
function loadStoredToken(): string | null {
  return localStorage.getItem(TOKEN_KEY)
}

function loadStoredUser(): { userId: string; username: string } | null {
  const raw = localStorage.getItem(USER_KEY)
  if (raw) {
    try {
      return JSON.parse(raw)
    } catch {
      return null
    }
  }
  return null
}

export const useAuthStore = defineStore('auth', () => {
  // ==========================================================================
  // State
  // ==========================================================================
  const storedUser = loadStoredUser()
  const token = ref<string | null>(loadStoredToken())
  const userId = ref<string | null>(storedUser?.userId ?? null)
  const username = ref<string | null>(storedUser?.username ?? null)
  const loading = ref(false)
  const error = ref<string | null>(null)

  // ==========================================================================
  // Getters
  // ==========================================================================
  const isAuthenticated = computed(() => !!token.value)

  // ==========================================================================
  // Actions
  // ==========================================================================

  /** 登录 — 调用 POST /auth/login，成功后将 token 持久化 */
  async function login(name: string, password: string) {
    loading.value = true
    error.value = null
    try {
      const res = await apiLogin({ username: name, password })
      const { token: t, userId: uid, username: uname } = res.data
      token.value = t
      userId.value = uid
      username.value = uname
      localStorage.setItem(TOKEN_KEY, t)
      localStorage.setItem(USER_KEY, JSON.stringify({ userId: uid, username: uname }))
    } catch (e: any) {
      const msg = e?.response?.data?.message || e?.message || '登录失败'
      error.value = msg
      throw e
    } finally {
      loading.value = false
    }
  }

  /** 注册 — 调用 POST /auth/register，成功后自动登录 */
  async function register(name: string, password: string) {
    loading.value = true
    error.value = null
    try {
      const res = await apiRegister({ username: name, password })
      const { token: t, userId: uid, username: uname } = res.data
      token.value = t
      userId.value = uid
      username.value = uname
      localStorage.setItem(TOKEN_KEY, t)
      localStorage.setItem(USER_KEY, JSON.stringify({ userId: uid, username: uname }))
    } catch (e: any) {
      const msg = e?.response?.data?.message || e?.message || '注册失败'
      error.value = msg
      throw e
    } finally {
      loading.value = false
    }
  }

  /** 登出 — 调用后端接口 + 清除本地状态 */
  async function logout() {
    try {
      await apiLogout()
    } catch {
      // 后端 /auth/logout 尚未实现时静默忽略 404
    }
    token.value = null
    userId.value = null
    username.value = null
    localStorage.removeItem(TOKEN_KEY)
    localStorage.removeItem(USER_KEY)
    error.value = null
  }

  /** 清除错误信息（切换登录/注册模式时调用） */
  function clearError() {
    error.value = null
  }

  return {
    token,
    userId,
    username,
    loading,
    error,
    isAuthenticated,
    login,
    register,
    logout,
    clearError,
  }
})
