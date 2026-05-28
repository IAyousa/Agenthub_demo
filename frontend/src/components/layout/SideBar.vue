<template>
  <div class="w-16 h-full bg-gradient-to-b from-[#1e1b4b] to-[#312e81] flex flex-col items-center py-6 space-y-6">
    <div class="w-9 h-9 bg-gradient-to-br from-[#6366f1] to-[#8b5cf6] rounded-xl mb-2 overflow-hidden shadow-lg shadow-indigo-500/20">
      <img src="https://api.dicebear.com/7.x/avataaars/svg?seed=Felix" alt="avatar" />
    </div>

    <div class="flex flex-col space-y-6 flex-1 text-[#a5b4fc]">
      <div
        @click="goChat"
        class="cursor-pointer hover:text-white transition-all duration-300 relative"
        :class="isChatActive ? 'text-white' : ''"
      >
        <div v-if="isChatActive" class="absolute left-0 top-1/2 -translate-y-1/2 w-1 h-6 bg-gradient-to-b from-[#6366f1] to-[#8b5cf6] rounded-r-full"></div>
        <MessageSquareIcon :size="22" />
      </div>
      <div
        @click="goOffice"
        class="cursor-pointer hover:text-white transition-all duration-300 relative"
        :class="isOfficeActive ? 'text-white' : ''"
      >
        <div v-if="isOfficeActive" class="absolute left-0 top-1/2 -translate-y-1/2 w-1 h-6 bg-gradient-to-b from-[#6366f1] to-[#8b5cf6] rounded-r-full"></div>
        <Building2Icon :size="22" />
      </div>
      <div class="cursor-pointer hover:text-white transition-all duration-300">
        <LayoutGridIcon :size="22" />
      </div>
    </div>

    <div class="flex flex-col space-y-6 text-[#a5b4fc] pb-4">
      <div class="cursor-pointer hover:text-white transition-all duration-300">
        <SettingsIcon :size="22" />
      </div>
    </div>
  </div>
</template>

<script setup lang="ts">
import { computed } from 'vue'
import { useRoute, useRouter } from 'vue-router'
import {
  MessageSquare as MessageSquareIcon,
  Building2 as Building2Icon,
  LayoutGrid as LayoutGridIcon,
  Settings as SettingsIcon
} from 'lucide-vue-next'

const route = useRoute()
const router = useRouter()

const isChatActive = computed(() => route.name === 'chat')
const isOfficeActive = computed(() => route.name === 'office')

const goChat = () => {
  router.push('/chat/conv_frontend_001')
}

const goOffice = () => {
  router.push('/office')
}
</script>
