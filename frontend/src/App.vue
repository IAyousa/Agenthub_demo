<script setup lang="ts">
import SideBar from './components/layout/SideBar.vue'
import ChatList from './components/chat/ChatList.vue'
import ChatWindow from './components/chat/ChatWindow.vue'
import ArtifactWindow from './components/chat/ArtifactWindow.vue'
import { useChatStore } from './stores/chat'

const chatStore = useChatStore()
</script>

<template>
  <div class="h-screen w-screen flex overflow-hidden font-sans select-none">
    <!-- Left: Navigation Sidebar (Dark) - Always visible, fixed width -->
    <SideBar class="flex-shrink-0" />

    <!-- Main Responsive Container -->
    <div class="flex-1 flex overflow-hidden relative">
      <!-- Middle: Chat List -->
      <ChatList 
        :class="[
          'flex-shrink-0 w-full md:w-64 border-r border-[#d6d6d6]',
          chatStore.mobileView === 'chat' ? 'hidden md:flex' : 'flex'
        ]"
      />

      <!-- Right: Main Chat Area -->
      <div 
        :class="[
          'flex-1 h-full flex overflow-hidden relative',
          chatStore.mobileView === 'list' ? 'hidden md:flex' : 'flex'
        ]"
      >
        <!-- Chat Window -->
        <div class="h-full w-full overflow-hidden">
          <ChatWindow class="w-full h-full" />
        </div>

        <!-- Artifact Window (Overlay) -->
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
  </div>
</template>

<style>
/* Global WeChat-like scrollbar */
::-webkit-scrollbar {
  width: 6px;
  height: 6px;
}
::-webkit-scrollbar-thumb {
  background: #c3c3c3;
  border-radius: 10px;
}
::-webkit-scrollbar-track {
  background: transparent;
}

/* Artifact Overlay Transition */
.overlay-enter-active,
.overlay-leave-active {
  transition: all 0.4s cubic-bezier(0.4, 0, 0.2, 1);
}

.overlay-enter-from,
.overlay-leave-to {
  transform: translateY(100%);
  opacity: 0.8;
}

#app {
  height: 100vh;
  width: 100vw;
}

body {
  margin: 0;
  padding: 0;
  overflow: hidden;
  background-color: #f5f5f5;
}
</style>
