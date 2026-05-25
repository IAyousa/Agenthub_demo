<script setup lang="ts">
import SideBar from './components/layout/SideBar.vue'
import ChatList from './components/chat/ChatList.vue'
import ChatWindow from './components/chat/ChatWindow.vue'
import OfficeView from './components/office/OfficeView.vue'
import ArtifactWindow from './components/chat/ArtifactWindow.vue'
import { useChatStore } from './stores/chat'

const chatStore = useChatStore()
</script>

<template>
  <div class="h-screen w-screen flex overflow-hidden font-sans select-none">
    <!-- Left: Navigation Sidebar (Dark) - Always visible, fixed width -->
    <SideBar class="flex-shrink-0" />

    <!-- Main Responsive Container -->
    <Transition name="main-view" mode="out-in">
      <div key="chat" v-if="chatStore.currentView === 'chat'" class="flex-1 flex overflow-hidden relative">
        <!-- Middle: Chat List -->
        <ChatList 
          :class="[
            'flex-shrink-0 w-full md:w-64 border-r border-[#e2e8f0]',
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

      <!-- Office View -->
      <div key="office" v-else class="flex-1 flex overflow-hidden">
        <OfficeView />
      </div>
    </Transition>
  </div>
</template>

<style>
/* Modern tech-style scrollbar */
::-webkit-scrollbar {
  width: 5px;
  height: 5px;
}
::-webkit-scrollbar-thumb {
  background: linear-gradient(180deg, #6366f1, #8b5cf6);
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

/* Main view switch animation */
.main-view-enter-active,
.main-view-leave-active {
  transition: all 0.35s cubic-bezier(0.4, 0, 0.2, 1);
}

.main-view-enter-from {
  opacity: 0;
  transform: translateX(30px);
}

.main-view-leave-to {
  opacity: 0;
  transform: translateX(-30px);
}

#app {
  height: 100vh;
  width: 100vw;
}

body {
  margin: 0;
  padding: 0;
  overflow: hidden;
  background: linear-gradient(135deg, #f8fafc 0%, #eef2ff 100%);
}
</style>
