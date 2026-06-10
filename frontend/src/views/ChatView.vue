<script setup lang="ts">
import { watch, onMounted, onBeforeUnmount } from 'vue'
import { useRoute, useRouter, onBeforeRouteLeave } from 'vue-router'
import ChatList from '../components/chat/ChatList.vue'
import ChatWindow from '../components/chat/ChatWindow.vue'
import ArtifactWindow from '../components/chat/ArtifactWindow.vue'
import { useChatStore } from '../stores/chat'

const route = useRoute()
const router = useRouter()
const chatStore = useChatStore()

watch(
  () => route.params.conversationId,
  (id) => {
    if (id && typeof id === 'string') {
      chatStore.selectConversation(id)
    }
  }
  // 去掉 immediate:true — 改为 onMounted 中先加载列表再选择
)

// ===================================================================
// 流式进行中阻止刷新/关闭/导航离开
// ===================================================================
function handleBeforeUnload(e: BeforeUnloadEvent) {
  if (chatStore.isLoading) {
    e.preventDefault()
  }
}

// Vue Router 内部导航也阻止（点击侧边栏/会话列表等）
onBeforeRouteLeave((_to, _from) => {
  if (chatStore.isLoading) {
    return window.confirm('Agent 正在生成回复，确定要离开当前会话吗？')
  }
  return true
})

onMounted(async () => {
  // 流式进行中阻止刷新/关闭浏览器
  window.addEventListener('beforeunload', handleBeforeUnload)

  chatStore.mobileView = 'list'
  await chatStore.loadConversationList()  // 先加载会话列表
  chatStore.loadAgents()                  // REST API: GET /agents
  chatStore.initWebSocket()

  // 列表加载完后，检查路由中的 conversationId 是否有效
  const id = route.params.conversationId
  if (id && typeof id === 'string') {
    chatStore.selectConversation(id)
  }
})

onBeforeUnmount(() => {
  window.removeEventListener('beforeunload', handleBeforeUnload)
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
