<template>
  <div class="h-full w-full overflow-hidden bg-gradient-to-br from-[#fefefe] to-[#f8fafc] relative">
    <header class="absolute top-0 left-0 right-0 z-20 h-16 bg-white/70 backdrop-blur-md border-b border-slate-100 px-6 flex items-center justify-between">
      <div class="flex items-center gap-3">
        <h1 class="text-lg font-bold text-slate-800">办公室</h1>
        <span class="text-sm text-slate-500">{{ totalNumber }} 人</span>
      </div>
    </header>

    <div class="w-full h-full pt-16 relative">
      <svg viewBox="0 0 900 550" class="w-full h-full">
<<<<<<< HEAD
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
          <rect 
            :x="seat.x - 30" 
            :y="seat.y - 20" 
            width="60" 
            height="70" 
        <rect x="0" y="0" width="900" height="550" fill="#fffaf8" />
        <g stroke="#d4c4b7" stroke-width="1.5" stroke-dasharray="4,2">
          <line x1="0" y1="450" x2="900" y2="450" />
          <line x1="0" y1="480" x2="900" y2="480" />
          <line x1="0" y1="510" x2="900" y2="510" />
        </g>
        <g>
          <rect x="820" y="320" width="60" height="130" rx="4" fill="#e8d5c4" stroke="#a88970" stroke-width="3" />
          <circle cx="865" cy="390" r="5" fill="#8b6b4d" />
        </g>
        <ellipse cx="450" cy="120" rx="180" ry="60" fill="#fef3e7" stroke="#c4a07c" stroke-width="3.5" />
        <ellipse cx="450" cy="120" rx="160" ry="48" fill="#fdf7f2" stroke="#d4b595" stroke-width="1.5" />
        <g transform="translate(450, 65)">
          <ellipse cx="0" cy="0" rx="28" ry="14" fill="#ffedd5" stroke="#d97706" stroke-width="2.5" />
          <rect x="-20" y="-35" width="40" height="18" rx="4" fill="#fed7aa" stroke="#f97316" stroke-width="2" />
        </g>
        <g>
          <rect x="60" y="260" width="160" height="45" rx="8" fill="#faf5ef" stroke="#c2a07c" stroke-width="2.5" />
          <rect x="60" y="340" width="160" height="45" rx="8" fill="#faf5ef" stroke="#c2a07c" stroke-width="2.5" />
          <rect x="680" y="260" width="160" height="45" rx="8" fill="#faf5ef" stroke="#c2a07c" stroke-width="2.5" />
          <rect x="680" y="340" width="160" height="45" rx="8" fill="#faf5ef" stroke="#c2a07c" stroke-width="2.5" />
        </g>

        <!-- 8个空座位可点击区域 -->
        <g 
          v-for="(seat, idx) in allSeats" 
          :key="'seat-click-' + idx"
          @click="onSeatClick(idx)"
          class="cursor-pointer"
        >
          <rect 
            :x="seat.x - 35" 
            :y="seat.y - 60" 
            width="70" 
            height="110" 
>>>>>>> 321ea3cbb2142824b9d80a9cd3ae5cd602b35a84
            fill="transparent" 
          />
        </g>

<<<<<<< HEAD
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
=======
        <g fill="#fef3e7" stroke="#a16207" stroke-width="2">
          <rect x="50" y="235" width="24" height="16" rx="4" />
          <rect x="50" y="315" width="24" height="16" rx="4" />
          <rect x="202" y="235" width="24" height="16" rx="4" />
          <rect x="202" y="315" width="24" height="16" rx="4" />
          <rect x="676" y="235" width="24" height="16" rx="4" />
          <rect x="676" y="315" width="24" height="16" rx="4" />
          <rect x="826" y="235" width="24" height="16" rx="4" />
          <rect x="826" y="315" width="24" height="16" rx="4" />
        </g>

        <!-- 群主小人 -->
        <g class="cursor-pointer" transform="translate(450, 35)">
          <circle cx="0" cy="-30" r="13" fill="#fff" stroke="#374151" stroke-width="2.5" />
          <path d="M -12 -15 L 0 0 L 12 -15" stroke="#374151" stroke-width="3" fill="none" stroke-linecap="round" />
          <line x1="0" y1="0" x2="0" y2="22" stroke="#374151" stroke-width="3" stroke-linecap="round" />
          <line x1="-15" y1="6" x2="15" y2="6" stroke="#374151" stroke-width="3" stroke-linecap="round" />
          <line x1="0" y1="22" x2="-12" y2="42" stroke="#374151" stroke-width="3" stroke-linecap="round" />
          <line x1="0" y1="22" x2="12" y2="42" stroke="#374151" stroke-width="3" stroke-linecap="round" />
          <path d="M -10 -48 L -6 -58 L -2 -48 L 2 -58 L 6 -48 L 10 -58 L 14 -48 Z" fill="#fcd34d" stroke="#d97706" stroke-width="1.5" />
        </g>

        <!-- 动态渲染普通成员小人 根据 seatIndex 直接取位置 顺序完全不变 -->
        <g 
          v-for="member in nonOwnerMembersWithSeat" 
          :key="'member-' + member.id"
          class="cursor-pointer"
          :transform="getMemberTransformBySeat(member.seatIndex!)"
          @click="onMemberClick(member, $event)"
        >
          <circle cx="0" cy="-25" r="11" fill="#fff" stroke="#4b5563" stroke-width="2.2" />
          <path d="M -10 -12 L 0 2 L 10 -12" stroke="#4b5563" stroke-width="2.5" fill="none" stroke-linecap="round" />
          <line x1="0" y1="2" x2="0" y2="22" stroke="#4b5563" stroke-width="2.5" stroke-linecap="round" />
          <line x1="-11" y1="9" x2="11" y2="9" stroke="#4b5563" stroke-width="2.5" stroke-linecap="round" />
          <line x1="0" y1="22" x2="-9" y2="38" stroke="#4b5563" stroke-width="2.5" stroke-linecap="round" />
          <line x1="0" y1="22" x2="9" y2="38" stroke="#4b5563" stroke-width="2.5" stroke-linecap="round" />
        </g>

        <!-- 正在飞出去的人物动画 -->
        <g v-if="showFlyingMan" :transform="flyingManPos">
          <circle cx="0" cy="-25" r="11" fill="#fff" stroke="#f97316" stroke-width="2.2" />
          <path d="M -10 -12 L 0 2 L 10 -12" stroke="#f97316" stroke-width="2.5" fill="none" stroke-linecap="round" />
          <line x1="0" y1="2" x2="0" y2="22" stroke="#f97316" stroke-width="2.5" stroke-linecap="round" />
          <line x1="-11" y1="9" x2="11" y2="9" stroke="#f97316" stroke-width="2.5" stroke-linecap="round" />
          <line x1="0" y1="22" x2="-9" y2="38" stroke="#f97316" stroke-width="2.5" stroke-linecap="round" />
          <line x1="0" y1="22" x2="9" y2="38" stroke="#f97316" stroke-width="2.5" stroke-linecap="round" />
          <text y="-35" x="-10" font-size="14">💨</text>
        </g>

        <!-- 正在走进来的人物动画 -->
        <g v-if="showWalkingMan" :transform="walkingManPos">
          <circle cx="0" cy="-25" r="11" fill="#ecfdf5" stroke="#10b981" stroke-width="2.2" />
          <path d="M -10 -12 L 0 2 L 10 -12" stroke="#10b981" stroke-width="2.5" fill="none" stroke-linecap="round" />
          <line x1="0" y1="2" x2="0" y2="22" stroke="#10b981" stroke-width="2.5" stroke-linecap="round" />
          <line x1="-11" y1="9" x2="11" y2="9" stroke="#10b981" stroke-width="2.5" stroke-linecap="round" />
          <line x1="0" y1="22" x2="-9" y2="38" stroke="#10b981" stroke-width="2.5" stroke-linecap="round" />
          <line x1="0" y1="22" x2="9" y2="38" stroke="#10b981" stroke-width="2.5" stroke-linecap="round" />
        </g>
>>>>>>> 321ea3cbb2142824b9d80a9cd3ae5cd602b35a84
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
  </div>
</template>

<script setup lang="ts">
import { ref, computed, onUnmounted } from 'vue'
import { useChatStore } from '../../stores/chat'
import type { OfficeMember } from '../../stores/chat'
<<<<<<< HEAD
import StickFigure from './StickFigure.vue'
import OfficeChair from './OfficeChair.vue'
import gsap from 'gsap'
=======
>>>>>>> 321ea3cbb2142824b9d80a9cd3ae5cd602b35a84

const chatStore = useChatStore()
const showMemberInfoPanel = ref(false)
const showInvitePanel = ref(false)
const clickedMember = ref<OfficeMember | null>(null)
const clickSeatIndex = ref(-1)
const panelX = ref(0)
const panelY = ref(0)

<<<<<<< HEAD
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
=======
// 8个座位位置
const allSeats = [
  { x: 200, y: 285 },
  { x: 200, y: 365 },
  { x: 70, y: 285 },
  { x: 70, y: 365 },
  { x: 700, y: 285 },
  { x: 700, y: 365 },
  { x: 830, y: 285 },
  { x: 830, y: 365 }
>>>>>>> 321ea3cbb2142824b9d80a9cd3ae5cd602b35a84
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
const totalNumber = computed(() => chatStore.officeMembers.length)

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

<<<<<<< HEAD
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
=======
// 踢飞动画
const showFlyingMan = ref(false)
const flyP = ref(0)
const flyStartPos = ref({ x: 0, y: 0 })
const flyVector = ref({ x: 0, y: 0 })
const idToKick = ref('')

const flyingManPos = computed(() => {
  const p = flyP.value
  const x = flyStartPos.value.x + flyVector.value.x * p
  const y = flyStartPos.value.y + flyVector.value.y * p - Math.sin(p * Math.PI) * 100 // 增加一点抛物线感
  const scale = 1 - p * 0.5 // 飞远变小
  const rotate = p * 720 // 旋转
  return `translate(${x}, ${y}) scale(${scale}) rotate(${rotate})`
})

let flyingTimer: any = null
>>>>>>> 321ea3cbb2142824b9d80a9cd3ae5cd602b35a84

const doKickNow = (memberId: string) => {
  const member = chatStore.officeMembers.find(m => m.id === memberId)
  if (!member || member.seatIndex === undefined) return

<<<<<<< HEAD
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
=======
  idToKick.value = memberId
  const startPos = allSeats[member.seatIndex]
  flyStartPos.value = { ...startPos }

  // 随机飞出方向
  const angle = Math.random() * Math.PI * 2
  const distance = 600 + Math.random() * 200
  flyVector.value = {
    x: Math.cos(angle) * distance,
    y: Math.sin(angle) * distance
  }

  showFlyingMan.value = true
  flyP.value = 0
  closeAllPanels()

  const total = 25
  let step = 0
  if (flyingTimer) clearInterval(flyingTimer)
  flyingTimer = setInterval(() => {
    step++
    flyP.value = step / total
    if (step >= total) {
      clearInterval(flyingTimer)
      chatStore.removeMember(idToKick.value)
      showFlyingMan.value = false
      flyP.value = 0
      idToKick.value = ''
    }
  }, 24)
}

// 走进来动画 门口坐标
const DOOR_POS = { x: 850, y: 390 }
const showWalkingMan = ref(false)
const walkP = ref(0)
const idToAdd = ref('')
const walkingManPos = computed(() => {
  const idx = clickSeatIndex.value !== -1 ? clickSeatIndex.value : 0
  const targetPos = allSeats[idx]
  const p = walkP.value
  // 从门口走到座位
  const x = DOOR_POS.x - p * (DOOR_POS.x - targetPos.x)
  const y = DOOR_POS.y - p * (DOOR_POS.y - targetPos.y)
  // 走路时的晃动感
  const bounce = Math.abs(Math.sin(p * 10 * Math.PI)) * 5
  return `translate(${x}, ${y - bounce})`
})
let walkingTimer: any = null

const doInviteToSeat = (userId: string) => {
  idToAdd.value = userId
  showWalkingMan.value = true
  walkP.value = 0
  const toSeat = clickSeatIndex.value !== -1 ? clickSeatIndex.value : 0
  closeAllPanels()
  const total = 30
  let step = 0
  if (walkingTimer) clearInterval(walkingTimer)
  walkingTimer = setInterval(() => {
    step++
    walkP.value = step / total
    if (step >= total) {
      clearInterval(walkingTimer)
      chatStore.inviteMember(idToAdd.value, toSeat)
      showWalkingMan.value = false
      walkP.value = 0
      idToAdd.value = ''
    }
  }, 22)
}

onUnmounted(() => {
  if (flyingTimer) clearInterval(flyingTimer)
  if (walkingTimer) clearInterval(walkingTimer)
>>>>>>> 321ea3cbb2142824b9d80a9cd3ae5cd602b35a84
})
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
