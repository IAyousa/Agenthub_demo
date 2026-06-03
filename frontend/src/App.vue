<script setup lang="ts">
import SideBar from './components/layout/SideBar.vue'
</script>

<template>
  <div class="h-screen w-screen flex overflow-hidden font-sans select-none">
    <SideBar class="flex-shrink-0" />

    <RouterView v-slot="{ Component }">
      <Transition name="main-view" mode="out-in">
        <component :is="Component" />
      </Transition>
    </RouterView>
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
