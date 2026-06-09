<template>
  <div class="w-16 h-full flex flex-col items-center py-6 space-y-6" :style="{ background: `linear-gradient(to bottom, var(--sidebar-start), var(--sidebar-end))` }">
    <div class="w-9 h-9 rounded-xl mb-2 overflow-hidden shadow-lg" :style="{ background: `linear-gradient(to bottom right, var(--accent-start), var(--accent-end))`, boxShadow: `0 4px 6px -1px color-mix(in srgb, var(--accent-start) 20%, transparent)` }">
      <img src="https://api.dicebear.com/7.x/avataaars/svg?seed=Felix" alt="avatar" />
    </div>

    <div class="flex flex-col space-y-6 flex-1" :style="{ color: `color-mix(in srgb, var(--accent-start) 60%, white)` }">
      <div
        @click="goChat"
        class="cursor-pointer hover:text-white transition-all duration-300 relative"
        :class="isChatActive ? 'text-white' : ''"
      >
        <div v-if="isChatActive" class="absolute left-0 top-1/2 -translate-y-1/2 w-1 h-6 rounded-r-full" :style="{ background: `linear-gradient(to bottom, var(--accent-start), var(--accent-end))` }"></div>
        <MessageSquareIcon :size="22" />
      </div>
      <div
        @click="goOffice"
        class="cursor-pointer hover:text-white transition-all duration-300 relative"
        :class="isOfficeActive ? 'text-white' : ''"
      >
        <div v-if="isOfficeActive" class="absolute left-0 top-1/2 -translate-y-1/2 w-1 h-6 rounded-r-full" :style="{ background: `linear-gradient(to bottom, var(--accent-start), var(--accent-end))` }"></div>
        <Building2Icon :size="22" />
      </div>
      <div class="cursor-pointer hover:text-white transition-all duration-300">
        <LayoutGridIcon :size="22" />
      </div>
    </div>

    <div class="flex flex-col space-y-6 pb-4" :style="{ color: `color-mix(in srgb, var(--accent-start) 60%, white)` }">
      <div
        @click="showSettings = true"
        class="cursor-pointer hover:text-white transition-all duration-300"
      >
        <SettingsIcon :size="22" />
      </div>
      <div
        @click="handleLogout"
        class="cursor-pointer hover:text-white transition-all duration-300"
        title="登出"
      >
        <LogOutIcon :size="22" />
      </div>
    </div>

    <ThemeSettingsModal
      :is-open="showSettings"
      @close="showSettings = false"
    />
  </div>
</template>

<script setup lang="ts">
import { ref, computed } from 'vue'
import { useRoute, useRouter } from 'vue-router'
import {
  MessageSquare as MessageSquareIcon,
  Building2 as Building2Icon,
  LayoutGrid as LayoutGridIcon,
  Settings as SettingsIcon,
  LogOut as LogOutIcon
} from 'lucide-vue-next'
import { useAuthStore } from '../../stores/auth'
import ThemeSettingsModal from './ThemeSettingsModal.vue'
import { useChatStore } from '../../stores/chat'
import { destroyWsClient } from '../../websocket/wsClient'

const route = useRoute()
const router = useRouter()
const auth = useAuthStore()
const chat = useChatStore()

const showSettings = ref(false)

const isChatActive = computed(() => route.name === 'chat')
const isOfficeActive = computed(() => route.name === 'office')

const goChat = () => { router.push('/chat') }
const goOffice = () => { router.push('/office') }

const handleLogout = async () => {
  await auth.logout()
  chat.resetState()
  destroyWsClient()
  router.push('/login')
}
</script>
