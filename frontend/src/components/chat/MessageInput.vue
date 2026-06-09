<template>
  <footer class="h-[180px] bg-white/90 backdrop-blur-md border-t flex flex-col shrink-0 input-footer">
    <div class="h-10 px-4 flex items-center gap-4 input-toolbar">
      <SmileIcon :size="20" class="cursor-pointer transition-colors toolbar-icon" />
      <FolderIcon :size="20" class="cursor-pointer transition-colors toolbar-icon" />
      <ScissorsIcon :size="20" class="cursor-pointer transition-colors toolbar-icon" />
      <HistoryIcon :size="20" class="cursor-pointer transition-colors toolbar-icon ml-auto" />
    </div>

    <div class="flex-1 px-4">
      <textarea
        v-model="input"
        class="w-full h-full resize-none border-none outline-none text-[14px] text-gray-800 leading-relaxed py-1 bg-transparent"
        :placeholder="placeholder"
        :disabled="disabled"
        @keydown.enter.exact.prevent="handleSend"
      ></textarea>
    </div>

    <div class="h-12 px-4 flex justify-end items-center">
      <button
        @click="handleSend"
        :class="[
          'px-6 py-2 rounded-xl text-[13px] font-semibold transition-all shadow-md',
          canSend ? 'send-btn text-white hover:shadow-lg hover:scale-105 transform' : 'bg-gray-100 text-gray-400 cursor-not-allowed'
        ]"
        :disabled="!canSend"
      >
        发送
      </button>
    </div>
  </footer>
</template>

<script setup lang="ts">
import { ref, computed } from 'vue'
import {
  Smile as SmileIcon,
  Folder as FolderIcon,
  Scissors as ScissorsIcon,
  History as HistoryIcon,
} from 'lucide-vue-next'

const props = withDefaults(defineProps<{
  disabled?: boolean
  placeholder?: string
}>(), {
  disabled: false,
  placeholder: '输入消息...',
})

const emit = defineEmits<{
  send: [content: string]
}>()

const input = ref('')

const canSend = computed(() => input.value.trim().length > 0 && !props.disabled)

const handleSend = () => {
  const content = input.value.trim()
  if (!content || props.disabled) return

  emit('send', content)
  input.value = ''
}
</script>

<style scoped>
.input-footer { border-color: color-mix(in srgb, var(--accent-start) 15%, #e2e8f0); }
.toolbar-icon { color: color-mix(in srgb, var(--accent-start) 50%, #94a3b8); }
.toolbar-icon:hover { color: var(--accent-start); }
.send-btn { background: linear-gradient(to right, var(--accent-start), var(--accent-end)); }
</style>
