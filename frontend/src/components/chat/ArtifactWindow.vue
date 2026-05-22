<template>
  <div class="w-full h-full flex flex-col bg-white">
    <!-- Header -->
    <div class="flex items-center justify-between px-4 py-3 border-b border-gray-200 bg-gray-50">
      <div class="flex items-center gap-3">
        <button 
          @click="$emit('close')" 
          class="p-1.5 hover:bg-gray-200 rounded-md transition-colors text-gray-600 flex items-center gap-1 group"
          title="Back to Chat"
        >
          <ArrowLeft :size="20" class="group-hover:-translate-x-0.5 transition-transform" />
          <span class="text-sm font-medium">返回聊天</span>
        </button>
        <div class="h-4 w-[1px] bg-gray-300 mx-1"></div>
        <div class="flex items-center gap-2">
          <div class="p-1 bg-green-100 rounded">
            <Layout :size="16" class="text-green-600" />
          </div>
          <div>
            <h3 class="text-sm font-semibold text-gray-800 leading-none">{{ title }}</h3>
            <p class="text-[10px] text-gray-500 uppercase mt-1">{{ language }}</p>
          </div>
        </div>
      </div>
      <div class="flex items-center gap-2">
        <button 
          @click="toggleMode" 
          class="p-1.5 hover:bg-gray-200 rounded-md transition-colors text-gray-600"
          :title="mode === 'preview' ? 'View Code' : 'View Preview'"
        >
          <Code v-if="mode === 'preview'" :size="18" />
          <Eye v-else :size="18" />
        </button>
      </div>
    </div>

    <!-- Content Area -->
    <div class="flex-1 overflow-hidden relative">
      <div v-if="mode === 'preview'" class="w-full h-full">
        <ArtifactSandbox :code="code" :language="language" />
      </div>
      <div v-else class="w-full h-full">
        <CodeEditor :code="code" :language="language" :read-only="true" class="rounded-none border-none" />
      </div>
    </div>
  </div>
</template>

<script setup lang="ts">
import { ref } from 'vue'
import { ArrowLeft, Layout, Code, Eye } from 'lucide-vue-next'
import ArtifactSandbox from './ArtifactSandbox.vue'
import CodeEditor from './CodeEditor.vue'

const props = defineProps<{
  title: string
  code: string
  language: string
}>()

defineEmits(['close'])

const mode = ref<'preview' | 'code'>('preview')

const toggleMode = () => {
  mode.value = mode.value === 'preview' ? 'code' : 'preview'
}
</script>
