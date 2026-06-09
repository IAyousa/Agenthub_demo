<template>
  <div class="flex flex-col h-full overflow-hidden" :style="{ background: `linear-gradient(to bottom right, color-mix(in srgb, var(--accent-light) 50%, #f8fafc), var(--accent-light))` }">
    <!-- Header -->
    <header class="h-[60px] bg-white/80 backdrop-blur-md border-b px-3 md:px-5 flex items-center justify-between shrink-0" :style="{ borderColor: `color-mix(in srgb, var(--accent-start) 15%, #e2e8f0)` }">
      <div class="flex items-center gap-2">
        <!-- Mobile Back Button -->
        <button 
          @click="chatStore.mobileView = 'list'"
          class="md:hidden p-1 hover:bg-white/50 rounded-full transition-colors"
        >
          <ChevronLeftIcon :size="24" :style="{ color: `color-mix(in srgb, var(--accent-start) 80%, #475569)` }" />
        </button>
        
        <div class="flex flex-col">
          <h1 class="text-[16px] font-semibold text-gray-800">{{ currentTitle }}</h1>
        </div>
      </div>
    </header>

    <!-- Floating Error Toast -->
    <Transition name="toast">
      <div
        v-if="toastMessage"
        class="absolute top-4 left-1/2 -translate-x-1/2 z-50 flex items-center gap-3 px-5 py-3 bg-white/95 backdrop-blur-sm border border-red-200 rounded-2xl shadow-lg text-sm text-red-600"
      >
        <span class="w-2 h-2 rounded-full bg-red-500 animate-pulse shrink-0"></span>
        <span>{{ toastMessage }}</span>
        <button @click="dismissToast" class="text-red-300 hover:text-red-500 transition-colors ml-1">
          <XIcon :size="14" />
        </button>
      </div>
    </Transition>

    <!-- Empty state: no conversation selected -->
    <main v-if="!chatStore.currentConversationId" class="flex-1 flex items-center justify-center bg-transparent">
      <div class="text-center">
        <div class="w-20 h-20 mx-auto mb-5 rounded-2xl flex items-center justify-center" :style="{ background: `linear-gradient(to bottom right, color-mix(in srgb, var(--accent-start) 25%, white), color-mix(in srgb, var(--accent-end) 25%, white))` }">
          <svg class="w-10 h-10" fill="none" viewBox="0 0 24 24" stroke="currentColor" stroke-width="1.5" :style="{ color: `color-mix(in srgb, var(--accent-start) 50%, #94a3b8)` }">
            <path stroke-linecap="round" stroke-linejoin="round" d="M12 20.25c4.97 0 9-3.694 9-8.25s-4.03-8.25-9-8.25S3 7.444 3 12c0 2.104.859 4.023 2.273 5.48.432.447.74 1.04.586 1.641a4.483 4.483 0 01-.923 1.785A5.969 5.969 0 006 21c1.282 0 2.47-.402 3.445-1.087.81.22 1.668.337 2.555.337z" />
          </svg>
        </div>
        <h2 class="text-lg font-semibold text-gray-600 mb-2">选择一个会话开始聊天</h2>
        <p class="text-sm text-gray-400">点击左侧 + 按钮创建新会话，或选择一个已有会话</p>
      </div>
    </main>

    <!-- Messages -->
    <template v-else>
    <main ref="scrollContainer" class="flex-1 overflow-y-auto py-5 bg-transparent scroll-smooth">
      <div class="max-w-6xl mx-auto px-4 md:px-10">
        <ChatMessage
          v-for="msg in currentMessages"
          :key="msg.id"
          :id="msg.id"
          :role="msg.role"
          :type="msg.type"
          :content="msg.content"
          :metadata="msg.metadata"
        />
        <div v-if="isLoading" class="flex justify-start px-4 mb-4">
          <div class="bg-white rounded-xl px-4 py-3 shadow-lg text-xs italic" :style="{ color: `color-mix(in srgb, var(--accent-start) 70%, #64748b)`, borderColor: `color-mix(in srgb, var(--accent-start) 15%, #e2e8f0)`, borderWidth: '1px', borderStyle: 'solid' }">
            <div class="flex items-center gap-2">
              <div class="w-2 h-2 rounded-full animate-bounce" style="animation-delay: 0ms" :style="{ background: `linear-gradient(to right, var(--accent-start), var(--accent-end))` }"></div>
              <div class="w-2 h-2 rounded-full animate-bounce" style="animation-delay: 150ms" :style="{ background: `linear-gradient(to right, var(--accent-start), var(--accent-end))` }"></div>
              <div class="w-2 h-2 rounded-full animate-bounce" style="animation-delay: 300ms" :style="{ background: `linear-gradient(to right, var(--accent-start), var(--accent-end))` }"></div>
              <span class="ml-1">Agent 正在思考...</span>
            </div>
          </div>
        </div>
      </div>
    </main>

    <MessageInput
      :key="chatStore.currentConversationId"
      :disabled="isLoading"
      placeholder="输入消息..."
      @send="handleSend"
    />
    </template>
  </div>
</template>

<script setup lang="ts">
import { ref, onMounted, watch, nextTick } from 'vue'
import { storeToRefs } from 'pinia'
import { useChatStore } from '../../stores/chat'
import ChatMessage from './ChatMessage.vue'
import MessageInput from './MessageInput.vue'
import {
  ChevronLeft as ChevronLeftIcon,
  X as XIcon
} from 'lucide-vue-next'

const chatStore = useChatStore()
const { currentMessages, currentTitle, isLoading, selectedAgentId, error } = storeToRefs(chatStore)
const scrollContainer = ref<HTMLElement | null>(null)
const toastMessage = ref('')
let toastTimer: ReturnType<typeof setTimeout> | null = null

const dismissToast = () => {
  toastMessage.value = ''
  if (toastTimer) {
    clearTimeout(toastTimer)
    toastTimer = null
  }
}

// 监听 store 的 error 状态，自动弹出 toast
watch(error, (msg) => {
  if (msg) showToast(msg)
})

const showToast = (msg: string) => {
  dismissToast()
  toastMessage.value = msg
  toastTimer = setTimeout(() => {
    toastMessage.value = ''
  }, 4000)
}

const scrollToBottom = async () => {
  await nextTick()
  if (scrollContainer.value) {
    scrollContainer.value.scrollTop = scrollContainer.value.scrollHeight
  }
}

// Watch for message changes to scroll
watch(() => currentMessages.value.length, () => {
  scrollToBottom()
}, { deep: true })

// Watch for loading state to scroll when agent starts/stops thinking
watch(isLoading, (loading) => {
  if (loading) {
    scrollToBottom()
  }
})

// Watch for agent switch to scroll
watch(() => chatStore.currentConversationId, () => {
  scrollToBottom()
  dismissToast()
})

onMounted(() => {
  scrollToBottom()
})

const handleSend = (content: string) => {
  chatStore.sendMessage(content)
  if (!chatStore.wsConnected) {
    showToast('服务端连接出现问题，请稍后重试')
  }
}
</script>

<style scoped>
.toast-enter-active,
.toast-leave-active {
  transition: opacity 0.2s;
}
.toast-enter-from,
.toast-leave-to {
  opacity: 0;
}
</style>
