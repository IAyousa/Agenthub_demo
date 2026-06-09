<template>
  <Teleport to="body">
    <Transition name="modal-fade">
      <div v-if="isOpen" class="fixed inset-0 z-50 flex items-center justify-center bg-black/40 backdrop-blur-sm">
        <div class="bg-white rounded-3xl shadow-2xl w-full max-w-md mx-4 overflow-hidden animate-in fade-in zoom-in-95 duration-300">
          <div class="px-8 py-6" :style="{ background: `linear-gradient(to right, var(--accent-start), var(--accent-end))` }">
            <div class="flex items-center justify-between">
              <h2 class="text-2xl font-bold text-white">新建会话</h2>
              <button @click="closeModal" class="text-white/80 hover:text-white transition-colors">
                <svg class="w-6 h-6" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                  <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M6 18L18 6M6 6l12 12" />
                </svg>
              </button>
            </div>
            <p class="text-indigo-100 text-sm mt-2">创建新会话，选择参与协作的 Agent</p>
          </div>
          <div class="px-8 py-6 space-y-5">
            <div>
              <label class="block text-sm font-semibold text-slate-700 mb-2">会话名称</label>
              <input v-model="formData.title" type="text" placeholder="例如：前端开发讨论"
                class="w-full px-4 py-3 rounded-xl border border-slate-200 focus:border-indigo-500 focus:ring-2 focus:ring-indigo-200 outline-none transition-all" />
              <p v-if="errors.title" class="text-red-500 text-xs mt-1">{{ errors.title }}</p>
            </div>
            <div>
              <label class="block text-sm font-semibold text-slate-700 mb-3">会话类型</label>
              <div class="grid grid-cols-2 gap-3">
                <button @click="formData.type = 'direct'" :class="['p-4 rounded-xl border-2 transition-all text-center', formData.type === 'direct' ? 'border-indigo-600 bg-indigo-50 shadow-sm' : 'border-slate-200 hover:border-slate-300']">
                  <svg class="w-8 h-8 mx-auto mb-2" :class="formData.type === 'direct' ? 'text-indigo-600' : 'text-slate-400'" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                    <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M16 7a4 4 0 11-8 0 4 4 0 018 0zM12 14a7 7 0 00-7 7h14a7 7 0 00-7-7z" />
                  </svg>
                  <p class="text-sm font-semibold" :class="formData.type === 'direct' ? 'text-indigo-700' : 'text-slate-600'">一对一对话</p>
                  <p class="text-xs mt-1" :class="formData.type === 'direct' ? 'text-indigo-400' : 'text-slate-400'">与单个 Agent 对话</p>
                </button>
                <button @click="formData.type = 'group'" :class="['p-4 rounded-xl border-2 transition-all text-center', formData.type === 'group' ? 'border-indigo-600 bg-indigo-50 shadow-sm' : 'border-slate-200 hover:border-slate-300']">
                  <svg class="w-8 h-8 mx-auto mb-2" :class="formData.type === 'group' ? 'text-indigo-600' : 'text-slate-400'" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                    <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M17 20h5v-2a3 3 0 00-5.356-1.857M17 20H7m10 0v-2c0-.656-.126-1.283-.356-1.857M7 20H2v-2a3 3 0 015.356-1.857M7 20v-2c0-.656.126-1.283.356-1.857m0 0a5.002 5.002 0 019.288 0M15 7a3 3 0 11-6 0 3 3 0 016 0zm6 3a2 2 0 11-4 0 2 2 0 014 0zM7 10a2 2 0 11-4 0 2 2 0 014 0z" />
                  </svg>
                  <p class="text-sm font-semibold" :class="formData.type === 'group' ? 'text-indigo-700' : 'text-slate-600'">群聊协作</p>
                  <p class="text-xs mt-1" :class="formData.type === 'group' ? 'text-indigo-400' : 'text-slate-400'">多个 Agent 协同工作</p>
                </button>
              </div>
            </div>
            <div v-if="formData.type === 'direct'">
              <label class="block text-sm font-semibold text-slate-700 mb-2">选择 Agent</label>
              <select v-model="formData.selectedAgentId"
                class="w-full px-4 py-3 rounded-xl border border-slate-200 focus:border-indigo-500 focus:ring-2 focus:ring-indigo-200 outline-none transition-all text-sm text-slate-700 bg-white">
                <option value="" disabled>请选择 Agent</option>
                <option v-for="agent in agents" :key="agent.id" :value="agent.id">
                  {{ agent.name }} — {{ agent.type === 'claude_code' ? 'Claude Code' : agent.type === 'codex' ? 'Codex' : agent.type }}
                </option>
              </select>
              <p v-if="errors.agent" class="text-red-500 text-xs mt-1">{{ errors.agent }}</p>
            </div>
            <div v-else>
              <label class="block text-sm font-semibold text-slate-700 mb-3">
                选择参与 Agent <span class="text-slate-400 font-normal text-xs ml-1">(已选 {{ formData.selectedAgentIds.length }} 个)</span>
              </label>
              <div class="space-y-2 max-h-48 overflow-y-auto">
                <label v-for="agent in agents" :key="agent.id" :class="['flex items-center gap-3 p-3 rounded-xl border-2 cursor-pointer transition-all', formData.selectedAgentIds.includes(agent.id) ? 'border-indigo-400 bg-indigo-50' : 'border-slate-100 hover:border-slate-200 bg-white']">
                  <input type="checkbox" :checked="formData.selectedAgentIds.includes(agent.id)" @change="toggleAgent(agent.id)" class="w-4 h-4 rounded accent-indigo-600" />
                  <div class="flex-1">
                    <div class="text-sm font-semibold text-slate-700">{{ agent.name }}</div>
                    <div class="text-xs text-slate-400">{{ agent.type === 'claude_code' ? 'Claude Code' : agent.type === 'codex' ? 'Codex' : agent.type }}</div>
                  </div>
                </label>
              </div>
              <p v-if="errors.agent" class="text-red-500 text-xs mt-1">{{ errors.agent }}</p>
            </div>
          </div>
          <div class="bg-slate-50 px-8 py-4 flex gap-3 border-t border-slate-200">
            <button @click="closeModal" class="flex-1 px-4 py-2.5 rounded-xl border border-slate-300 text-slate-700 font-medium hover:bg-slate-100 transition-colors">取消</button>
            <button @click="handleCreate" class="flex-1 px-4 py-2.5 rounded-xl text-white font-medium hover:shadow-lg transition-all" :style="{ background: `linear-gradient(to right, var(--accent-start), var(--accent-end))`, boxShadow: `0 4px 6px -1px color-mix(in srgb, var(--accent-start) 30%, transparent)` }">创建会话</button>
          </div>
        </div>
      </div>
    </Transition>
  </Teleport>
</template>

<script setup lang="ts">
import { reactive } from 'vue'
import { storeToRefs } from 'pinia'
import { useChatStore } from '../../stores/chat'

interface Props { isOpen: boolean }
interface Emits {
  (e: 'close'): void
  (e: 'create', data: { title: string; type: string; agentIds: string[] }): void
}

defineProps<Props>()
const emit = defineEmits<Emits>()
const chatStore = useChatStore()
const { agents } = storeToRefs(chatStore)

const formData = reactive({
  title: '',
  type: 'direct' as 'direct' | 'group',
  selectedAgentId: '',
  selectedAgentIds: [] as string[],
})
const errors = reactive({ title: '', agent: '' })

const toggleAgent = (agentId: string) => {
  const idx = formData.selectedAgentIds.indexOf(agentId)
  idx >= 0 ? formData.selectedAgentIds.splice(idx, 1) : formData.selectedAgentIds.push(agentId)
}
const resetForm = () => {
  formData.title = ''; formData.type = 'direct'; formData.selectedAgentId = ''; formData.selectedAgentIds = []; errors.title = ''; errors.agent = ''
}
const closeModal = () => { resetForm(); emit('close') }
const handleCreate = () => {
  errors.title = ''; errors.agent = ''
  if (!formData.title.trim()) { errors.title = '请输入会话名称'; return }
  if (formData.title.length > 50) { errors.title = '会话名称不能超过50个字符'; return }
  if (formData.type === 'direct' && !formData.selectedAgentId) { errors.agent = '请选择一个 Agent'; return }
  if (formData.type === 'group' && formData.selectedAgentIds.length === 0) { errors.agent = '请至少选择一个 Agent'; return }
  const agentIds = formData.type === 'direct' ? [formData.selectedAgentId] : [...formData.selectedAgentIds]
  emit('create', { title: formData.title.trim(), type: formData.type, agentIds })
  resetForm()
}
</script>

<style scoped>
/* 主题色覆盖 */
.from-indigo-600 { --tw-gradient-from: var(--accent-start) !important; }
.to-purple-600 { --tw-gradient-to: var(--accent-end) !important; }
.text-indigo-100 { color: color-mix(in srgb, var(--accent-start) 30%, white) !important; }
.text-indigo-600 { color: color-mix(in srgb, var(--accent-start) 80%, #475569) !important; }
.text-indigo-700 { color: color-mix(in srgb, var(--accent-start) 90%, #334155) !important; }
.text-indigo-400 { color: color-mix(in srgb, var(--accent-start) 60%, #94a3b8) !important; }
.bg-indigo-50 { background-color: color-mix(in srgb, var(--accent-start) 10%, white) !important; }
.border-indigo-600 { border-color: var(--accent-start) !important; }
.border-indigo-400 { border-color: color-mix(in srgb, var(--accent-start) 60%, #cbd5e1) !important; }
.accent-indigo-600 { accent-color: var(--accent-start) !important; }

.modal-fade-enter-active, .modal-fade-leave-active { transition: opacity 0.3s ease; }
.modal-fade-enter-from, .modal-fade-leave-to { opacity: 0; }
.animate-in { animation: slideIn 0.3s ease-out; }
@keyframes slideIn { from { opacity: 0; transform: scale(0.95); } to { opacity: 1; transform: scale(1); } }
</style>
