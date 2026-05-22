import { defineStore } from 'pinia'
import { ref, computed } from 'vue'

export interface Message {
  id: string
  role: 'user' | 'assistant' | 'system'
  type: 'text' | 'code' | 'diff' | 'artifact_preview'
  content: string
  created_at: string
  metadata?: Record<string, any>
}

export interface Conversation {
  id: string
  title: string
  messages: Message[]
}

export const useChatStore = defineStore('chat', () => {
  const currentConversationId = ref<string>('orchestrator')
  const mobileView = ref<'list' | 'chat'>('list')
  const conversations = ref<Record<string, Conversation>>({
    'orchestrator': {
      id: 'orchestrator',
      title: 'Orchestrator Agent',
      messages: [
        {
          id: 'welcome',
          role: 'assistant',
          type: 'text',
          content: '你好！我是 Multi-Agent Orchestrator。我可以协调多个专业 Agent 帮助你完成任务。',
          created_at: new Date().toISOString()
        }
      ]
    },
    'coder': {
      id: 'coder',
      title: '代码助手 (Coder)',
      messages: [
        {
          id: 'welcome-coder',
          role: 'assistant',
          type: 'text',
          content: '你好！我是代码专家，有什么编程问题可以问我。',
          created_at: new Date().toISOString()
        },
        {
          id: 'example-code',
          role: 'assistant',
          type: 'code',
          content: 'export function hello() {\n  console.log("Hello from Monaco!");\n}',
          metadata: {
            language: 'typescript'
          },
          created_at: new Date().toISOString()
        },
        {
          id: 'example-artifact',
          role: 'assistant',
          type: 'artifact_preview',
          content: '<html>\n<body style="display:flex;justify-content:center;align-items:center;height:100vh;margin:0;background:linear-gradient(135deg, #667eea 0%, #764ba2 100%);color:white;font-family:sans-serif;">\n  <div style="text-align:center;padding:40px;background:rgba(255,255,255,0.1);backdrop-filter:blur(10px);border-radius:20px;box-shadow:0 10px 30px rgba(0,0,0,0.2);">\n    <h1 style="margin:0;font-size:3em;">Hello Artifact!</h1>\n    <p style="opacity:0.8;margin-top:10px;">This is a live preview rendered in an iframe.</p>\n    <button onclick="alert(\'Clicked!\')" style="margin-top:20px;padding:10px 25px;border:none;border-radius:50px;background:white;color:#764ba2;font-weight:bold;cursor:pointer;transition:transform 0.2s;" onmouseover="this.style.transform=\'scale(1.05)\'" onmouseout="this.style.transform=\'scale(1)\'">Interact With Me</button>\n  </div>\n</body>\n</html>',
          metadata: {
            title: 'Welcome Card',
            language: 'html'
          },
          created_at: new Date().toISOString()
        }
      ]
    },
    'designer': {
      id: 'designer',
      title: '设计专家 (Designer)',
      messages: [
        {
          id: 'welcome-designer',
          role: 'assistant',
          type: 'text',
          content: '你好！我是设计专家，我可以帮你优化 UI/UX。',
          created_at: new Date().toISOString()
        }
      ]
    }
  })
  const isLoading = ref(false)

  // Artifact State
  const currentArtifact = ref<{
    id: string
    title: string
    code: string
    language: string
  } | null>(null)
  const isArtifactVisible = ref(false)

  const showArtifact = (artifact: { id: string; title: string; code: string; language: string }) => {
    currentArtifact.value = artifact
    isArtifactVisible.value = true
  }

  const closeArtifact = () => {
    isArtifactVisible.value = false
  }

  const currentMessages = computed(() => {
    return conversations.value[currentConversationId.value]?.messages || []
  })

  const currentTitle = computed(() => {
    return conversations.value[currentConversationId.value]?.title || 'Chat'
  })

  const addMessage = (message: Message) => {
    if (conversations.value[currentConversationId.value]) {
      conversations.value[currentConversationId.value].messages.push(message)
    }
  }

  const selectConversation = (id: string) => {
    if (currentConversationId.value !== id) {
      currentConversationId.value = id
      closeArtifact() // Close artifact window when switching agents
    }
  }

  return {
    currentConversationId,
    conversations,
    currentMessages,
    currentTitle,
    isLoading,
    currentArtifact,
    isArtifactVisible,
    mobileView,
    addMessage,
    selectConversation,
    showArtifact,
    closeArtifact
  }
})
