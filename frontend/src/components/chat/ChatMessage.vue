<template>
  <div :class="['flex w-full mb-5 px-4', role === 'user' ? 'flex-row-reverse' : 'flex-row']">
    <!-- Avatar -->
    <div class="w-9 h-9 rounded-xl overflow-hidden flex-shrink-0 shadow-md" :class="role === 'user' ? 'bg-gradient-to-br from-indigo-500 to-purple-600' : 'bg-gradient-to-br from-purple-400 to-indigo-500'">
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
        'rounded-xl text-[14px] leading-relaxed relative break-words shadow-md',
        type === 'code' || type === 'artifact_preview' ? 'w-full p-0 overflow-hidden' : 'px-4 py-3',
        role === 'user' ? 'bg-gradient-to-br from-indigo-500 to-purple-600 text-white after:content-[\'\'] after:absolute after:top-4 after:-right-2 after:border-t-[7px] after:border-t-transparent after:border-b-[7px] after:border-b-transparent after:border-l-[7px] after:border-l-indigo-500' : 'bg-white text-gray-800 after:content-[\'\'] after:absolute after:top-4 after:-left-2 after:border-t-[7px] after:border-t-transparent after:border-b-[7px] after:border-b-transparent after:border-r-[7px] after:border-r-white'
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
          class="w-full border border-indigo-100 rounded-xl bg-white overflow-hidden shadow-sm cursor-pointer hover:border-indigo-300 hover:shadow-lg transition-all group"
        >
          <div class="flex items-center gap-2 px-3 py-2 bg-gradient-to-r from-indigo-50 to-purple-50 border-b border-indigo-100 text-[12px] text-indigo-700 group-hover:bg-gradient-to-r from-indigo-100 to-purple-100">
            <div class="w-2.5 h-2.5 rounded-full bg-gradient-to-r from-indigo-500 to-purple-500 animate-pulse"></div>
            <span class="font-semibold">{{ metadata?.title || 'Preview' }}</span>
          </div>
          <div class="p-6 flex flex-col items-start bg-white">
            <div class="text-[11px] text-gray-400 mb-2 flex items-center gap-1">
              <span>点击查看完整产物</span>
              <div class="w-1 h-1 rounded-full bg-gray-300"></div>
              <span class="uppercase">{{ metadata?.language || 'html' }}</span>
            </div>
            <div class="w-full text-[13px] text-gray-600 font-mono line-clamp-3 opacity-80 bg-gradient-to-br from-gray-50 to-indigo-50 p-3 rounded-lg border border-gray-100 italic">
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
