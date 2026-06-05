<script setup lang="ts">
import { watch, onMounted } from 'vue'
import { useRoute } from 'vue-router'
import ChatList from '../components/chat/ChatList.vue'
import ChatWindow from '../components/chat/ChatWindow.vue'
import ArtifactWindow from '../components/chat/ArtifactWindow.vue'
import { useChatStore } from '../stores/chat'

const route = useRoute()
const chatStore = useChatStore()

watch(
  () => route.params.conversationId,
  (id) => {
    if (id && typeof id === 'string') {
      chatStore.selectConversation(id)
    }
  },
  { immediate: true }
)

onMounted(() => {
  chatStore.mobileView = 'list'
  chatStore.loadConversationList()  // REST API: GET /conversations
  chatStore.loadAgents()            // REST API: GET /agents
  chatStore.initWebSocket()
})
</script>

<template>
  <div class="flex-1 flex overflow-hidden relative">
    <ChatList
      :class="[
        'flex-shrink-0 w-full md:w-64 border-r border-[#e2e8f0]',
        chatStore.mobileView === 'chat' ? 'hidden md:flex' : 'flex'
      ]"
    />

    <div
      :class="[
        'flex-1 h-full flex overflow-hidden relative',
        chatStore.mobileView === 'list' ? 'hidden md:flex' : 'flex'
      ]"
    >
      <div class="h-full w-full overflow-hidden">
        <ChatWindow class="w-full h-full" />
      </div>

      <Transition name="overlay">
        <div
          v-if="chatStore.isArtifactVisible && chatStore.currentArtifact"
          class="absolute inset-0 z-50 bg-white overflow-hidden shadow-2xl"
        >
          <ArtifactWindow
            :title="chatStore.currentArtifact.title"
            :code="chatStore.currentArtifact.code"
            :language="chatStore.currentArtifact.language"
            @close="chatStore.closeArtifact"
          />
        </div>
      </Transition>
    </div>
  </div>
</template>
