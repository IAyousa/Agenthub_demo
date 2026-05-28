<script setup lang="ts">
import { ref } from 'vue'
import { Search as SearchIcon, Plus as PlusIcon, X as XIcon } from 'lucide-vue-next'
import { useChatStore } from '../../stores/chat'
import { storeToRefs } from 'pinia'

const chatStore = useChatStore()
const { currentConversationId, conversationList } = storeToRefs(chatStore)

const showCreateInput = ref(false)
const createTitle = ref('')

const handleSelect = (id: string) => {
  chatStore.selectConversation(id)
  chatStore.mobileView = 'chat'
}

const handleCreateClick = () => {
  showCreateInput.value = true
  createTitle.value = ''
}

const confirmCreate = () => {
  const title = createTitle.value.trim()
  if (title) {
    chatStore.createConversation(title)
  }
  showCreateInput.value = false
}

const cancelCreate = () => {
  showCreateInput.value = false
}

const formatTime = (iso: string) => {
  const date = new Date(iso)
  const now = new Date()
  const diffMs = now.getTime() - date.getTime()
  const diffMin = Math.floor(diffMs / 60000)
  const diffHour = Math.floor(diffMs / 3600000)
  const diffDay = Math.floor(diffMs / 86400000)
  if (diffMin < 1) return '刚刚'
  if (diffMin < 60) return `${diffMin}分钟前`
  if (diffHour < 24) return `${diffHour}小时前`
  if (diffDay < 7) return `${diffDay}天前`
  return date.toLocaleDateString('zh-CN', { month: 'short', day: 'numeric' })
}
</script>

<template>
  <div class="w-64 h-full bg-gradient-to-b from-[#f8fafc] to-[#f1f5f9] border-r border-[#e2e8f0] flex flex-col">
    <div class="p-3 flex items-center gap-2">
      <template v-if="showCreateInput">
        <div class="flex-1 bg-white border-2 border-indigo-400 rounded-xl flex items-center px-3 py-2 shadow-sm">
          <input
            v-model="createTitle"
            type="text"
            placeholder="输入会话名称"
            class="bg-transparent border-none outline-none text-xs w-full text-gray-700 placeholder:text-gray-400"
            @keydown.enter="confirmCreate"
            @keydown.escape="cancelCreate"
          />
        </div>
        <button
          @click="confirmCreate"
          :disabled="!createTitle.trim()"
          class="w-8 h-8 bg-gradient-to-r from-indigo-500 to-purple-600 rounded-xl flex items-center justify-center text-white shadow-md hover:shadow-lg transition-all flex-shrink-0 disabled:opacity-40 disabled:cursor-not-allowed"
          title="确认"
        >
          <PlusIcon :size="16" />
        </button>
        <button
          @click="cancelCreate"
          class="w-8 h-8 bg-gray-100 rounded-xl flex items-center justify-center text-gray-400 hover:text-gray-600 hover:bg-gray-200 transition-all flex-shrink-0"
          title="取消"
        >
          <XIcon :size="14" />
        </button>
      </template>
      <template v-else>
        <div class="flex-1 bg-white border border-[#e2e8f0] rounded-xl flex items-center px-3 py-2 shadow-sm">
          <SearchIcon :size="14" class="text-indigo-400 mr-2" />
          <input
            type="text"
            placeholder="搜索会话"
            class="bg-transparent border-none outline-none text-xs w-full text-gray-700 placeholder:text-gray-400"
          />
        </div>
        <button
          @click="handleCreateClick"
          class="w-8 h-8 bg-gradient-to-r from-indigo-500 to-purple-600 rounded-xl flex items-center justify-center text-white shadow-md hover:shadow-lg transition-all hover:scale-105 flex-shrink-0"
          title="新建会话"
        >
          <PlusIcon :size="16" />
        </button>
      </template>
    </div>

    <div class="flex-1 overflow-y-auto">
      <div
        v-for="item in conversationList"
        :key="item.id"
        @click="handleSelect(item.id)"
        :class="[
          'flex items-center px-3 py-3 cursor-pointer transition-all duration-200 mx-2 my-1 rounded-xl',
          currentConversationId === item.id ? 'bg-gradient-to-r from-[#eef2ff] to-[#e0e7ff] border border-[#c7d2fe] shadow-sm' : 'hover:bg-white hover:shadow-sm'
        ]"
      >
        <div class="w-10 h-10 rounded-xl bg-gradient-to-br from-indigo-400 to-purple-500 mr-3 flex items-center justify-center shadow-md flex-shrink-0">
          <span class="text-white text-sm font-bold">{{ item.title.charAt(0) }}</span>
        </div>
        <div class="flex-1 min-w-0">
          <div class="flex justify-between items-baseline">
            <h3 class="text-sm font-semibold text-gray-800 truncate">{{ item.title }}</h3>
            <span class="text-[10px] text-gray-400 flex-shrink-0 ml-1">{{ formatTime(item.updatedAt) }}</span>
          </div>
          <div class="flex items-center gap-1 mt-0.5" v-if="item.agentNames.length > 0">
            <span
              v-for="name in item.agentNames.slice(0, 2)"
              :key="name"
              class="text-[9px] text-indigo-400 bg-indigo-50 px-1.5 py-0.5 rounded-full truncate max-w-[80px]"
            >{{ name }}</span>
            <span v-if="item.agentNames.length > 2" class="text-[9px] text-gray-400">+{{ item.agentNames.length - 2 }}</span>
          </div>
          <p class="text-xs text-gray-500 truncate mt-0.5">{{ item.lastMessage }}</p>
        </div>
      </div>
    </div>
  </div>
</template>
