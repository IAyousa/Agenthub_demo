<template>
  <div class="h-full w-full overflow-hidden bg-gradient-to-br from-slate-50 via-blue-50 to-indigo-50 relative">
    <!-- 精致的顶部导航栏 -->
    <header class="absolute top-0 left-0 right-0 z-20 h-24 bg-white/80 backdrop-blur-xl border-b border-slate-200/50 px-8 flex flex-col justify-between shadow-sm">
      <!-- 第一行：标题和操作按钮 -->
      <div class="flex items-center justify-between pt-4">
        <div class="flex items-center gap-3">
          <div class="w-10 h-10 rounded-xl bg-gradient-to-br from-indigo-500 to-purple-600 flex items-center justify-center">
            <svg class="w-6 h-6 text-white" fill="none" stroke="currentColor" viewBox="0 0 24 24">
              <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M19 21V5a2 2 0 00-2-2H7a2 2 0 00-2 2v16m14 0h2m-2 0h-5m-9 0H3m2 0h5M9 7h1m-1 4h1m4-4h1m-1 4h1m-5 10v-5a1 1 0 011-1h2a1 1 0 011 1v5m-4 0h4" />
            </svg>
          </div>
          <div>
            <h1 class="text-xl font-bold bg-gradient-to-r from-indigo-600 to-purple-600 bg-clip-text text-transparent">办公室</h1>
            <p class="text-xs text-slate-500">{{ currentOffice?.name }}</p>
          </div>
        </div>
        
        <div class="flex items-center gap-3">
          <div class="flex items-center gap-2 px-3 py-1.5 bg-indigo-50 rounded-lg">
            <svg class="w-4 h-4 text-indigo-600" fill="currentColor" viewBox="0 0 20 20">
              <path d="M10 9a3 3 0 100-6 3 3 0 000 6zm-7 9a7 7 0 1114 0H3z" />
            </svg>
            <span class="text-sm font-semibold text-indigo-600">{{ totalNumber }} 人</span>
          </div>
          
          <button
            @click="showCreateModal = true"
            class="px-4 py-2 rounded-lg bg-gradient-to-r from-indigo-600 to-purple-600 text-white text-sm font-semibold hover:shadow-lg hover:shadow-indigo-500/30 transition-all duration-200 flex items-center gap-2"
          >
            <svg class="w-4 h-4" fill="none" stroke="currentColor" viewBox="0 0 24 24">
              <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M12 4v16m8-8H4" />
            </svg>
            新建
          </button>
          
          <button
            class="p-2 rounded-lg hover:bg-slate-100 transition-colors"
            title="设置"
          >
            <svg class="w-5 h-5 text-slate-600" fill="none" stroke="currentColor" viewBox="0 0 24 24">
              <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M10.325 4.317c.426-1.756 2.924-1.756 3.35 0a1.724 1.724 0 002.573 1.066c1.543-.94 3.31.826 2.37 2.37a1.724 1.724 0 001.065 2.572c1.756.426 1.756 2.924 0 3.35a1.724 1.724 0 00-1.066 2.573c.94 1.543-.826 3.31-2.37 2.37a1.724 1.724 0 00-2.572 1.065c-.426 1.756-2.924 1.756-3.35 0a1.724 1.724 0 00-2.573-1.066c-1.543.94-3.31-.826-2.37-2.37a1.724 1.724 0 00-1.065-2.572c-1.756-.426-1.756-2.924 0-3.35a1.724 1.724 0 001.066-2.573c-.94-1.543.826-3.31 2.37-2.37.996.608 2.296.07 2.572-1.065z" />
              <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M15 12a3 3 0 11-6 0 3 3 0 016 0z" />
            </svg>
          </button>
        </div>
      </div>
      
      <!-- 第二行：办公室列表选项卡 -->
      <div class="flex items-center gap-2 pb-3 overflow-x-auto">
        <button
          v-for="office in offices"
          :key="office.id"
          @click="switchOffice(office.id)"
          :class="[
            'px-4 py-2 rounded-lg font-medium text-sm whitespace-nowrap transition-all duration-200 flex items-center gap-2',
            currentOfficeId === office.id
              ? 'bg-gradient-to-r from-indigo-600 to-purple-600 text-white shadow-lg shadow-indigo-500/30'
              : 'bg-slate-100 text-slate-700 hover:bg-slate-200'
          ]"
        >
          <span class="w-2 h-2 rounded-full" :class="currentOfficeId === office.id ? 'bg-white' : 'bg-slate-400'"></span>
          {{ office.name }}
          <span class="text-xs opacity-75">({{ office.members.length }})</span>
        </button>
      </div>
    </header>

    <div class="w-full h-full pt-24 relative">
      <svg viewBox="0 0 900 550" class="w-full h-full">
        <!-- 背景渐变定义 -->
        <defs>
          <linearGradient id="floorGrad" x1="0%" y1="0%" x2="0%" y2="100%">
            <stop offset="0%" style="stop-color:#f8fafc;stop-opacity:1" />
            <stop offset="100%" style="stop-color:#f1f5f9;stop-opacity:1" />
          </linearGradient>
          <radialGradient id="impactGrad">
            <stop offset="0%" style="stop-color:#fb923c;stop-opacity:0.8" />
            <stop offset="100%" style="stop-color:#fb923c;stop-opacity:0" />
          </radialGradient>
          <filter id="softShadow" x="-20%" y="-20%" width="140%" height="140%">
            <feGaussianBlur in="SourceAlpha" stdDeviation="3" />
            <feOffset dx="2" dy="2" result="offsetblur" />
            <feComponentTransfer>
              <feFuncA type="linear" slope="0.2" />
            </feComponentTransfer>
            <feMerge>
              <feMergeNode />
              <feMergeNode in="SourceGraphic" />
            </feMerge>
          </filter>
        </defs>

        <!-- 地面 -->
        <rect x="0" y="0" width="900" height="550" fill="url(#floorGrad)" />
        
        <!-- 装饰：地毯 -->
        <ellipse cx="450" cy="400" rx="400" ry="80" fill="#f1f5f9" stroke="#e2e8f0" stroke-width="1" />
        <ellipse cx="450" cy="400" rx="380" ry="70" fill="#f8fafc" stroke="#e2e8f0" stroke-width="0.5" />

        <!-- 墙壁装饰线 -->
        <g stroke="#cbd5e1" stroke-width="1" stroke-dasharray="8,4" opacity="0.5">
          <line x1="0" y1="180" x2="900" y2="180" />
        </g>

        <!-- 门口形象优化 -->
        <g filter="url(#softShadow)">
          <rect x="820" y="280" width="70" height="180" rx="4" fill="#fff" stroke="#94a3b8" stroke-width="2" />
          <rect x="830" y="290" width="50" height="160" rx="2" fill="#f8fafc" stroke="#e2e8f0" stroke-width="1" />
          <circle cx="838" cy="370" r="4" fill="#64748b" />
        </g>

        <!-- 装饰：绿植 (移到后面) -->
        <g transform="translate(40, 480)" filter="url(#softShadow)">
          <rect x="-15" y="0" width="30" height="35" fill="#94a3b8" />
          <path d="M -20 0 L 20 0 L 25 -10 L -25 -10 Z" fill="#64748b" />
          <ellipse cx="0" cy="-25" rx="20" ry="30" fill="#10b981" />
          <ellipse cx="-10" cy="-35" rx="15" ry="25" fill="#059669" />
          <ellipse cx="10" cy="-30" rx="12" ry="20" fill="#34d399" />
        </g>
        <g transform="translate(860, 480)" filter="url(#softShadow)">
          <rect x="-15" y="0" width="30" height="35" fill="#94a3b8" />
          <path d="M -20 0 L 20 0 L 25 -10 L -25 -10 Z" fill="#64748b" />
          <ellipse cx="0" cy="-30" rx="18" ry="35" fill="#10b981" />
          <ellipse cx="8" cy="-25" rx="12" ry="25" fill="#059669" />
        </g>

        <!-- 1. 渲染椅子 (最底层) -->
        <g 
          v-for="(seat, idx) in allSeats" 
          :key="'chair-' + idx"
          @click="onSeatClick(idx)"
          class="cursor-pointer group"
        >
          <OfficeChair 
            :x="seat.x" 
            :y="seat.y"
          />
          <!-- 增强点击区域 -->
          <rect 
            :x="seat.x - 30" 
            :y="seat.y - 20" 
            width="60" 
            height="70" 
            fill="transparent" 
          />
        </g>

        <!-- 2. 渲染角色 (中间层) -->
        <!-- 群主小人 -->
        <StickFigure 
          role="owner" 
          :transform="`translate(${ownerPos.x}, ${ownerPos.y})`" 
          class="cursor-pointer"
          color="#334155"
          :isKicking="isOwnerKicking"
          :isBack="false"
        />

        <!-- 动态渲染普通成员小人 -->
        <StickFigure 
          v-for="member in nonOwnerMembersWithSeat" 
          :key="'member-' + member.id"
          :role="member.role"
          class="cursor-pointer"
          :transform="getMemberTransformBySeat(member.seatIndex!)"
          @click="onMemberClick(member, $event)"
          color="#4b5563"
          :isShocked="memberShockedState[member.id]"
        />

        <!-- 3. 渲染桌子 (最顶层，实现遮挡，3D 透视风格) -->
        <!-- 主办公桌 (群主位置) -->
        <g filter="url(#softShadow)" pointer-events="none">
          <!-- 桌面 (梯形透视) -->
          <path d="M 320 160 L 580 160 L 620 210 L 280 210 Z" fill="#fff" stroke="#64748b" stroke-width="2.5" />
          <!-- 桌边厚度 -->
          <path d="M 280 210 L 620 210 L 620 220 L 280 220 Z" fill="#e2e8f0" stroke="#64748b" stroke-width="2" />
          
          <!-- 桌上装饰：电脑 (3D 倾斜) -->
          <g transform="translate(450, 165)">
            <rect x="-35" y="-15" width="70" height="40" rx="2" fill="#334155" transform="skewX(-10)" />
            <rect x="-30" y="-10" width="60" height="30" fill="#475569" transform="skewX(-10)" />
            <path d="M -15 25 L 15 25 L 20 30 L -20 30 Z" fill="#334155" />
          </g>
        </g>

        <!-- 普通办公桌 (3D 透视风格) -->
        <g filter="url(#softShadow)" pointer-events="none">
          <!-- 左侧上排桌 -->
          <g transform="translate(50, 240)">
            <path d="M 10 0 L 170 0 L 180 40 L 0 40 Z" fill="#fff" stroke="#94a3b8" stroke-width="2" />
            <path d="M 0 40 L 180 40 L 180 48 L 0 48 Z" fill="#f1f5f9" stroke="#94a3b8" stroke-width="1.5" />
            <!-- 咖啡杯 -->
            <circle cx="150" cy="20" r="5" fill="#fff" stroke="#94a3b8" stroke-width="1.5" />
            <circle cx="150" cy="20" r="3" fill="#92400e" />
          </g>
          <!-- 左侧下排桌 -->
          <g transform="translate(50, 430)">
            <path d="M 10 0 L 170 0 L 180 40 L 0 40 Z" fill="#fff" stroke="#94a3b8" stroke-width="2" />
            <path d="M 0 40 L 180 40 L 180 48 L 0 48 Z" fill="#f1f5f9" stroke="#94a3b8" stroke-width="1.5" />
            <rect x="30" y="10" width="25" height="20" fill="#e2e8f0" rx="1" />
          </g>
          
          <!-- 右侧上排桌 -->
          <g transform="translate(670, 240)">
            <path d="M 10 0 L 170 0 L 180 40 L 0 40 Z" fill="#fff" stroke="#94a3b8" stroke-width="2" />
            <path d="M 0 40 L 180 40 L 180 48 L 0 48 Z" fill="#f1f5f9" stroke="#94a3b8" stroke-width="1.5" />
          </g>
          <!-- 右侧下排桌 -->
          <g transform="translate(670, 430)">
            <path d="M 10 0 L 170 0 L 180 40 L 0 40 Z" fill="#fff" stroke="#94a3b8" stroke-width="2" />
            <path d="M 0 40 L 180 40 L 180 48 L 0 48 Z" fill="#f1f5f9" stroke="#94a3b8" stroke-width="1.5" />
          </g>
        </g>

        <!-- 踢人冲击波效果 -->
        <circle id="kick-impact" cx="0" cy="0" r="30" fill="url(#impactGrad)" style="pointer-events: none; opacity: 0;" />

        <!-- 正在飞出去的人物动画 (放在桌子上面) -->
        <g v-if="showFlyingMan">
          <StickFigure 
            :role="flyingMemberRole"
            :transform="flyingManTransform"
            color="#f97316"
            :isBack="false"
          />
          <text 
            :x="flyState.x - 20" 
            :y="flyState.y - 40" 
            font-size="20"
            :style="{ opacity: flyState.opacity }"
          >💨</text>
        </g>

        <!-- 正在走进来的人物动画 -->
        <StickFigure 
          v-if="showWalkingMan" 
          role="member"
          :transform="walkingManTransform"
          :isWalking="true"
          color="#10b981"
          :isBack="false"
        />
      </svg>
    </div>

    <!-- 人物信息小卡片 -->
    <Transition name="pop-fade">
      <div v-if="showMemberInfoPanel && clickedMember" class="absolute z-50 bg-white/60 backdrop-blur-xl rounded-2xl shadow-2xl p-4 w-48 border border-white/50" :style="memberInfoPanelStyle">
        <div class="flex items-center gap-2 mb-3">
          <img :src="clickedMember.avatar" class="w-10 h-10 rounded-xl" />
          <div>
            <div class="font-semibold text-slate-800 text-sm">{{ clickedMember.name }}</div>
            <div class="text-xs text-slate-500">
              {{ clickedMember.role === 'admin' ? '管理员' : '普通成员' }}
            </div>
          </div>
        </div>
        <button 
          @click="doKickNow(clickedMember.id)"
          class="w-full py-2 rounded-xl bg-red-400/80 text-white text-xs font-semibold hover:bg-red-400 transition-colors"
        >
          踢出办公室
        </button>
      </div>
    </Transition>

    <!-- 空位邀请小列表 -->
    <Transition name="pop-fade">
      <div v-if="showInvitePanel && clickSeatIndex !== -1" class="absolute z-50 bg-white/50 backdrop-blur-md rounded-2xl shadow-xl p-3 w-56 border border-white/40" :style="invitePanelStyle">
        <div class="text-xs font-bold text-slate-700 mb-2">邀请新成员入座</div>
        <div class="space-y-2 max-h-52 overflow-y-auto">
          <div 
            v-for="guest in allGuests" 
            :key="guest.id"
            @click="doInviteToSeat(guest.id)"
            class="flex items-center p-2 bg-white/40 rounded-xl hover:bg-indigo-50/70 cursor-pointer transition-colors"
          >
            <img :src="guest.avatar" class="w-7 h-7 rounded-lg mr-2" />
            <div class="flex-1">
              <div class="font-medium text-slate-700 text-xs">{{ guest.name }}</div>
            </div>
            <div class="text-xs text-indigo-600">邀请</div>
          </div>
        </div>
      </div>
    </Transition>

    <div 
      v-if="showMemberInfoPanel || showInvitePanel" 
      @click="closeAllPanels"
      class="absolute inset-0 z-40"
    ></div>

    <!-- 新建办公室对话框 -->
    <CreateOfficeModal 
      :isOpen="showCreateModal"
      @close="showCreateModal = false"
      @create="handleCreateOffice"
    />
  </div>
</template>

<script setup lang="ts">
import { ref, computed, onUnmounted } from 'vue'
import { useChatStore } from '../../stores/chat'
import type { OfficeMember } from '../../stores/chat'
import StickFigure from './StickFigure.vue'
import OfficeChair from './OfficeChair.vue'
import CreateOfficeModal from './CreateOfficeModal.vue'
import gsap from 'gsap'

const chatStore = useChatStore()
const showMemberInfoPanel = ref(false)
const showInvitePanel = ref(false)
const showCreateModal = ref(false)
const clickedMember = ref<OfficeMember | null>(null)
const clickSeatIndex = ref(-1)
const panelX = ref(0)
const panelY = ref(0)

// 办公室管理
const offices = computed(() => chatStore.offices)
const currentOfficeId = computed(() => chatStore.currentOfficeId)
const currentOffice = computed(() => chatStore.currentOffice)

const switchOffice = (officeId: string) => {
  chatStore.switchOffice(officeId)
}

// 角色状态跟踪
const memberShockedState = ref<Record<string, boolean>>({}) // 受惊状态
const isOwnerKicking = ref(false)
const ownerPos = ref({ x: 450, y: 100 })

// 8个座位位置 - 拉大间距
const allSeats = [
  { x: 200, y: 240 },
  { x: 200, y: 430 },
  { x: 70, y: 240 },
  { x: 70, y: 430 },
  { x: 700, y: 240 },
  { x: 700, y: 430 },
  { x: 830, y: 240 },
  { x: 830, y: 430 }
]

const nonOwnerMembers = computed(() => {
  return chatStore.officeMembers.filter(m => m.role !== 'owner')
})
const nonOwnerMembersWithSeat = computed(() => {
  return nonOwnerMembers.value.filter(m => 
    m.seatIndex !== undefined && 
    m.id !== idToKick.value && 
    m.id !== idToAdd.value
  )
})
const allGuests = computed(() => chatStore.availableUsersToInvite)
const totalNumber = computed(() => currentOffice.value?.members.length || 0)

const getMemberTransformBySeat = (seatIdx: number) => {
  const pos = allSeats[seatIdx % 8]
  return `translate(${pos.x}, ${pos.y})`
}

const onMemberClick = (member: OfficeMember, evt: MouseEvent) => {
  if (member.role === 'owner') return
  const rect = (evt.target as Element).getBoundingClientRect()
  panelX.value = Math.min(rect.right + 16, window.innerWidth - 200)
  panelY.value = Math.max(rect.top - 10, 70)
  clickedMember.value = member
  showMemberInfoPanel.value = true
  showInvitePanel.value = false
}

const onSeatClick = (idx: number) => {
  const usedIdx = nonOwnerMembersWithSeat.value.find(m => m.seatIndex === idx)
  if (usedIdx) return
  clickSeatIndex.value = idx
  const pos = allSeats[idx]
  panelX.value = Math.min(pos.x + 100, window.innerWidth - 230)
  panelY.value = Math.max(pos.y, 80)
  showMemberInfoPanel.value = false
  showInvitePanel.value = true
}

const memberInfoPanelStyle = computed(() => {
  return { left: panelX.value + 'px', top: panelY.value + 'px' }
})
const invitePanelStyle = computed(() => {
  return { left: panelX.value + 'px', top: panelY.value + 'px' }
})

const closeAllPanels = () => {
  showMemberInfoPanel.value = false
  showInvitePanel.value = false
  clickSeatIndex.value = -1
  clickedMember.value = null
}

// 踢飞动画 - GSAP版
const showFlyingMan = ref(false)
const idToKick = ref('')
const flyingMemberRole = ref<'admin' | 'member'>('member')
const flyState = ref({
  x: 0,
  y: 0,
  rotation: 0,
  scale: 1,
  opacity: 1
})

const flyingManTransform = computed(() => {
  const { x, y, rotation, scale } = flyState.value
  return `translate(${x}, ${y}) scale(${scale}) rotate(${rotation})`
})

const doKickNow = (memberId: string) => {
  const member = chatStore.officeMembers.find(m => m.id === memberId)
  if (!member || member.seatIndex === undefined) return

  // 此时不设置 idToKick，让他在原位待着
  flyingMemberRole.value = member.role as 'admin' | 'member'
  const startPos = allSeats[member.seatIndex]
  
  closeAllPanels()

  // 1. 皇冠小人走过去
  const tl = gsap.timeline()
  tl.to(ownerPos.value, {
    x: startPos.x + 40,
    y: startPos.y,
    duration: 0.8,
    ease: "power1.inOut",
    onStart: () => { isOwnerKicking.value = false }
  })
  // 2. 皇冠小人踢腿
  .to({}, { 
    duration: 0.2, 
    onStart: () => { 
      isOwnerKicking.value = true
      // 被踢者进入受惊状态
      memberShockedState.value[memberId] = true
      
      // 增加全场震动效果
      gsap.to(".w-full.h-full.pt-16", {
        x: (Math.random() - 0.5) * 10,
        y: (Math.random() - 0.5) * 10,
        duration: 0.1,
        repeat: 3,
        yoyo: true
      })
    } 
  })
  // 3. 目标瞬间切换并飞走
  .add(() => {
    // 关键：在这里设置 idToKick，原位置角色瞬间消失
    idToKick.value = memberId 
    delete memberShockedState.value[memberId] // 飞走后清理状态

    // 初始化飞走状态
    flyState.value = {
      x: startPos.x,
      y: startPos.y,
      rotation: 0,
      scale: 1,
      opacity: 1
    }
    showFlyingMan.value = true

    const angle = -Math.PI / 6 // 向右上角飞，角度更平一些
    const distance = 1000
    
    gsap.to(flyState.value, {
      duration: 1.0,
      x: startPos.x + Math.cos(angle) * distance,
      y: startPos.y + Math.sin(angle) * distance - 200, // 增加弧度
      rotation: 1440,
      scale: 0.05,
      opacity: 0,
      ease: "power1.in",
      onStart: () => {
        // 在踢中瞬间显示一个小小的打击效果
        gsap.fromTo("#kick-impact", 
          { x: startPos.x, y: startPos.y, scale: 0, opacity: 1 }, 
          { scale: 2.5, opacity: 0, duration: 0.5, ease: "power2.out" }
        )
      },
      onComplete: () => {
        chatStore.removeMember(memberId)
        showFlyingMan.value = false
        idToKick.value = ''
      }
    })
  })
  // 4. 皇冠小人回原位
  .to(ownerPos.value, {
    x: 450,
    y: 100,
    duration: 0.8,
    delay: 0.4,
    ease: "power1.inOut",
    onStart: () => { isOwnerKicking.value = false }
  })
}

// 走进来动画 - GSAP版
const DOOR_POS = { x: 850, y: 390 }
const showWalkingMan = ref(false)
const idToAdd = ref('')
const walkState = ref({
  x: DOOR_POS.x,
  y: DOOR_POS.y
})

const walkingManTransform = computed(() => {
  return `translate(${walkState.value.x}, ${walkState.value.y})`
})

const doInviteToSeat = (userId: string) => {
  const user = allGuests.value.find(u => u.id === userId)
  if (!user) return

  idToAdd.value = userId
  const toSeat = clickSeatIndex.value !== -1 ? clickSeatIndex.value : 0
  const targetPos = allSeats[toSeat]
  
  walkState.value = {
    x: DOOR_POS.x,
    y: DOOR_POS.y
  }
  
  showWalkingMan.value = true
  closeAllPanels()

  gsap.to(walkState.value, {
    duration: 1.5,
    x: targetPos.x,
    y: targetPos.y,
    ease: "power1.inOut",
    onComplete: () => {
      chatStore.inviteMember(idToAdd.value, toSeat)
      showWalkingMan.value = false
      idToAdd.value = ''
    }
  })
}

onUnmounted(() => {
  gsap.killTweensOf(flyState.value)
  gsap.killTweensOf(walkState.value)
  gsap.killTweensOf(ownerPos.value)
})

// 处理新建办公室
const handleCreateOffice = (data: { name: string; description: string; maxMembers: number; theme: string }) => {
  chatStore.createOffice(data)
  showCreateModal.value = false
}
</script>

<style scoped>
.pop-fade-enter-active, .pop-fade-leave-active {
  transition: all 0.25s ease;
}
.pop-fade-enter-from, .pop-fade-leave-to {
  opacity: 0;
  transform: scale(0.92);
}
</style>
