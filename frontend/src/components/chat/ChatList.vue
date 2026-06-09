<script setup lang="ts">
import { ref, computed } from 'vue'
import { useRouter } from 'vue-router'
import { Search as SearchIcon, Plus as PlusIcon, X as XIcon } from 'lucide-vue-next'
import { useChatStore } from '../../stores/chat'
import { storeToRefs } from 'pinia'
import CreateConversationModal from './CreateConversationModal.vue'

const chatStore = useChatStore()
const router = useRouter()
const { currentConversationId, conversationList } = storeToRefs(chatStore)

const showCreateModal = ref(false)

// ---- 搜索 ----
const searchQuery = ref('')

/** 根据搜索词过滤会话列表，匹配标题和 Agent 名称（大小写不敏感） */
const filteredList = computed(() => {
  const q = searchQuery.value.trim().toLowerCase()
  if (!q) return conversationList.value

  return conversationList.value.filter(item => {
    if (item.title.toLowerCase().includes(q)) return true
    if (item.agentNames.some(name => name.toLowerCase().includes(q))) return true
    return false
  })
})

const handleSelect = (id: string) => {
  router.push('/chat/' + id)
}

const handleDelete = (id: string) => {
  chatStore.deleteConversation(id)
}

const handleCreateConfirm = async (data: { title: string; type: string; agentIds: string[] }) => {
  const id = await chatStore.createConversation(data.title, data.type, data.agentIds)
  router.push('/chat/' + id)
  showCreateModal.value = false
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
      <div class="flex-1 bg-white border border-[#e2e8f0] rounded-xl flex items-center px-3 py-2 shadow-sm">
        <SearchIcon :size="14" class="text-indigo-400 mr-2 flex-shrink-0" />
        <input v-model="searchQuery" type="text" placeholder="搜索会话"
          class="bg-transparent border-none outline-none text-xs w-full text-gray-700 placeholder:text-gray-400" />
        <button v-if="searchQuery" @click="searchQuery = ''"
          class="flex-shrink-0 ml-1 text-gray-400 hover:text-gray-600 transition-colors" title="清除搜索">
          <XIcon :size="12" />
        </button>
      </div>
      <button @click="showCreateModal = true"
        class="w-8 h-8 bg-gradient-to-r from-indigo-500 to-purple-600 rounded-xl flex items-center justify-center text-white shadow-md hover:shadow-lg transition-all hover:scale-105 flex-shrink-0"
        title="新建会话">
        <PlusIcon :size="16" />
      </button>
    </div>

    <div class="flex-1 overflow-y-auto">
      <div
        v-for="item in filteredList"
        :key="item.id"
        @click="handleSelect(item.id)"
        :class="[
          'flex items-center px-3 py-3 cursor-pointer transition-all duration-200 mx-2 my-1 rounded-xl group relative',
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
        <button
          @click.stop="handleDelete(item.id)"
          class="absolute right-2 top-2 w-6 h-6 rounded-full bg-red-50 hover:bg-red-100 text-red-400 hover:text-red-600 flex items-center justify-center opacity-0 group-hover:opacity-100 transition-all"
          title="删除会话"
        >
          <XIcon :size="12" />
        </button>
      </div>
    </div>

    <CreateConversationModal
      :is-open="showCreateModal"
      @close="showCreateModal = false"
      @create="handleCreateConfirm"
    />
  </div>
</template>
