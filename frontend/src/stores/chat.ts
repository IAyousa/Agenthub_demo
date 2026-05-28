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

export interface ConversationSummary {
  id: string
  title: string
  type: 'direct' | 'group'
  lastMessage: string
  updatedAt: string
  agentNames: string[]
  isArchived?: boolean
}

export interface OfficeMember {
  id: string
  name: string
  avatar: string
  role: 'owner' | 'admin' | 'member'
  status: 'online' | 'away' | 'offline'
  lastActive?: string
  seatIndex?: number
  isInviting?: boolean
  isRemoving?: boolean
}

export interface Office {
  id: string
  name: string
  description?: string
  theme: string
  maxMembers: number
  members: OfficeMember[]
  availableUsers: OfficeMember[]
  createdAt: string
  ownerId: string
}

export type AppView = 'chat' | 'office'

export const useChatStore = defineStore('chat', () => {
  const currentConversationId = ref<string>('conv_frontend_001')
  const mobileView = ref<'list' | 'chat'>('list')
  const currentView = ref<AppView>('chat')
  
  // 办公室管理
  const offices = ref<Office[]>([
    {
      id: 'office-1',
      name: '默认办公室',
      description: '团队协作空间',
      theme: 'modern',
      maxMembers: 8,
      createdAt: new Date().toISOString(),
      ownerId: '1',
      members: [
        { id: '1', name: '你', avatar: 'https://api.dicebear.com/7.x/avataaars/svg?seed=Felix', role: 'owner', status: 'online', lastActive: '刚刚' },
        { id: '2', name: '张小明', avatar: 'https://api.dicebear.com/7.x/avataaars/svg?seed=xiaoming', role: 'admin', status: 'online', lastActive: '2分钟前', seatIndex: 0 },
        { id: '3', name: '李小红', avatar: 'https://api.dicebear.com/7.x/avataaars/svg?seed=xiaohong', role: 'member', status: 'away', lastActive: '15分钟前', seatIndex: 1 },
        { id: '4', name: '王大伟', avatar: 'https://api.dicebear.com/7.x/avataaars/svg?seed=dawei', role: 'member', status: 'offline', lastActive: '1小时前', seatIndex: 2 },
      ],
      availableUsers: [
        { id: 'u100', name: '陈静静', avatar: 'https://api.dicebear.com/7.x/avataaars/svg?seed=jingjing', role: 'member', status: 'online' },
        { id: 'u101', name: '刘先生', avatar: 'https://api.dicebear.com/7.x/avataaars/svg?seed=liu', role: 'member', status: 'online' },
        { id: 'u102', name: '产品经理', avatar: 'https://api.dicebear.com/7.x/avataaars/svg?seed=pm', role: 'member', status: 'away' },
      ]
    }
  ])
  
  const currentOfficeId = ref<string>('office-1')
  
  const currentOffice = computed(() => {
    return offices.value.find(o => o.id === currentOfficeId.value)
  })
  
  const officeMembers = computed(() => {
    return currentOffice.value?.members || []
  })
  
  const availableUsersToInvite = computed(() => {
    return currentOffice.value?.availableUsers || []
  })
  
  // 切换办公室
  const switchOffice = (officeId: string) => {
    if (offices.value.find(o => o.id === officeId)) {
      currentOfficeId.value = officeId
    }
  }
  
  // 创建新办公室
  const createOffice = (data: { name: string; description: string; maxMembers: number; theme: string }) => {
    const newOffice: Office = {
      id: `office-${Date.now()}`,
      name: data.name,
      description: data.description,
      theme: data.theme,
      maxMembers: data.maxMembers,
      createdAt: new Date().toISOString(),
      ownerId: '1',
      members: [
        { id: '1', name: '你', avatar: 'https://api.dicebear.com/7.x/avataaars/svg?seed=Felix', role: 'owner', status: 'online', lastActive: '刚刚' }
      ],
      availableUsers: [
        { id: 'u100', name: '陈静静', avatar: 'https://api.dicebear.com/7.x/avataaars/svg?seed=jingjing', role: 'member', status: 'online' },
        { id: 'u101', name: '刘先生', avatar: 'https://api.dicebear.com/7.x/avataaars/svg?seed=liu', role: 'member', status: 'online' },
        { id: 'u102', name: '产品经理', avatar: 'https://api.dicebear.com/7.x/avataaars/svg?seed=pm', role: 'member', status: 'away' },
        { id: 'u103', name: '数据分析师', avatar: 'https://api.dicebear.com/7.x/avataaars/svg?seed=data', role: 'member', status: 'offline' }
      ]
    }
    offices.value.push(newOffice)
    currentOfficeId.value = newOffice.id
    return newOffice
  }
  
  // 删除办公室
  const deleteOffice = (officeId: string) => {
    const index = offices.value.findIndex(o => o.id === officeId)
    if (index > -1) {
      offices.value.splice(index, 1)
      if (currentOfficeId.value === officeId && offices.value.length > 0) {
        currentOfficeId.value = offices.value[0].id
      }
    }
  }
  
  // 找到第一个空位seatIndex
  const findEmptySeat = (): number => {
    const used = officeMembers.value.filter(m => m.seatIndex !== undefined).map(m => m.seatIndex!)
    for (let i = 0; i < 8; i++) {
      if (!used.includes(i)) return i
    }
    return 0
  }

  const inviteMember = (userId: string, targetSeatIdx?: number) => {
    if (!currentOffice.value) return
    const user = currentOffice.value.availableUsers.find(u => u.id === userId)
    if (user) {
      const emptySeat = targetSeatIdx !== undefined ? targetSeatIdx : findEmptySeat()
      currentOffice.value.members.push({ ...user, lastActive: '刚刚', seatIndex: emptySeat })
      currentOffice.value.availableUsers = currentOffice.value.availableUsers.filter(u => u.id !== userId)
    }
  }

  const removeMember = (memberId: string) => {
    if (!currentOffice.value) return
    const member = currentOffice.value.members.find(m => m.id === memberId)
    if (member && member.role !== 'owner') {
      currentOffice.value.members = currentOffice.value.members.filter(m => m.id !== memberId)
      currentOffice.value.availableUsers.push({ ...member, isInviting: false, isRemoving: false })
    }
  }

  // 聊天管理
  const conversations = ref<Record<string, Conversation>>({
    'conv_frontend_001': {
      id: 'conv_frontend_001',
      title: '前端博客开发',
      messages: [
        {
          id: 'welcome-frontend',
          role: 'assistant',
          type: 'text',
          content: '你好！我是 Claude Code，我会协助你完成前端博客的开发任务。让我们开始吧！',
          created_at: new Date().toISOString()
        }
      ]
    },
    'conv_backend_001': {
      id: 'conv_backend_001',
      title: '后端接口重构',
      messages: [
        {
          id: 'welcome-backend',
          role: 'assistant',
          type: 'text',
          content: '你好！我是 Codex，我会协助你重构后端接口。请告诉我需要重构哪些接口？',
          created_at: new Date().toISOString()
        }
      ]
    },
    'conv_review_001': {
      id: 'conv_review_001',
      title: '代码审查',
      messages: [
        {
          id: 'welcome-review',
          role: 'assistant',
          type: 'text',
          content: '你好！代码审查已准备就绪。请提交需要审查的代码。',
          created_at: new Date().toISOString()
        }
      ]
    }
  })
  const isLoading = ref(false)

  const conversationList = ref<ConversationSummary[]>([
    {
      id: 'conv_frontend_001',
      title: '前端博客开发',
      type: 'direct',
      lastMessage: '已生成 App.jsx 组件',
      updatedAt: new Date(Date.now() - 3600000).toISOString(),
      agentNames: ['Claude Code'],
    },
    {
      id: 'conv_backend_001',
      title: '后端接口重构',
      type: 'direct',
      lastMessage: '完成了 User API 和 Message API 的重构',
      updatedAt: new Date(Date.now() - 7200000).toISOString(),
      agentNames: ['Codex'],
    },
    {
      id: 'conv_review_001',
      title: '代码审查',
      type: 'direct',
      lastMessage: '发现 3 处潜在性能问题，建议优化',
      updatedAt: new Date(Date.now() - 86400000).toISOString(),
      agentNames: ['Claude Code', 'Codex'],
    },
  ])

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
      closeArtifact()
    }
  }

  const createConversation = (title: string) => {
    const id = `conv_${Date.now()}`
    const newConv: ConversationSummary = {
      id,
      title,
      type: 'direct',
      lastMessage: '新会话已创建',
      updatedAt: new Date().toISOString(),
      agentNames: [],
    }
    conversationList.value.unshift(newConv)
    conversations.value[id] = {
      id,
      title,
      messages: [
        {
          id: `welcome-${id}`,
          role: 'assistant',
          type: 'text',
          content: '新会话已创建，你可以选择参与的 Agent 并开始对话。',
          created_at: new Date().toISOString()
        }
      ]
    }
    currentConversationId.value = id
    mobileView.value = 'chat'
  }

  return {
    currentConversationId,
    conversations,
    conversationList,
    currentMessages,
    currentTitle,
    isLoading,
    currentArtifact,
    isArtifactVisible,
    mobileView,
    currentView,
    offices,
    currentOfficeId,
    currentOffice,
    officeMembers,
    availableUsersToInvite,
    switchOffice,
    createOffice,
    deleteOffice,
    addMessage,
    selectConversation,
    createConversation,
    showArtifact,
    closeArtifact,
    inviteMember,
    removeMember
  }
})
