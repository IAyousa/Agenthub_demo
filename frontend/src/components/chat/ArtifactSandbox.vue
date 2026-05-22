<template>
  <div class="w-full h-full bg-white overflow-hidden flex flex-col relative">
    <iframe
      ref="iframeRef"
      class="w-full h-full border-none bg-white"
      sandbox="allow-scripts allow-same-origin"
      :srcdoc="srcdoc"
    ></iframe>
    <div v-if="error" class="absolute inset-0 flex items-center justify-center bg-red-50 text-red-500 p-4 text-center">
      <div class="flex flex-col items-center gap-2">
        <AlertCircle :size="24" />
        <p class="text-sm">{{ error }}</p>
      </div>
    </div>
  </div>
</template>

<script setup lang="ts">
import { ref, computed } from 'vue'
import { AlertCircle } from 'lucide-vue-next'

const props = defineProps<{
  code: string
  language: string
}>()

const error = ref<string | null>(null)

const srcdoc = computed(() => {
  try {
    if (props.language === 'html') {
      return props.code
    }
    
    if (props.language === 'javascript' || props.language === 'typescript') {
      return `
        <!DOCTYPE html>
        <html>
          <head>
            <meta charset="UTF-8">
            <style>
              body { font-family: sans-serif; padding: 20px; margin: 0; }
            </style>
          </head>
          <body>
            <div id="root"></div>
            <script>
              try {
                ${props.code}
              } catch (err) {
                document.body.innerHTML = '<div style="color: red; padding: 20px;">Runtime Error: ' + err.message + '</div>';
              }
            <\/script>
          </body>
        </html>
      `
    }
    
    if (props.language === 'css') {
      return `
        <!DOCTYPE html>
        <html>
          <head>
            <meta charset="UTF-8">
            <style>${props.code}</style>
          </head>
          <body>
            <div class="preview-container" style="padding: 20px;">
              <h1>CSS Preview</h1>
              <p>This is a preview of your CSS code.</p>
              <div class="box" style="width: 100px; height: 100px; background: #eee; display: flex; align-items: center; justify-content: center; margin-bottom: 10px;">Box</div>
              <button style="padding: 8px 16px;">Button</button>
            </div>
          </body>
        </html>
      `
    }

    return `
      <!DOCTYPE html>
      <html>
        <head><meta charset="UTF-8"></head>
        <body style="padding: 20px;"><pre>${props.code}</pre></body>
      </html>
    `
  } catch (err: any) {
    console.error('Failed to generate srcdoc:', err)
    return `<html><body><div style="color: red">Render Error: ${err.message}</div></body></html>`
  }
})
</script>
