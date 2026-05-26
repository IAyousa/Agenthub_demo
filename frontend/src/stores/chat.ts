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
  const currentConversationId = ref<string>('orchestrator')
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

  return {
    currentConversationId,
    conversations,
    currentMessages,
    currentTitle,
    isLoading,
    currentArtifact,
    isArtifactVisible,
    mobileView,
    currentView,
    officeMembers,
    availableUsersToInvite,
    addMessage,
    selectConversation,
    showArtifact,
    closeArtifact,
    inviteMember,
    removeMember
  }
})
