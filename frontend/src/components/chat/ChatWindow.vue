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
        <MoreHorizontalIcon :size="20" class="cursor-pointer hover:text-indigo-700 transition-colors" />
      </div>
    </header>

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
  ChevronLeft as ChevronLeftIcon
} from 'lucide-vue-next'

const chatStore = useChatStore()
const { currentMessages, currentTitle, isLoading } = storeToRefs(chatStore)
const scrollContainer = ref<HTMLElement | null>(null)

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
})

onMounted(() => {
  scrollToBottom()
})

const handleSend = (content: string) => {
  chatStore.addMessage({
    id: Date.now().toString(),
    role: 'user',
    type: 'text',
    content: content,
    created_at: new Date().toISOString()
  })
  
  simulateResponse(content)
}

const simulateResponse = (query: string) => {
  chatStore.isLoading = true
  
  setTimeout(() => {
    const q = query.toLowerCase()
    
    if (q.includes('counter')) {
      chatStore.addMessage({
        id: Date.now().toString(),
        role: 'assistant',
        type: 'artifact_preview',
        content: `<!DOCTYPE html>
<html>
<head>
  <style>
    body { font-family: sans-serif; display: flex; justify-content: center; align-items: center; height: 100vh; margin: 0; background: #f0f2f5; }
    .card { background: white; padding: 2rem; border-radius: 12px; shadow: 0 4px 6px rgba(0,0,0,0.1); text-align: center; }
    .count { font-size: 3rem; font-weight: bold; color: #6366f1; margin: 1rem 0; }
    button { padding: 0.5rem 1rem; font-size: 1rem; border: none; border-radius: 6px; background: linear-gradient(135deg, #6366f1, #8b5cf6); color: white; cursor: pointer; transition: opacity 0.2s; }
    button:hover { opacity: 0.8; }
  </style>
<\/head>
<body>
  <div class="card">
    <h2>Interactive Counter</h2>
    <div class="count" id="counter">0</div>
    <button onclick="document.getElementById('counter').innerText = parseInt(document.getElementById('counter').innerText) + 1">Increment</button>
  </div>
<\/body>
<\/html>`,
        metadata: { title: 'Interactive Counter', language: 'html' },
        created_at: new Date().toISOString()
      })
    } else if (q.includes('animation') || q.includes('css')) {
      chatStore.addMessage({
        id: Date.now().toString(),
        role: 'assistant',
        type: 'artifact_preview',
        content: `<!DOCTYPE html>
<html>
<head>
  <style>
    body { display: flex; justify-content: center; align-items: center; height: 100vh; margin: 0; background: #1a1a1a; overflow: hidden; }
    .loader { width: 100px; height: 100px; position: relative; }
    .circle { width: 100%; height: 100%; border: 4px solid transparent; border-top-color: #6366f1; border-radius: 50%; position: absolute; animation: spin 1s linear infinite; }
    .circle:nth-child(2) { width: 80%; height: 80%; top: 10%; left: 10%; border-top-color: #8b5cf6; animation: spin 2s linear infinite; }
    .circle:nth-child(3) { width: 60%; height: 60%; top: 20%; left: 20%; border-top-color: #a855f7; animation: spin 3s linear infinite; }
    @keyframes spin { 0% { transform: rotate(0deg); } 100% { transform: rotate(360deg); } }
  </style>
<\/head>
<body>
  <div class="loader">
    <div class="circle"><\/div>
    <div class="circle"><\/div>
    <div class="circle"><\/div>
  </div>
<\/body>
<\/html>`,
        metadata: { title: 'CSS Magic Animation', language: 'html' },
        created_at: new Date().toISOString()
      })
    } else if (q.includes('dashboard') || q.includes('chart')) {
      chatStore.addMessage({
        id: Date.now().toString(),
        role: 'assistant',
        type: 'artifact_preview',
        content: `<!DOCTYPE html>
<html>
<head>
  <script src="https://cdn.jsdelivr.net/npm/chart.js"><\/script>
  <style>
    body { font-family: sans-serif; padding: 20px; background: #f8f9fa; }
    .container { max-width: 600px; margin: auto; background: white; padding: 20px; border-radius: 8px; box-shadow: 0 2px 10px rgba(0,0,0,0.05); }
    h2 { color: #333; margin-top: 0; }
  </style>
<\/head>
<body>
  <div class="container">
    <h2>Project Progress</h2>
    <canvas id="myChart"><\/canvas>
  </div>
  <script>
    const ctx = document.getElementById('myChart');
    new Chart(ctx, {
      type: 'bar',
      data: {
        labels: ['Task A', 'Task B', 'Task C', 'Task D', 'Task E'],
        datasets: [{
          label: 'Completion %',
          data: [85, 45, 100, 30, 60],
          backgroundColor: '#6366f1'
        }]
      },
      options: { scales: { y: { beginAtZero: true, max: 100 } } }
    });
  <\/script>
<\/body>
<\/html>`,
        metadata: { title: 'Data Dashboard', language: 'html' },
        created_at: new Date().toISOString()
      })
    } else if (q.includes('code')) {
      chatStore.addMessage({
        id: (Date.now() + 1).toString(),
        role: 'assistant',
        type: 'code',
        content: `function helloWorld() {\n  console.log("Hello from Modern Tech Agent Platform!");\n}`,
        metadata: { language: 'javascript' },
        created_at: new Date().toISOString()
      })
    } else if (query.toLowerCase().includes('preview') || query.toLowerCase().includes('artifact')) {
      chatStore.addMessage({
        id: (Date.now() + 1).toString(),
        role: 'assistant',
        type: 'artifact_preview',
        content: '<html><body><h1>Artifact Preview<\/h1><\/body><\/html>',
        metadata: { title: 'Dashboard Prototype', language: 'html' },
        created_at: new Date().toISOString()
      })
    } else {
      chatStore.addMessage({
        id: (Date.now() + 1).toString(),
        role: 'assistant',
        type: 'text',
        content: '我是你的多 Agent 调度器。我可以帮你编写代码或生成预览。试着输入 "some code" 或 "preview" 看看效果。',
        created_at: new Date().toISOString()
      })
    }
    chatStore.isLoading = false
  }, 1000)
}
</script>
