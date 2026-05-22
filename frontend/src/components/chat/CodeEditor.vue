<template>
  <div class="code-editor-container flex flex-col h-full w-full rounded-md overflow-hidden border border-[#333] bg-[#1e1e1e]">
    <!-- Header -->
    <div class="flex items-center justify-between px-3 py-1.5 bg-[#2d2d2d] text-[#cccccc] text-[12px] font-sans border-b border-[#333]">
      <div class="flex items-center gap-2">
        <Code :size="14" class="text-blue-400" />
        <span class="font-medium tracking-wide uppercase opacity-80">{{ language }}</span>
      </div>
      <div class="flex items-center gap-3">
        <button 
          @click="copyCode" 
          class="hover:text-white transition-all flex items-center gap-1.5 px-2 py-0.5 rounded hover:bg-[#3d3d3d]"
          title="Copy Code"
        >
          <component :is="copied ? Check : Copy" :size="14" />
          <span>{{ copied ? '已复制' : '复制' }}</span>
        </button>
      </div>
    </div>
    
    <!-- Editor Instance -->
    <div ref="editorContainer" class="flex-1 min-h-[300px] md:min-h-[400px] w-full"></div>
  </div>
</template>

<script setup lang="ts">
import { ref, onMounted, onBeforeUnmount, watch } from 'vue'
import * as monaco from 'monaco-editor'
import { Copy, Check, Code } from 'lucide-vue-next'

const props = defineProps<{
  code: string
  language?: string
  readOnly?: boolean
}>()

const editorContainer = ref<HTMLElement | null>(null)
let editor: monaco.editor.IStandaloneCodeEditor | null = null
let resizeObserver: ResizeObserver | null = null
const copied = ref(false)

const initMonaco = () => {
  if (!editorContainer.value) return

  editor = monaco.editor.create(editorContainer.value, {
    value: props.code,
    language: props.language || 'plaintext',
    theme: 'vs-dark',
    readOnly: props.readOnly ?? true,
    automaticLayout: false, // We'll handle layout manually for better performance and reliability
    minimap: { enabled: false },
    fontSize: 13,
    lineNumbers: 'on',
    scrollBeyondLastLine: false,
    renderLineHighlight: 'all',
    scrollbar: {
      vertical: 'auto',
      horizontal: 'auto'
    },
    padding: { top: 10, bottom: 10 }
  })

  // Watch for container size changes
  resizeObserver = new ResizeObserver(() => {
    if (editor) {
      editor.layout()
    }
  })
  resizeObserver.observe(editorContainer.value)
}

const copyCode = async () => {
  try {
    await navigator.clipboard.writeText(props.code)
    copied.value = true
    setTimeout(() => {
      copied.value = false
    }, 2000)
  } catch (err) {
    console.error('Failed to copy code:', err)
  }
}

watch(() => props.code, (newCode) => {
  if (editor && editor.getValue() !== newCode) {
    editor.setValue(newCode)
  }
})

watch(() => props.language, (newLang) => {
  if (editor) {
    const model = editor.getModel()
    if (model) {
      monaco.editor.setModelLanguage(model, newLang || 'plaintext')
    }
  }
})

onMounted(() => {
  initMonaco()
})

onBeforeUnmount(() => {
  if (resizeObserver) {
    resizeObserver.disconnect()
  }
  if (editor) {
    editor.dispose()
  }
})
</script>

<style scoped>
.code-editor-container {
  font-family: 'Consolas', 'Monaco', 'Courier New', monospace;
}
</style>
