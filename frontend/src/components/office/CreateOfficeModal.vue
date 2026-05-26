<template>
  <Teleport to="body">
    <Transition name="modal-fade">
      <div v-if="isOpen" class="fixed inset-0 z-50 flex items-center justify-center bg-black/40 backdrop-blur-sm">
        <div class="bg-white rounded-3xl shadow-2xl w-full max-w-md mx-4 overflow-hidden animate-in fade-in zoom-in-95 duration-300">
          <!-- Header -->
          <div class="bg-gradient-to-r from-indigo-600 to-purple-600 px-8 py-6">
            <div class="flex items-center justify-between">
              <h2 class="text-2xl font-bold text-white">创建新办公室</h2>
              <button
                @click="closeModal"
                class="text-white/80 hover:text-white transition-colors"
              >
                <svg class="w-6 h-6" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                  <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M6 18L18 6M6 6l12 12" />
                </svg>
              </button>
            </div>
            <p class="text-indigo-100 text-sm mt-2">为你的团队创建一个协作空间</p>
          </div>

          <!-- Content -->
          <div class="px-8 py-6 space-y-5">
            <!-- Office Name -->
            <div>
              <label class="block text-sm font-semibold text-slate-700 mb-2">办公室名称</label>
              <input
                v-model="formData.name"
                type="text"
                placeholder="例如：产品团队办公室"
                class="w-full px-4 py-3 rounded-xl border border-slate-200 focus:border-indigo-500 focus:ring-2 focus:ring-indigo-200 outline-none transition-all"
              />
              <p v-if="errors.name" class="text-red-500 text-xs mt-1">{{ errors.name }}</p>
            </div>

            <!-- Description -->
            <div>
              <label class="block text-sm font-semibold text-slate-700 mb-2">描述（可选）</label>
              <textarea
                v-model="formData.description"
                placeholder="描述这个办公室的用途..."
                rows="3"
                class="w-full px-4 py-3 rounded-xl border border-slate-200 focus:border-indigo-500 focus:ring-2 focus:ring-indigo-200 outline-none transition-all resize-none"
              />
            </div>

            <!-- Max Members -->
            <div>
              <label class="block text-sm font-semibold text-slate-700 mb-2">最大成员数</label>
              <div class="flex items-center gap-4">
                <input
                  v-model.number="formData.maxMembers"
                  type="range"
                  min="2"
                  max="20"
                  class="flex-1 h-2 bg-slate-200 rounded-lg appearance-none cursor-pointer accent-indigo-600"
                />
                <span class="text-lg font-semibold text-indigo-600 min-w-12 text-right">{{ formData.maxMembers }}</span>
              </div>
            </div>

            <!-- Theme Selection -->
            <div>
              <label class="block text-sm font-semibold text-slate-700 mb-3">选择主题</label>
              <div class="grid grid-cols-4 gap-3">
                <button
                  v-for="theme in themes"
                  :key="theme.id"
                  @click="formData.theme = theme.id"
                  :class="[
                    'p-3 rounded-xl border-2 transition-all',
                    formData.theme === theme.id
                      ? 'border-indigo-600 bg-indigo-50'
                      : 'border-slate-200 hover:border-slate-300'
                  ]"
                >
                  <div :class="['w-full h-12 rounded-lg', theme.bgClass]"></div>
                  <p class="text-xs font-medium text-slate-600 mt-2 text-center">{{ theme.name }}</p>
                </button>
              </div>
            </div>
          </div>

          <!-- Footer -->
          <div class="bg-slate-50 px-8 py-4 flex gap-3 border-t border-slate-200">
            <button
              @click="closeModal"
              class="flex-1 px-4 py-2.5 rounded-xl border border-slate-300 text-slate-700 font-medium hover:bg-slate-100 transition-colors"
            >
              取消
            </button>
            <button
              @click="createOffice"
              :disabled="isLoading"
              class="flex-1 px-4 py-2.5 rounded-xl bg-gradient-to-r from-indigo-600 to-purple-600 text-white font-medium hover:shadow-lg hover:shadow-indigo-500/30 disabled:opacity-50 disabled:cursor-not-allowed transition-all"
            >
              <span v-if="!isLoading">创建办公室</span>
              <span v-else class="flex items-center justify-center gap-2">
                <svg class="w-4 h-4 animate-spin" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                  <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M12 4v16m8-8H4" />
                </svg>
                创建中...
              </span>
            </button>
          </div>
        </div>
      </div>
    </Transition>
  </Teleport>
</template>

<script setup lang="ts">
import { ref, reactive } from 'vue'

interface Props {
  isOpen: boolean
}

interface Emits {
  (e: 'close'): void
  (e: 'create', data: { name: string; description: string; maxMembers: number; theme: string }): void
}

defineProps<Props>()
const emit = defineEmits<Emits>()

const isLoading = ref(false)
const formData = reactive({
  name: '',
  description: '',
  maxMembers: 8,
  theme: 'modern'
})

const errors = reactive({
  name: ''
})

const themes = [
  { id: 'modern', name: '现代', bgClass: 'bg-gradient-to-br from-indigo-500 to-purple-600' },
  { id: 'ocean', name: '海洋', bgClass: 'bg-gradient-to-br from-blue-400 to-cyan-500' },
  { id: 'forest', name: '森林', bgClass: 'bg-gradient-to-br from-green-400 to-emerald-600' },
  { id: 'sunset', name: '日落', bgClass: 'bg-gradient-to-br from-orange-400 to-red-500' }
]

const closeModal = () => {
  resetForm()
  emit('close')
}

const resetForm = () => {
  formData.name = ''
  formData.description = ''
  formData.maxMembers = 8
  formData.theme = 'modern'
  errors.name = ''
}

const createOffice = async () => {
  errors.name = ''
  
  if (!formData.name.trim()) {
    errors.name = '请输入办公室名称'
    return
  }

  if (formData.name.length > 50) {
    errors.name = '办公室名称不能超过50个字符'
    return
  }

  isLoading.value = true
  
  // 模拟API调用
  await new Promise(resolve => setTimeout(resolve, 800))
  
  emit('create', {
    name: formData.name,
    description: formData.description,
    maxMembers: formData.maxMembers,
    theme: formData.theme
  })
  
  isLoading.value = false
  resetForm()
}
</script>

<style scoped>
.modal-fade-enter-active,
.modal-fade-leave-active {
  transition: opacity 0.3s ease;
}

.modal-fade-enter-from,
.modal-fade-leave-to {
  opacity: 0;
}

.animate-in {
  animation: slideIn 0.3s ease-out;
}

@keyframes slideIn {
  from {
    opacity: 0;
    transform: scale(0.95);
  }
  to {
    opacity: 1;
    transform: scale(1);
  }
}
</style>
