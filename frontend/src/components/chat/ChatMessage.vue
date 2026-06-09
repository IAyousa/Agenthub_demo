<template>
  <div :class="['flex w-full mb-5 px-4 group', role === 'user' ? 'flex-row-reverse' : 'flex-row']">
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
        <!-- Text (rendered as Markdown) -->
        <div v-if="type === 'text'" class="markdown-body" v-html="renderedContent"></div>

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

      <!-- Action bar (appears on hover) -->
      <div
        :class="[
          'flex items-center gap-1 mt-1.5 transition-all duration-150',
          role === 'user' ? 'justify-end' : 'justify-start',
          'opacity-0 group-hover:opacity-100'
        ]"
      >
        <button
          @click="copyContent"
          class="flex items-center gap-1 px-2 py-1 rounded-md text-[11px] text-gray-400 bg-white/80 hover:bg-white hover:text-indigo-500 hover:shadow-sm border border-gray-100 transition-all"
          :title="copied ? '已复制' : '复制'"
        >
          <ClipboardIcon :size="12" />
          <span>{{ copied ? '已复制' : '复制' }}</span>
        </button>
      </div>
    </div>
  </div>
</template>

<script setup lang="ts">
import { computed, ref, onMounted, nextTick, watch } from 'vue'
import { marked } from 'marked'
import { ClipboardIcon, CheckIcon } from 'lucide-vue-next'
import { createApp, h } from 'vue'

// Custom marked renderer: DeepSeek-style code blocks with header bar
const renderer = new marked.Renderer()
const originalCode = renderer.code.bind(renderer)
renderer.code = function(token: marked.Tokens.Code) {
  const lang = token.lang || 'plaintext'
  const raw = originalCode(token)
  const id = `code-${Math.random().toString(36).slice(2, 8)}`
  return `
<div class="md-code-block md-code-block-dark">
  <div class="md-code-block-banner">
    <span class="md-code-lang">${lang}</span>
    <div class="md-code-actions">
      <button class="md-code-btn" data-code-id="${id}">
        <svg width="14" height="14" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"><rect x="9" y="9" width="13" height="13" rx="2" ry="2"/><path d="M5 15H4a2 2 0 0 1-2-2V4a2 2 0 0 1 2-2h9a2 2 0 0 1 2 2v1"/></svg>
        <span>复制</span>
      </button>
    </div>
  </div>
  <div class="md-code-body" id="${id}">${raw}</div>
</div>`
}

marked.use({ renderer })

// Global click handler for dynamically rendered copy buttons
if (typeof document !== 'undefined') {
  document.addEventListener('click', (e) => {
    const btn = (e.target as HTMLElement).closest('.md-code-btn') as HTMLElement | null
    if (!btn) return
    const codeId = btn.dataset.codeId
    if (!codeId) return
    const codeEl = document.getElementById(codeId)
    if (!codeEl) return
    const text = codeEl.querySelector('code')?.textContent || codeEl.textContent || ''
    navigator.clipboard.writeText(text).then(() => {
      const span = btn.querySelector('span')
      const svg = btn.querySelector('svg')
      if (span) span.textContent = '已复制'
      if (svg) { svg.innerHTML = '<polyline points="20 6 9 17 4 12"/>'; svg.setAttribute('stroke', '#22c55e') }
      setTimeout(() => {
        if (span) span.textContent = '复制'
        if (svg) { svg.innerHTML = '<rect x="9" y="9" width="13" height="13" rx="2" ry="2"/><path d="M5 15H4a2 2 0 0 1-2-2V4a2 2 0 0 1 2-2h9a2 2 0 0 1 2 2v1"/>'; svg.setAttribute('stroke', 'currentColor') }
      }, 2000)
    }).catch(() => {})
  })
}
import CodeEditor from './CodeEditor.vue'
import { useChatStore } from '../../stores/chat'

const chatStore = useChatStore()
const copied = ref(false)

const props = defineProps<{
  id: string
  role: 'user' | 'assistant' | 'system'
  type: 'text' | 'code' | 'diff' | 'artifact_preview'
  content: string
  metadata?: Record<string, any>
}>()

// HTML 标签正则：防止 XSS 同时保留 markdown 语法
const HTML_TAG_RE = /<(\/?[a-zA-Z][a-zA-Z0-9]*)/g

const renderedContent = computed(() => {
  if (props.type !== 'text') return ''
  // 转义 HTML 标签（如 <script>），保留 markdown 自动链接 <url>
  const safeContent = props.content.replace(HTML_TAG_RE, '&lt;$1')
  return marked.parse(safeContent, { breaks: true }) as string
})

const handleArtifactClick = async () => {
  if (props.type !== 'artifact_preview') return
  let code = props.content
  // If loaded from API, content is just a filename — fetch actual file
  const previewUrl = props.metadata?.previewUrl
  if (previewUrl && (!code || code.includes('.html') || code.includes('.js') || code.includes('.css') || !code.includes('<'))) {
    try {
      const res = await fetch(`http://localhost:8080${previewUrl}`)
      if (res.ok) {
        code = await res.text()
      }
    } catch { /* keep filename as fallback */ }
  }
  chatStore.showArtifact({
    id: props.id,
    title: props.metadata?.title || 'Preview',
    code,
    language: props.metadata?.language || 'html'
  })
}

const copyContent = async () => {
  try {
    await navigator.clipboard.writeText(props.content)
    copied.value = true
    setTimeout(() => { copied.value = false }, 2000)
  } catch {
    // fallback for older browsers
  }
}

const avatarUrl = computed(() => {
  if (props.role === 'user') return 'https://api.dicebear.com/7.x/avataaars/svg?seed=Felix'
  return `https://api.dicebear.com/7.x/bottts/svg?seed=${props.role}`
})
</script>

<style>
/* 主题色覆盖：用户消息气泡渐变 */
.bg-gradient-to-br.from-indigo-500.to-purple-600 {
  background-image: linear-gradient(to bottom right, var(--accent-start), var(--accent-end)) !important;
}
/* 主题色覆盖：头像 */
.bg-gradient-to-br.from-indigo-500.to-purple-600,
.bg-gradient-to-br.from-purple-400.to-indigo-500 {
  background-image: linear-gradient(to bottom right, var(--accent-start), var(--accent-end)) !important;
}
/* 主题色覆盖：预览卡片 header */
.bg-gradient-to-r.from-indigo-50.to-purple-50 {
  background-image: linear-gradient(to right, color-mix(in srgb, var(--accent-start) 10%, white), color-mix(in srgb, var(--accent-end) 10%, white)) !important;
}
.bg-gradient-to-r.from-indigo-100.to-purple-100 {
  background-image: linear-gradient(to right, color-mix(in srgb, var(--accent-start) 15%, white), color-mix(in srgb, var(--accent-end) 15%, white)) !important;
}
/* 主题色覆盖：预览卡片圆点 */
.bg-gradient-to-r.from-indigo-500.to-purple-500 {
  background-image: linear-gradient(to right, var(--accent-start), var(--accent-end)) !important;
}
/* 主题色覆盖：预览卡片文字 */
.text-indigo-700 { color: color-mix(in srgb, var(--accent-start) 70%, #475569) !important; }
.border-indigo-100 { border-color: color-mix(in srgb, var(--accent-start) 15%, #e2e8f0) !important; }
/* 主题色覆盖：片段背景 */
.bg-gradient-to-br.from-gray-50.to-indigo-50 {
  background-image: linear-gradient(to bottom right, #f9fafb, var(--accent-light)) !important;
}
/* 主题色覆盖：操作按钮 hover */
.hover\:text-indigo-500:hover { color: var(--accent-start) !important; }
/* 主题色覆盖：markdown 链接和引用 */
.markdown-body a { color: var(--accent-start); }
.markdown-body blockquote {
  border-left-color: var(--accent-start);
}

.markdown-body {
  line-height: 1.7;
}
.markdown-body h1, .markdown-body h2, .markdown-body h3 {
  font-weight: 600;
  margin: 0.6em 0 0.3em;
}
.markdown-body h1 { font-size: 1.3em; }
.markdown-body h2 { font-size: 1.15em; }
.markdown-body h3 { font-size: 1.05em; }
.markdown-body p { margin: 0.4em 0; }
.markdown-body ul, .markdown-body ol { padding-left: 1.5em; margin: 0.4em 0; }
.markdown-body li { margin: 0.15em 0; }
.markdown-body strong { font-weight: 600; }
.markdown-body em { font-style: italic; }
.markdown-body code {
  background: #e2e8f0;
  color: #1e293b;
  padding: 0.15em 0.4em;
  border-radius: 4px;
  font-size: 0.9em;
  font-family: 'Consolas', 'Monaco', monospace;
}
/* Code block with header bar */
.md-code-block {
  margin: 0.6em 0;
  border-radius: 10px;
  overflow: hidden;
  background: #1e1e1e;
}
.md-code-block-banner {
  display: flex;
  align-items: center;
  justify-content: space-between;
  padding: 0 12px;
  height: 32px;
  background: #252525;
  user-select: none;
}
.md-code-lang {
  font-size: 12px;
  color: #8b8b8b;
  font-family: 'Consolas', 'Monaco', monospace;
}
.md-code-actions {
  display: flex;
  align-items: center;
  gap: 2px;
}
.md-code-btn {
  display: inline-flex;
  align-items: center;
  gap: 4px;
  padding: 2px 8px;
  border-radius: 6px;
  border: none;
  background: transparent;
  color: #8b8b8b;
  cursor: pointer;
  font-size: 11px;
  line-height: 20px;
  transition: all 0.15s;
}
.md-code-btn:hover {
  background: rgba(255,255,255,0.08);
  color: #d4d4d4;
}
.md-code-body pre {
  margin: 0 !important;
  border-radius: 0 !important;
  background: #1e1e1e !important;
}
.md-code-body code {
  font-size: 0.85em;
  line-height: 1.65;
}

.markdown-body pre {
  background: #1e293b;
  color: #e2e8f0;
  padding: 1em;
  border-radius: 8px;
  overflow-x: auto;
  margin: 0.6em 0;
}
.markdown-body pre code {
  background: transparent;
  padding: 0;
  color: inherit;
  font-size: 0.88em;
}
.markdown-body blockquote {
  border-left: 3px solid #818cf8;
  padding-left: 1em;
  color: #64748b;
  margin: 0.5em 0;
}
.markdown-body table {
  border-collapse: collapse;
  width: 100%;
  margin: 0.5em 0;
}
.markdown-body th, .markdown-body td {
  border: 1px solid #e2e8f0;
  padding: 0.4em 0.8em;
  text-align: left;
  font-size: 0.9em;
}
.markdown-body th {
  background: #f8fafc;
  font-weight: 600;
}
.markdown-body hr {
  border: none;
  border-top: 1px solid #e2e8f0;
  margin: 0.8em 0;
}
.markdown-body a {
  color: #6366f1;
  text-decoration: underline;
}
.markdown-body > *:first-child { margin-top: 0; }
.markdown-body > *:last-child { margin-bottom: 0; }
</style>
