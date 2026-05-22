<template>
  <div :class="['flex w-full mb-5 px-4', role === 'user' ? 'flex-row-reverse' : 'flex-row']">
    <!-- Avatar -->
    <div class="w-9 h-9 rounded-sm overflow-hidden flex-shrink-0">
      <img :src="avatarUrl" alt="avatar" />
    </div>

    <!-- Message Content -->
    <div :class="[
      'flex flex-col',
      type === 'text' ? 'max-w-[85%] md:max-w-[70%]' : 'w-full md:max-w-[85%]',
      role === 'user' ? 'mr-3 items-end' : 'ml-3 items-start'
    ]">
      <!-- Chat Bubble -->
      <div :class="[
        'rounded-md text-[14px] leading-relaxed relative break-words shadow-sm',
        type === 'code' || type === 'artifact_preview' ? 'w-full p-0 overflow-hidden' : 'px-3 py-2',
        role === 'user' ? 'bg-[#95ec69] text-black after:content-[\'\'] after:absolute after:top-3 after:-right-1.5 after:border-t-[6px] after:border-t-transparent after:border-b-[6px] after:border-b-transparent after:border-l-[6px] after:border-l-[#95ec69]' : 'bg-white text-black after:content-[\'\'] after:absolute after:top-3 after:-left-1.5 after:border-t-[6px] after:border-t-transparent after:border-b-[6px] after:border-b-transparent after:border-r-[6px] after:border-r-white'
      ]">
        <!-- Text -->
        <div v-if="type === 'text'" class="whitespace-pre-wrap">
          {{ content }}
        </div>

        <!-- Code -->
        <div v-else-if="type === 'code'" class="w-full overflow-hidden">
          <CodeEditor 
            :code="content" 
            :language="metadata?.language || 'plaintext'" 
            :read-only="true"
          />
        </div>

        <!-- Artifact Preview -->
        <div 
          v-else-if="type === 'artifact_preview'" 
          @click="handleArtifactClick"
          class="w-full border border-gray-200 rounded bg-white overflow-hidden shadow-sm cursor-pointer hover:border-green-300 hover:shadow-md transition-all group"
        >
          <div class="flex items-center gap-2 px-3 py-2 bg-gray-50 border-b border-gray-100 text-[12px] text-gray-600 group-hover:bg-green-50">
            <div class="w-2.5 h-2.5 rounded-full bg-green-500 animate-pulse"></div>
            <span class="font-semibold">{{ metadata?.title || 'Preview' }}</span>
          </div>
          <div class="p-6 flex flex-col items-start bg-white">
            <div class="text-[11px] text-gray-400 mb-2 flex items-center gap-1">
              <span>点击查看完整产物</span>
              <div class="w-1 h-1 rounded-full bg-gray-300"></div>
              <span class="uppercase">{{ metadata?.language || 'html' }}</span>
            </div>
            <div class="w-full text-[13px] text-gray-600 font-mono line-clamp-3 opacity-80 bg-gray-50 p-3 rounded border border-gray-100 italic">
              {{ content.substring(0, 200) }}...
            </div>
          </div>
        </div>
      </div>
    </div>
  </div>
</template>

<script setup lang="ts">
import { computed } from 'vue'
import CodeEditor from './CodeEditor.vue'
import { useChatStore } from '../../stores/chat'

const chatStore = useChatStore()

const props = defineProps<{
  id: string
  role: 'user' | 'assistant' | 'system'
  type: 'text' | 'code' | 'diff' | 'artifact_preview'
  content: string
  metadata?: Record<string, any>
}>()

const handleArtifactClick = () => {
  if (props.type === 'artifact_preview') {
    chatStore.showArtifact({
      id: props.id,
      title: props.metadata?.title || 'Preview',
      code: props.content,
      language: props.metadata?.language || 'html'
    })
  }
}

const avatarUrl = computed(() => {
  if (props.role === 'user') return 'https://api.dicebear.com/7.x/avataaars/svg?seed=Felix'
  return `https://api.dicebear.com/7.x/bottts/svg?seed=${props.role}`
})
</script>
