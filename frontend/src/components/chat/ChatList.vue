<script setup lang="ts">
import { Search as SearchIcon } from 'lucide-vue-next'
import { useChatStore } from '../../stores/chat'
import { storeToRefs } from 'pinia'

const chatStore = useChatStore()
const { currentConversationId } = storeToRefs(chatStore)

const mockChats = [
  {
    id: 'orchestrator',
    name: 'Orchestrator Agent',
    lastMsg: 'Hello! I am your Multi-Agent Orchestrator.',
    time: '16:40',
    avatar: 'https://api.dicebear.com/7.x/bottts/svg?seed=orchestrator'
  },
  {
    id: 'coder',
    name: '代码助手 (Coder)',
    lastMsg: '好的，我已经写好了 React 组件。',
    time: '15:20',
    avatar: 'https://api.dicebear.com/7.x/bottts/svg?seed=coder'
  },
  {
    id: 'designer',
    name: '设计专家 (Designer)',
    lastMsg: '这里的配色可以再优化一下。',
    time: '昨天',
    avatar: 'https://api.dicebear.com/7.x/bottts/svg?seed=designer'
  }
]

const handleSelect = (id: string) => {
  chatStore.selectConversation(id)
  chatStore.mobileView = 'chat'
}
</script>

<template>
  <div class="w-64 h-full bg-gradient-to-b from-[#f8fafc] to-[#f1f5f9] border-r border-[#e2e8f0] flex flex-col">
    <!-- Search Bar -->
    <div class="p-3">
      <div class="bg-white border border-[#e2e8f0] rounded-xl flex items-center px-3 py-2 shadow-sm">
        <SearchIcon :size="14" class="text-indigo-400 mr-2" />
        <input 
          type="text" 
          placeholder="搜索会话" 
          class="bg-transparent border-none outline-none text-xs w-full text-gray-700 placeholder:text-gray-400"
        />
      </div>
    </div>

    <!-- Chat List -->
    <div class="flex-1 overflow-y-auto">
      <div 
        v-for="item in mockChats" 
        :key="item.id"
        @click="handleSelect(item.id)"
        :class="[
          'flex items-center px-3 py-3 cursor-pointer transition-all duration-200 mx-2 my-1 rounded-xl',
          currentConversationId === item.id ? 'bg-gradient-to-r from-[#eef2ff] to-[#e0e7ff] border border-[#c7d2fe] shadow-sm' : 'hover:bg-white hover:shadow-sm'
        ]"
      >
        <div class="w-10 h-10 rounded-xl bg-gradient-to-br from-indigo-400 to-purple-500 mr-3 overflow-hidden shadow-md">
          <img :src="item.avatar" :alt="item.name" />
        </div>
        <div class="flex-1 min-w-0">
          <div class="flex justify-between items-baseline">
            <h3 class="text-sm font-semibold text-gray-800 truncate">{{ item.name }}</h3>
            <span class="text-[10px] text-gray-400">{{ item.time }}</span>
          </div>
          <p class="text-xs text-gray-500 truncate mt-0.5">{{ item.lastMsg }}</p>
        </div>
      </div>
    </div>
  </div>
</template>
