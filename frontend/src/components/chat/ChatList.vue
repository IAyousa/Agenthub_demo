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
  <div class="w-64 h-full bg-[#e6e5e4] border-r border-[#d6d6d6] flex flex-col">
    <!-- Search Bar -->
    <div class="p-3">
      <div class="bg-[#dbd9d8] rounded-sm flex items-center px-2 py-1">
        <SearchIcon :size="14" class="text-gray-500 mr-2" />
        <input 
          type="text" 
          placeholder="搜索" 
          class="bg-transparent border-none outline-none text-xs w-full"
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
          'flex items-center px-3 py-3 cursor-pointer hover:bg-[#d1cfce] transition-colors',
          currentConversationId === item.id ? 'bg-[#c7c6c5]' : ''
        ]"
      >
        <div class="w-10 h-10 rounded-sm bg-gray-300 mr-3 overflow-hidden">
          <img :src="item.avatar" :alt="item.name" />
        </div>
        <div class="flex-1 min-w-0">
          <div class="flex justify-between items-baseline">
            <h3 class="text-sm font-normal text-gray-900 truncate">{{ item.name }}</h3>
            <span class="text-[10px] text-gray-500">{{ item.time }}</span>
          </div>
          <p class="text-xs text-gray-500 truncate mt-0.5">{{ item.lastMsg }}</p>
        </div>
      </div>
    </div>
  </div>
</template>
