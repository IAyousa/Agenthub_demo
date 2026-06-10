<template>
  <div class="w-full border border-emerald-200 rounded-xl overflow-hidden shadow-md hover:shadow-lg transition-shadow">
    <!-- Header -->
    <div class="flex items-center justify-between px-4 py-2.5 bg-gradient-to-r from-emerald-50 to-teal-50 border-b border-emerald-100">
      <div class="flex items-center gap-2 text-[13px] font-semibold text-emerald-700">
        <svg width="16" height="16" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round" class="text-emerald-500">
          <path d="M16 4h2a2 2 0 0 1 2 2v14a2 2 0 0 1-2 2H6a2 2 0 0 1-2-2V6a2 2 0 0 1 2-2h2"/>
          <rect x="8" y="2" width="8" height="4" rx="1" ry="1"/>
        </svg>
        <span>项目成果</span>
        <span class="text-[11px] font-normal text-emerald-500 bg-emerald-100 px-1.5 py-0.5 rounded">
          {{ files.length }} 个文件
        </span>
      </div>
      <a
        v-if="downloadUrl"
        @click.prevent="handleDownload"
        class="flex items-center gap-1 text-[11px] text-emerald-600 hover:text-emerald-800 transition-colors px-2 py-1 rounded hover:bg-emerald-100 cursor-pointer"
      >
        <svg width="14" height="14" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round">
          <path d="M21 15v4a2 2 0 0 1-2 2H5a2 2 0 0 1-2-2v-4"/>
          <polyline points="7 10 12 15 17 10"/>
          <line x1="12" y1="15" x2="12" y2="3"/>
        </svg>
        <span>{{ downloading ? '下载中...' : '下载全部' }}</span>
      </a>
    </div>

    <!-- File Tree -->
    <div class="bg-white">
      <div
        v-for="file in files"
        :key="file.artifactId"
        class="border-b border-gray-50 last:border-b-0"
      >
        <div
          @click="toggleFile(file)"
          class="flex items-center gap-2 px-4 py-2.5 cursor-pointer hover:bg-gray-50 transition-colors"
        >
          <svg
            width="14" height="14" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2"
            class="text-gray-400 transition-transform duration-150"
            :class="{ 'rotate-90': expandedFiles.has(file.artifactId) }"
          >
            <polyline points="9 18 15 12 9 6"/>
          </svg>
          <svg width="14" height="14" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" class="text-gray-400">
            <path d="M13 2H6a2 2 0 0 0-2 2v16a2 2 0 0 0 2 2h12a2 2 0 0 0 2-2V9z"/>
            <polyline points="13 2 13 9 20 9"/>
          </svg>
          <span class="text-[12px] text-gray-700 font-mono flex-1 truncate">{{ file.path || file.filename }}</span>
          <span class="text-[10px] uppercase text-gray-400 bg-gray-100 px-1.5 py-0.5 rounded">{{ file.language }}</span>
          <span class="text-[10px] text-gray-400">{{ formatSize(file.size) }}</span>
        </div>

        <!-- Expanded Preview -->
        <div v-if="expandedFiles.has(file.artifactId)" class="px-4 pb-3">
          <div v-if="file.language === 'html'" class="border border-gray-200 rounded-lg overflow-hidden">
            <div class="flex items-center justify-between px-3 py-1.5 bg-gray-50 border-b border-gray-100">
              <span class="text-[11px] text-gray-500 font-medium">{{ file.path || file.filename }}</span>
              <a
                :href="file.previewUrl"
                target="_blank"
                class="text-[10px] text-blue-500 hover:text-blue-700"
              >新窗口打开</a>
            </div>
            <iframe
              v-if="htmlContents[file.artifactId]"
              :srcdoc="htmlContents[file.artifactId]"
              class="w-full h-64 border-0"
              sandbox="allow-scripts allow-same-origin"
            />
            <div v-else class="w-full h-64 flex items-center justify-center bg-gray-100 text-gray-400 text-xs">加载中...</div>
          </div>
          <div v-else class="border border-gray-200 rounded-lg overflow-hidden">
            <div class="flex items-center justify-between px-3 py-1.5 bg-gray-50 border-b border-gray-100">
              <span class="text-[11px] text-gray-500 font-medium">{{ file.path || file.filename }}</span>
              <span class="text-[10px] text-gray-400">{{ file.language }}</span>
            </div>
            <pre class="text-[11px] p-3 max-h-80 overflow-auto bg-gray-900 text-gray-100 font-mono leading-relaxed"><code>{{ fileContents[file.artifactId] || '加载中...' }}</code></pre>
          </div>
        </div>
      </div>
    </div>
  </div>
</template>

<script setup lang="ts">
import { ref, reactive, computed } from 'vue'
import apiClient from '../../api/index'

interface FileInfo {
  artifactId: string
  filename: string
  path?: string
  language: string
  previewUrl: string
  size?: number
}

const props = defineProps<{
  files: FileInfo[]
  downloadUrl?: string
}>()

const expandedFiles = ref<Set<string>>(new Set())
const fileContents = reactive<Record<string, string>>({})
const htmlContents = reactive<Record<string, string>>({})
const downloading = ref(false)

/** 从 downloadUrl 提取 conversationId（格式: /conversations/{id}/download） */
const conversationId = computed(() => {
  if (!props.downloadUrl) return ''
  const m = props.downloadUrl.match(/\/conversations\/([^/]+)\/download/)
  return m ? m[1] : ''
})

function formatSize(bytes?: number): string {
  if (!bytes) return ''
  if (bytes < 1024) return `${bytes} B`
  if (bytes < 1024 * 1024) return `${(bytes / 1024).toFixed(1)} KB`
  return `${(bytes / (1024 * 1024)).toFixed(1)} MB`
}

async function handleDownload() {
  if (!props.downloadUrl || downloading.value) return
  downloading.value = true
  try {
    const resp = await apiClient.get(props.downloadUrl, { responseType: 'blob' })
    const blob = new Blob([resp.data], { type: 'application/zip' })
    const url = URL.createObjectURL(blob)
    const a = document.createElement('a')
    a.href = url
    a.download = 'project.zip'
    document.body.appendChild(a)
    a.click()
    document.body.removeChild(a)
    URL.revokeObjectURL(url)
  } catch (e) {
    console.error('Download failed:', e)
  } finally {
    downloading.value = false
  }
}

async function toggleFile(file: FileInfo) {
  if (expandedFiles.value.has(file.artifactId)) {
    expandedFiles.value.delete(file.artifactId)
  } else {
    expandedFiles.value.add(file.artifactId)
    if (file.language === 'html' && !htmlContents[file.artifactId]) {
      try {
        const resp = await apiClient.get(file.previewUrl, { responseType: 'text' })
        const html = typeof resp.data === 'string' ? resp.data : ''
        // 注入 <base> 使相对引用（style.css, script.js）解析到按名称查找的端点
        const baseTag = `<base href="/artifacts/conversation/${conversationId.value}/">`
        let injected: string
        if (/<head[^>]*>/i.test(html)) {
          injected = html.replace(/<head[^>]*>/i, (m: string) => m + baseTag)
        } else if (/<html[^>]*>/i.test(html)) {
          injected = html.replace(/<html[^>]*>/i, (m: string) => m + '<head>' + baseTag + '</head>')
        } else {
          injected = '<head>' + baseTag + '</head>' + html
        }
        htmlContents[file.artifactId] = injected
      } catch {
        htmlContents[file.artifactId] = '<html><body><p>加载失败</p></body></html>'
      }
    } else if (file.language !== 'html' && !fileContents[file.artifactId]) {
      try {
        const resp = await apiClient.get(file.previewUrl, { responseType: 'text' })
        fileContents[file.artifactId] = typeof resp.data === 'string' ? resp.data : JSON.stringify(resp.data)
      } catch (e: any) {
        const status = e?.response?.status || 'ERR'
        fileContents[file.artifactId] = `// 无法加载 (HTTP ${status})`
      }
    }
  }
  expandedFiles.value = new Set(expandedFiles.value)
}
</script>
