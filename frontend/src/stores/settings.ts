/**
 * Settings Store — 主题设置（Pinia）
 *
 * 职责：管理界面颜色主题，持久化到 localStorage，通过 CSS 变量驱动全局配色。
 */

import { defineStore } from 'pinia'
import { ref, computed, watch } from 'vue'

interface ThemeColors {
  sidebarStart: string
  sidebarEnd: string
  accentStart: string
  accentEnd: string
  accentLight: string
}

interface Theme {
  id: string
  name: string
  colors: ThemeColors
}

const THEMES: Theme[] = [
  {
    id: 'modern',
    name: '现代靛紫',
    colors: {
      sidebarStart: '#1e1b4b',
      sidebarEnd: '#312e81',
      accentStart: '#6366f1',
      accentEnd: '#8b5cf6',
      accentLight: '#eef2ff',
    },
  },
  {
    id: 'ocean',
    name: '深海蓝',
    colors: {
      sidebarStart: '#0c1929',
      sidebarEnd: '#1a365d',
      accentStart: '#3b82f6',
      accentEnd: '#06b6d4',
      accentLight: '#eff6ff',
    },
  },
  {
    id: 'forest',
    name: '翠竹绿',
    colors: {
      sidebarStart: '#052e16',
      sidebarEnd: '#14532d',
      accentStart: '#10b981',
      accentEnd: '#34d399',
      accentLight: '#ecfdf5',
    },
  },
  {
    id: 'sunset',
    name: '日落橙',
    colors: {
      sidebarStart: '#431407',
      sidebarEnd: '#7c2d12',
      accentStart: '#f97316',
      accentEnd: '#ef4444',
      accentLight: '#fff7ed',
    },
  },
]

const STORAGE_KEY = 'agenthub_theme'

function loadStoredTheme(): string {
  return localStorage.getItem(STORAGE_KEY) || 'modern'
}

function applyCssVars(colors: ThemeColors) {
  const root = document.documentElement
  root.style.setProperty('--sidebar-start', colors.sidebarStart)
  root.style.setProperty('--sidebar-end', colors.sidebarEnd)
  root.style.setProperty('--accent-start', colors.accentStart)
  root.style.setProperty('--accent-end', colors.accentEnd)
  root.style.setProperty('--accent-light', colors.accentLight)
}

export const useSettingsStore = defineStore('settings', () => {
  const currentThemeId = ref<string>(loadStoredTheme())

  const themes = computed(() => THEMES)
  const currentTheme = computed(() => THEMES.find(t => t.id === currentThemeId.value) || THEMES[0])
  const colors = computed(() => currentTheme.value.colors)

  // 初始化时应用 CSS 变量
  applyCssVars(currentTheme.value.colors)

  // 切换主题时持久化 + 应用
  watch(currentThemeId, (id) => {
    const theme = THEMES.find(t => t.id === id)
    if (theme) {
      localStorage.setItem(STORAGE_KEY, id)
      applyCssVars(theme.colors)
    }
  })

  function setTheme(id: string) {
    if (THEMES.some(t => t.id === id)) {
      currentThemeId.value = id
    }
  }

  return { currentThemeId, themes, currentTheme, colors, setTheme }
})
