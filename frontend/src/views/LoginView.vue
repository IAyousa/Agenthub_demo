<script setup lang="ts">
import { ref } from 'vue'
import { useRouter } from 'vue-router'
import { useAuthStore } from '../stores/auth'
import { useChatStore } from '../stores/chat'
import { destroyWsClient } from '../websocket/wsClient'

const router = useRouter()
const auth = useAuthStore()
const chat = useChatStore()

const isRegister = ref(false)
const username = ref('')
const password = ref('')
const localError = ref<string | null>(null)

async function handleSubmit() {
  localError.value = null
  if (!username.value.trim() || !password.value.trim()) {
    localError.value = '用户名和密码不能为空'
    return
  }
  if (password.value.length < 6) {
    localError.value = '密码长度至少 6 个字符'
    return
  }
  try {
    if (isRegister.value) {
      await auth.register(username.value.trim(), password.value)
    } else {
      await auth.login(username.value.trim(), password.value)
    }
    // 重新登录时重置 chat store 和 WebSocket，确保右侧聊天区刷新
    chat.resetState()
    destroyWsClient()
    router.push('/chat')
  } catch {
    // 后端返回的错误信息已存入 auth.error
    localError.value = auth.error || (isRegister.value ? '注册失败' : '登录失败')
  }
}

function toggleMode() {
  isRegister.value = !isRegister.value
  localError.value = null
  auth.clearError()
}
</script>

<template>
  <div class="h-screen w-screen flex items-center justify-center bg-gradient-to-br from-[#f8fafc] via-[#eef2ff] to-[#e0e7ff]">
    <!-- 登录卡片 -->
    <div class="w-full max-w-md mx-4">
      <!-- Logo + 标题 -->
      <div class="text-center mb-8">
        <div class="inline-flex w-14 h-14 bg-gradient-to-br from-[#6366f1] to-[#8b5cf6] rounded-2xl items-center justify-center shadow-lg shadow-indigo-500/25 mb-4">
          <svg class="w-7 h-7 text-white" fill="none" viewBox="0 0 24 24" stroke="currentColor" stroke-width="2">
            <path stroke-linecap="round" stroke-linejoin="round" d="M8 10h.01M12 10h.01M16 10h.01M9 16H5a2 2 0 01-2-2V6a2 2 0 012-2h14a2 2 0 012 2v8a2 2 0 01-2 2h-5l-5 5v-5z" />
          </svg>
        </div>
        <h1 class="text-2xl font-bold text-gray-900">AgentHub</h1>
        <p class="text-sm text-gray-500 mt-1">多 Agent 协作平台</p>
      </div>

      <!-- 卡片表单 -->
      <div class="bg-white rounded-2xl shadow-xl shadow-indigo-500/5 border border-gray-100 p-8">
        <h2 class="text-lg font-semibold text-gray-800 mb-6">
          {{ isRegister ? '创建账号' : '登录账号' }}
        </h2>

        <!-- 错误提示 -->
        <div
          v-if="localError"
          class="mb-4 px-4 py-2.5 bg-red-50 border border-red-200 rounded-lg text-sm text-red-600"
        >
          {{ localError }}
        </div>

        <form @submit.prevent="handleSubmit" class="space-y-4">
          <div>
            <label class="block text-sm font-medium text-gray-700 mb-1.5">用户名</label>
            <input
              v-model="username"
              type="text"
              autocomplete="username"
              placeholder="请输入用户名"
              class="w-full px-4 py-2.5 border border-gray-300 rounded-lg text-sm focus:outline-none focus:ring-2 focus:ring-indigo-500/20 focus:border-indigo-500 transition-all duration-200 bg-gray-50 hover:bg-white"
            />
          </div>
          <div>
            <label class="block text-sm font-medium text-gray-700 mb-1.5">密码</label>
            <input
              v-model="password"
              type="password"
              autocomplete="current-password"
              placeholder="请输入密码（至少6位）"
              class="w-full px-4 py-2.5 border border-gray-300 rounded-lg text-sm focus:outline-none focus:ring-2 focus:ring-indigo-500/20 focus:border-indigo-500 transition-all duration-200 bg-gray-50 hover:bg-white"
            />
          </div>

          <button
            type="submit"
            :disabled="auth.loading"
            class="w-full py-2.5 bg-gradient-to-r from-[#6366f1] to-[#8b5cf6] text-white rounded-lg font-medium text-sm hover:from-[#4f46e5] hover:to-[#7c3aed] transition-all duration-200 shadow-md shadow-indigo-500/20 disabled:opacity-60 disabled:cursor-not-allowed"
          >
            <span v-if="!auth.loading">{{ isRegister ? '注册' : '登录' }}</span>
            <span v-else class="inline-flex items-center gap-2">
              <svg class="animate-spin w-4 h-4" fill="none" viewBox="0 0 24 24">
                <circle class="opacity-25" cx="12" cy="12" r="10" stroke="currentColor" stroke-width="4" />
                <path class="opacity-75" fill="currentColor" d="M4 12a8 8 0 018-8V0C5.373 0 0 5.373 0 12h4z" />
              </svg>
              处理中...
            </span>
          </button>
        </form>

        <!-- 切换登录/注册 -->
        <p class="mt-6 text-center text-sm text-gray-500">
          {{ isRegister ? '已有账号？' : '没有账号？' }}
          <button
            @click="toggleMode"
            class="text-indigo-600 hover:text-indigo-700 font-medium transition-colors"
          >
            {{ isRegister ? '去登录' : '去注册' }}
          </button>
        </p>
      </div>
    </div>
  </div>
</template>

<style scoped>
/* 登录页独占全屏，不需要 SideBar */
</style>
