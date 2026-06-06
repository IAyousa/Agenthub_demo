<template>
  <div class="flex flex-col h-full bg-gradient-to-br from-[#f8fafc] to-[#f0f4ff] overflow-hidden">
    <!-- Header -->
    <header class="h-[60px] bg-white/80 backdrop-blur-md border-b border-indigo-100 px-3 md:px-5 flex items-center justify-between shrink-0">
      <div class="flex items-center gap-2">
        <!-- Mobile Back Button -->
        <button 
          @click="chatStore.mobileView = 'list'"
          class="md:hidden p-1 hover:bg-indigo-50 rounded-full transition-colors"
        >
          <ChevronLeftIcon :size="24" class="text-indigo-600" />
        </button>
        
        <div class="flex flex-col">
          <h1 class="text-[16px] font-semibold text-gray-800">{{ currentTitle }}</h1>
        </div>
      </div>
      <div class="flex items-center gap-4 text-indigo-500">
        <!-- Agent Selector -->
        <select
          v-model="selectedAgentId"
          class="text-xs bg-indigo-50 border border-indigo-200 rounded-lg px-2 py-1.5 text-indigo-700 cursor-pointer hover:bg-indigo-100 transition-colors outline-none"
        >
          <option v-for="a in chatStore.agents" :key="a.id" :value="a.id">
            {{ a.name }}
          </option>
        </select>
        <MoreHorizontalIcon :size="20" class="cursor-pointer hover:text-indigo-700 transition-colors" />
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

    <!-- Messages -->
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
          <div class="bg-white rounded-xl px-4 py-3 shadow-lg text-xs text-indigo-500 italic border border-indigo-100">
            <div class="flex items-center gap-2">
              <div class="w-2 h-2 rounded-full bg-gradient-to-r from-indigo-500 to-purple-500 animate-bounce" style="animation-delay: 0ms"></div>
              <div class="w-2 h-2 rounded-full bg-gradient-to-r from-indigo-500 to-purple-500 animate-bounce" style="animation-delay: 150ms"></div>
              <div class="w-2 h-2 rounded-full bg-gradient-to-r from-indigo-500 to-purple-500 animate-bounce" style="animation-delay: 300ms"></div>
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
  </div>
</template>

<script setup lang="ts">
import { ref, onMounted, watch, nextTick } from 'vue'
import { storeToRefs } from 'pinia'
import { useChatStore } from '../../stores/chat'
import ChatMessage from './ChatMessage.vue'
import MessageInput from './MessageInput.vue'
import {
  MoreHorizontal as MoreHorizontalIcon,
  ChevronLeft as ChevronLeftIcon,
  X as XIcon
} from 'lucide-vue-next'

const chatStore = useChatStore()
const { currentMessages, currentTitle, isLoading, selectedAgentId } = storeToRefs(chatStore)
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
