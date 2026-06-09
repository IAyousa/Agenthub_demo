<template>
  <Teleport to="body">
    <Transition name="modal-fade">
      <div v-if="isOpen" class="fixed inset-0 z-50 flex items-center justify-center bg-black/40 backdrop-blur-sm" @click.self="$emit('close')">
        <div class="bg-white rounded-3xl shadow-2xl w-full max-w-sm mx-4 overflow-hidden animate-in fade-in zoom-in-95 duration-300">
          <div class="bg-gradient-to-r from-indigo-600 to-purple-600 px-8 py-6">
            <div class="flex items-center justify-between">
              <h2 class="text-2xl font-bold text-white">界面主题</h2>
              <button @click="$emit('close')" class="text-white/80 hover:text-white transition-colors">
                <svg class="w-6 h-6" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                  <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M6 18L18 6M6 6l12 12" />
                </svg>
              </button>
            </div>
            <p class="text-indigo-100 text-sm mt-2">选择你喜欢的配色方案</p>
          </div>

          <div class="px-8 py-6">
            <div class="grid grid-cols-2 gap-4">
              <button
                v-for="theme in settings.themes"
                :key="theme.id"
                @click="settings.setTheme(theme.id)"
                :class="[
                  'p-4 rounded-2xl border-2 transition-all text-center',
                  settings.currentThemeId === theme.id
                    ? 'border-indigo-600 shadow-md ring-2 ring-indigo-200'
                    : 'border-slate-200 hover:border-slate-300'
                ]"
              >
                <div
                  class="w-full h-14 rounded-xl mb-3 shadow-sm"
                  :style="{ background: `linear-gradient(135deg, ${theme.colors.sidebarStart}, ${theme.colors.sidebarEnd})` }"
                ></div>
                <div class="flex items-center justify-center gap-1.5 mb-2">
                  <span class="w-3 h-3 rounded-full" :style="{ background: theme.colors.accentStart }"></span>
                  <span class="w-3 h-3 rounded-full" :style="{ background: theme.colors.accentEnd }"></span>
                </div>
                <p class="text-sm font-semibold text-slate-700">{{ theme.name }}</p>
                <p v-if="settings.currentThemeId === theme.id" class="text-xs text-indigo-500 mt-1">当前使用</p>
              </button>
            </div>
          </div>
        </div>
      </div>
    </Transition>
  </Teleport>
</template>

<script setup lang="ts">
import { useSettingsStore } from '../../stores/settings'

interface Props { isOpen: boolean }
defineProps<Props>()
defineEmits(['close'])

const settings = useSettingsStore()
</script>

<style scoped>
/* 主题色覆盖 */
.from-indigo-600 { --tw-gradient-from: var(--accent-start) !important; }
.to-purple-600 { --tw-gradient-to: var(--accent-end) !important; }
.text-indigo-100 { color: color-mix(in srgb, var(--accent-start) 30%, white) !important; }
.text-indigo-500 { color: var(--accent-start) !important; }
.border-indigo-600 { border-color: var(--accent-start) !important; }
.ring-indigo-200 { --tw-ring-color: color-mix(in srgb, var(--accent-start) 30%, transparent) !important; }

.modal-fade-enter-active, .modal-fade-leave-active { transition: opacity 0.3s ease; }
.modal-fade-enter-from, .modal-fade-leave-to { opacity: 0; }
.animate-in { animation: slideIn 0.3s ease-out; }
@keyframes slideIn { from { opacity: 0; transform: scale(0.95); } to { opacity: 1; transform: scale(1); } }
</style>
