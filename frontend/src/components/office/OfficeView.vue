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
            class="px-5 py-2.5 rounded-xl bg-gradient-to-r from-indigo-600 to-purple-600 text-white text-sm font-bold hover:shadow-lg hover:shadow-indigo-500/40 transition-all duration-200 transform hover:scale-105 active:scale-95 flex items-center gap-2"
          >
            <svg class="w-4 h-4" fill="none" stroke="currentColor" viewBox="0 0 24 24">
              <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2.5" d="M12 4v16m8-8H4" />
            </svg>
            新建办公室
          </button>
          
          <button
            class="p-2.5 rounded-xl hover:bg-slate-100 transition-all duration-200 transform hover:scale-110 active:scale-95"
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
          v-if="currentOffice"
          @click="showOwnerDetailModal = true"
          class="px-3 py-2.5 rounded-xl bg-slate-100 text-slate-700 hover:bg-slate-200 transition-all text-sm font-semibold flex items-center gap-1.5 whitespace-nowrap"
          title="办公室详情"
        >
          <svg class="w-4 h-4" fill="none" stroke="currentColor" viewBox="0 0 24 24">
            <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M13 16h-1v-4h-1m1-4h.01M21 12a9 9 0 11-18 0 9 9 0 0118 0z" />
          </svg>
          详情
        </button>
        <button
          v-for="office in offices"
          :key="office.id"
          @click="switchOffice(office.id)"
          :class="[
            'px-4 py-2.5 rounded-xl font-bold text-sm whitespace-nowrap transition-all duration-300 flex items-center gap-2 transform',
            currentOfficeId === office.id
              ? 'bg-gradient-to-r from-indigo-600 to-purple-600 text-white shadow-lg shadow-indigo-500/40 scale-105'
              : 'bg-slate-100 text-slate-700 hover:bg-slate-200 hover:scale-102 active:scale-95'
          ]"
        >
          <span class="w-2.5 h-2.5 rounded-full" :class="currentOfficeId === office.id ? 'bg-white animate-pulse' : 'bg-slate-400'"></span>
          {{ office.name }}
          <span class="text-xs opacity-75 font-semibold">({{ office.members.length }})</span>
        </button>
      </div>
    </header>

    <div class="w-full h-full pt-24 relative">
      <svg viewBox="0 0 900 550" class="w-full h-full" @click="onSceneClick">
        <!-- 背景渐变定义 -->
        <defs>
          <linearGradient id="floorGrad" x1="0%" y1="0%" x2="0%" y2="100%">
            <stop offset="0%" style="stop-color:#f8fafc;stop-opacity:1" />
            <stop offset="50%" style="stop-color:#f1f5f9;stop-opacity:1" />
            <stop offset="100%" style="stop-color:#e0e7ff;stop-opacity:0.6" />
          </linearGradient>
          <radialGradient id="impactGrad">
            <stop offset="0%" style="stop-color:#fb923c;stop-opacity:0.9" />
            <stop offset="100%" style="stop-color:#fb923c;stop-opacity:0" />
          </radialGradient>
          <filter id="softShadow" x="-20%" y="-20%" width="140%" height="140%">
            <feGaussianBlur in="SourceAlpha" stdDeviation="3" />
            <feOffset dx="2" dy="3" result="offsetblur" />
            <feComponentTransfer>
              <feFuncA type="linear" slope="0.25" />
            </feComponentTransfer>
            <feMerge>
              <feMergeNode />
              <feMergeNode in="SourceGraphic" />
            </feMerge>
          </filter>
          <filter id="deepShadow" x="-30%" y="-30%" width="160%" height="160%">
            <feGaussianBlur in="SourceAlpha" stdDeviation="5" />
            <feOffset dx="3" dy="5" result="offsetblur" />
            <feComponentTransfer>
              <feFuncA type="linear" slope="0.35" />
            </feComponentTransfer>
            <feMerge>
              <feMergeNode />
              <feMergeNode in="SourceGraphic" />
            </feMerge>
          </filter>
          <radialGradient id="lightGrad" cx="40%" cy="40%">
            <stop offset="0%" style="stop-color:#fff;stop-opacity:0.15" />
            <stop offset="100%" style="stop-color:#fff;stop-opacity:0" />
          </radialGradient>
        </defs>

        <!-- 地面 -->
        <rect x="0" y="0" width="900" height="550" fill="url(#floorGrad)" />
        
        <!-- 环境光效果 -->
        <ellipse cx="450" cy="200" rx="500" ry="300" fill="url(#lightGrad)" />
        
        <!-- 装饰：地毯 - 增强层次感 -->
        <ellipse cx="450" cy="400" rx="400" ry="85" fill="#e0e7ff" stroke="#cbd5e1" stroke-width="1" opacity="0.4" />
        <ellipse cx="450" cy="400" rx="400" ry="80" fill="#f1f5f9" stroke="#e2e8f0" stroke-width="1.5" />
        <ellipse cx="450" cy="400" rx="380" ry="70" fill="#f8fafc" stroke="#e2e8f0" stroke-width="0.5" />

        <!-- 墙壁装饰线 -->
        <g stroke="#cbd5e1" stroke-width="1" stroke-dasharray="8,4" opacity="0.3">
          <line x1="0" y1="180" x2="900" y2="180" />
        </g>

        <!-- 门口形象优化 - 增强立体感 -->
        <g filter="url(#deepShadow)">
          <rect x="820" y="280" width="70" height="180" rx="4" fill="#fff" stroke="#94a3b8" stroke-width="2.5" />
          <rect x="830" y="290" width="50" height="160" rx="2" fill="#f8fafc" stroke="#e2e8f0" stroke-width="1.5" />
          <circle cx="838" cy="370" r="5" fill="#64748b" />
          <circle cx="838" cy="370" r="3" fill="#94a3b8" />
          <rect x="825" y="280" width="3" height="180" fill="#cbd5e1" opacity="0.6" />
        </g>

        <!-- 装饰：绿植 - 增强生机感 -->
        <g transform="translate(40, 480)" filter="url(#deepShadow)">
          <rect x="-15" y="0" width="30" height="35" fill="#94a3b8" />
          <path d="M -20 0 L 20 0 L 25 -10 L -25 -10 Z" fill="#64748b" />
          <ellipse cx="0" cy="-25" rx="20" ry="30" fill="#10b981" />
          <ellipse cx="-10" cy="-35" rx="15" ry="25" fill="#059669" />
          <ellipse cx="10" cy="-30" rx="12" ry="20" fill="#34d399" />
          <ellipse cx="-5" cy="-28" rx="8" ry="12" fill="#6ee7b7" opacity="0.6" />
          <ellipse cx="8" cy="-22" rx="6" ry="10" fill="#6ee7b7" opacity="0.5" />
        </g>
        <g transform="translate(860, 480)" filter="url(#deepShadow)">
          <rect x="-15" y="0" width="30" height="35" fill="#94a3b8" />
          <path d="M -20 0 L 20 0 L 25 -10 L -25 -10 Z" fill="#64748b" />
          <ellipse cx="0" cy="-30" rx="18" ry="35" fill="#10b981" />
          <ellipse cx="8" cy="-25" rx="12" ry="25" fill="#059669" />
          <ellipse cx="-8" cy="-32" rx="10" ry="15" fill="#6ee7b7" opacity="0.6" />
          <ellipse cx="5" cy="-20" rx="7" ry="12" fill="#6ee7b7" opacity="0.5" />
        </g>

        <!-- 1. 渲染椅子 (最底层) -->
        <!-- 主管椅子 -->
        <g>
          <OfficeChair 
            :x="ownerChairPos.x" 
            :y="ownerChairPos.y"
          />
        </g>

        <!-- 普通员工椅子 -->
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
            fill="transparent" 
          />
        </g>

        <!-- 2. 渲染角色 (中间层) -->
        <!-- 群主小人 -->
        <StickFigure 
          role="owner" 
          :transform="`translate(${ownerPos.x}, ${ownerPos.y})`" 
          :class="['cursor-pointer', isOwnerSelected ? 'opacity-75' : '']"
          color="#334155"
          :isKicking="isOwnerKicking"
          :isWalking="ownerWalkTarget !== null"
          :isBack="false"
          @click.stop="onOwnerClick"
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
        <!-- 主办公桌 (群主位置) - 增强立体感 -->
        <g filter="url(#deepShadow)" pointer-events="none">
          <!-- 桌面 (梯形透视) -->
          <path d="M 320 160 L 580 160 L 620 210 L 280 210 Z" fill="#fff" stroke="#64748b" stroke-width="2.5" stroke-linejoin="round" />
          <!-- 桌边厚度 -->
          <path d="M 280 210 L 620 210 L 620 222 L 280 222 Z" fill="#e2e8f0" stroke="#64748b" stroke-width="2" stroke-linejoin="round" />
          <!-- 桌面高光 -->
          <ellipse cx="450" cy="175" rx="120" ry="20" fill="#fff" opacity="0.3" />
          
          <!-- 桌上装饰：电脑 (3D 倾斜) -->
          <g transform="translate(450, 165)">
            <rect x="-35" y="-15" width="70" height="40" rx="2" fill="#334155" transform="skewX(-10)" stroke="#475569" stroke-width="1" />
            <rect x="-30" y="-10" width="60" height="30" fill="#475569" transform="skewX(-10)" />
            <rect x="-28" y="-8" width="56" height="26" fill="#1e293b" transform="skewX(-10)" opacity="0.8" />
            <path d="M -15 25 L 15 25 L 20 30 L -20 30 Z" fill="#334155" stroke="#475569" stroke-width="1" />
            <circle cx="-20" cy="27" r="1.5" fill="#60a5fa" opacity="0.8" />
            <circle cx="20" cy="27" r="1.5" fill="#60a5fa" opacity="0.8" />
          </g>
        </g>

        <!-- 普通办公桌 (3D 透视风格) - 增强细节 -->
        <g filter="url(#deepShadow)" pointer-events="none">
          <!-- 左侧上排桌 -->
          <g transform="translate(50, 240)">
            <path d="M 10 0 L 170 0 L 180 40 L 0 40 Z" fill="#fff" stroke="#94a3b8" stroke-width="2" stroke-linejoin="round" />
            <path d="M 0 40 L 180 40 L 180 50 L 0 50 Z" fill="#f1f5f9" stroke="#94a3b8" stroke-width="1.5" stroke-linejoin="round" />
            <ellipse cx="90" cy="10" rx="70" ry="8" fill="#fff" opacity="0.25" />
            <!-- 咖啡杯 -->
            <circle cx="150" cy="20" r="5" fill="#fff" stroke="#94a3b8" stroke-width="1.5" />
            <circle cx="150" cy="20" r="3" fill="#92400e" />
            <path d="M 155 18 L 158 17 L 158 23 L 155 22 Z" fill="#94a3b8" opacity="0.6" />
          </g>
          <!-- 左侧下排桌 -->
          <g transform="translate(50, 430)">
            <path d="M 10 0 L 170 0 L 180 40 L 0 40 Z" fill="#fff" stroke="#94a3b8" stroke-width="2" stroke-linejoin="round" />
            <path d="M 0 40 L 180 40 L 180 50 L 0 50 Z" fill="#f1f5f9" stroke="#94a3b8" stroke-width="1.5" stroke-linejoin="round" />
            <ellipse cx="90" cy="10" rx="70" ry="8" fill="#fff" opacity="0.25" />
            <rect x="30" y="10" width="25" height="20" fill="#e2e8f0" rx="1" stroke="#cbd5e1" stroke-width="0.5" />
            <rect x="32" y="12" width="21" height="16" fill="#f1f5f9" rx="0.5" opacity="0.7" />
          </g>
          
          <!-- 右侧上排桌 -->
          <g transform="translate(670, 240)">
            <path d="M 10 0 L 170 0 L 180 40 L 0 40 Z" fill="#fff" stroke="#94a3b8" stroke-width="2" stroke-linejoin="round" />
            <path d="M 0 40 L 180 40 L 180 50 L 0 50 Z" fill="#f1f5f9" stroke="#94a3b8" stroke-width="1.5" stroke-linejoin="round" />
            <ellipse cx="90" cy="10" rx="70" ry="8" fill="#fff" opacity="0.25" />
          </g>
          <!-- 右侧下排桌 -->
          <g transform="translate(670, 430)">
            <path d="M 10 0 L 170 0 L 180 40 L 0 40 Z" fill="#fff" stroke="#94a3b8" stroke-width="2" stroke-linejoin="round" />
            <path d="M 0 40 L 180 40 L 180 50 L 0 50 Z" fill="#f1f5f9" stroke="#94a3b8" stroke-width="1.5" stroke-linejoin="round" />
            <ellipse cx="90" cy="10" rx="70" ry="8" fill="#fff" opacity="0.25" />
          </g>
        </g>

        <!-- 踢人冲击波效果 - 增强视觉反馈 -->
        <circle id="kick-impact" cx="0" cy="0" r="30" fill="url(#impactGrad)" style="pointer-events: none; opacity: 0;" />
        
        <!-- 踢人时的尘埃效果 -->
        <g id="dust-particles" style="pointer-events: none; opacity: 0;">
          <circle cx="0" cy="0" r="2" fill="#fb923c" opacity="0.6" />
          <circle cx="8" cy="-5" r="1.5" fill="#fb923c" opacity="0.5" />
          <circle cx="-8" cy="-3" r="1.5" fill="#fb923c" opacity="0.5" />
          <circle cx="5" cy="6" r="1" fill="#fb923c" opacity="0.4" />
          <circle cx="-6" cy="5" r="1" fill="#fb923c" opacity="0.4" />
        </g>

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
            font-size="24"
            font-weight="bold"
            :style="{ opacity: flyState.opacity }"
          >💨</text>
          <text 
            :x="flyState.x + 15" 
            :y="flyState.y - 35" 
            font-size="20"
            :style="{ opacity: flyState.opacity * 0.7 }"
          >💫</text>
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

      <!-- Chat toggle button (floating on the office scene) -->
      <button
        @click="toggleChat"
        :class="[
          'absolute bottom-6 right-6 z-30 w-14 h-14 rounded-2xl shadow-xl flex items-center justify-center transition-all duration-300',
          isChatOpen
            ? 'bg-gradient-to-br from-indigo-600 to-purple-600 text-white rotate-180'
            : 'bg-white text-indigo-600 hover:shadow-2xl hover:scale-105'
        ]"
      >
        <svg class="w-6 h-6" fill="none" stroke="currentColor" viewBox="0 0 24 24">
          <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M5 15l7-7 7 7" />
        </svg>
      </button>
    </div>

    <!-- Bottom chat drawer -->
    <Transition name="drawer">
      <div
        v-if="isChatOpen"
        class="absolute bottom-0 left-0 right-0 z-25 bg-white/95 backdrop-blur-xl border-t border-indigo-100 shadow-2xl flex flex-col"
        :style="{ height: '45%', minHeight: '320px' }"
      >
        <!-- Drawer header -->
        <div class="flex items-center justify-between px-5 py-3 border-b border-slate-100 shrink-0">
          <div class="flex items-center gap-2">
            <div class="w-2 h-2 rounded-full bg-green-500 animate-pulse"></div>
            <span class="text-sm font-semibold text-slate-700">{{ currentTitle || '办公室群聊' }}</span>
          </div>
          <button
            @click="isChatOpen = false"
            class="p-1.5 rounded-lg hover:bg-slate-100 text-slate-400 hover:text-slate-600 transition-colors"
          >
            <svg class="w-5 h-5" fill="none" stroke="currentColor" viewBox="0 0 24 24">
              <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M6 18L18 6M6 6l12 12" />
            </svg>
          </button>
        </div>

        <!-- Messages -->
        <div ref="chatListRef" class="flex-1 overflow-y-auto py-3">
          <div v-if="currentMessages.length === 0" class="flex flex-col items-center justify-center h-full text-slate-400">
            <svg class="w-12 h-12 mb-3 opacity-30" fill="none" stroke="currentColor" viewBox="0 0 24 24">
              <path stroke-linecap="round" stroke-linejoin="round" stroke-width="1.5" d="M8 12h.01M12 12h.01M16 12h.01M21 12c0 4.418-4.03 8-9 8a9.863 9.863 0 01-4.255-.949L3 20l1.395-3.72C3.512 15.042 3 13.574 3 12c0-4.418 4.03-8 9-8s9 3.582 9 8z" />
            </svg>
            <p class="text-sm">暂无消息，开始聊天吧</p>
          </div>
          <ChatMessage
            v-for="msg in currentMessages"
            :key="msg.id"
            :id="msg.id"
            :role="msg.role"
            :type="msg.type"
            :content="msg.content"
            :metadata="msg.metadata"
          />
          <!-- Loading indicator -->
          <div v-if="isLoading" class="flex items-center gap-2 px-5 py-3">
            <div class="flex gap-1">
              <span class="w-2 h-2 bg-indigo-400 rounded-full animate-bounce" style="animation-delay: 0ms"></span>
              <span class="w-2 h-2 bg-indigo-400 rounded-full animate-bounce" style="animation-delay: 150ms"></span>
              <span class="w-2 h-2 bg-indigo-400 rounded-full animate-bounce" style="animation-delay: 300ms"></span>
            </div>
            <span class="text-xs text-slate-400">Agent 正在思考...</span>
          </div>
        </div>

        <!-- Input -->
        <div class="border-t border-slate-100 shrink-0">
          <MessageInput
            :disabled="isLoading"
            @send="handleOfficeSend"
          />
        </div>
      </div>
    </Transition>

    <!-- 群主详情弹窗 -->
    <Transition name="modal-fade">
      <div v-if="showOwnerDetailModal" class="fixed inset-0 z-50 flex items-center justify-center bg-black/40 backdrop-blur-sm">
        <div class="bg-white rounded-3xl shadow-2xl w-full max-w-md mx-4 max-h-[80vh] overflow-hidden flex flex-col">
          <!-- 弹窗头部 -->
          <div class="bg-gradient-to-r from-indigo-600 to-purple-600 px-6 py-6 flex items-center justify-between">
            <div class="flex items-center gap-3">
              <img :src="currentOffice?.members.find(m => m.role === 'owner')?.avatar" class="w-14 h-14 rounded-xl shadow-lg border-2 border-white" />
              <div>
                <h2 class="text-white font-bold text-lg">{{ currentOffice?.name }}</h2>
                <p class="text-indigo-100 text-sm">办公群聊详情</p>
              </div>
            </div>
            <button 
              @click="showOwnerDetailModal = false"
              class="text-white hover:bg-white/20 p-2 rounded-lg transition-all"
            >
              <svg class="w-6 h-6" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M6 18L18 6M6 6l12 12" />
              </svg>
            </button>
          </div>

          <!-- 弹窗内容 -->
          <div class="flex-1 overflow-y-auto">
            <!-- 基础信息展示区 -->
            <div class="px-6 py-4 border-b border-slate-200">
              <div class="flex items-center justify-between">
                <span class="text-slate-600 font-semibold">总人数</span>
                <span class="text-2xl font-bold text-indigo-600">{{ currentOffice?.members.length || 0 }}</span>
              </div>
              <p class="text-xs text-slate-500 mt-2">{{ currentOffice?.description }}</p>
            </div>

            <!-- 成员信息列表区 -->
            <div class="px-6 py-4">
              <h3 class="font-bold text-slate-800 mb-3 flex items-center gap-2">
                <svg class="w-5 h-5 text-indigo-600" fill="currentColor" viewBox="0 0 20 20">
                  <path d="M10 9a3 3 0 100-6 3 3 0 000 6zm-7 9a7 7 0 1114 0H3z" />
                </svg>
                成员列表
              </h3>
              <div class="space-y-2 max-h-64 overflow-y-auto">
                <div 
                  v-for="member in currentOffice?.members" 
                  :key="member.id"
                  class="flex items-center gap-3 p-3 bg-slate-50 rounded-xl hover:bg-slate-100 transition-all"
                >
                  <img :src="member.avatar" class="w-10 h-10 rounded-lg shadow-sm" />
                  <div class="flex-1">
                    <div class="font-semibold text-slate-800 text-sm">{{ member.name }}</div>
                    <div class="text-xs text-slate-500">
                      {{ member.role === 'owner' ? '👑 群主' : member.role === 'admin' ? '👨‍💼 管理员' : '👤 普通成员' }}
                    </div>
                  </div>
                  <span class="text-xs px-2 py-1 rounded-lg" :class="member.status === 'online' ? 'bg-green-100 text-green-700' : member.status === 'away' ? 'bg-yellow-100 text-yellow-700' : 'bg-slate-100 text-slate-700'">
                    {{ member.status === 'online' ? '在线' : member.status === 'away' ? '离开' : '离线' }}
                  </span>
                </div>
              </div>
            </div>
          </div>

          <!-- 操作按钮区 -->
          <div class="px-6 py-4 border-t border-slate-200 bg-slate-50">
            <button 
              @click="showDisbandConfirmModal = true"
              class="w-full py-3 rounded-xl bg-gradient-to-r from-red-400 to-red-500 text-white font-bold hover:shadow-lg hover:shadow-red-400/40 transition-all duration-200 transform hover:scale-105 active:scale-95 flex items-center justify-center gap-2"
            >
              <svg class="w-5 h-5" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M19 7l-.867 12.142A2 2 0 0116.138 21H7.862a2 2 0 01-1.995-1.858L5 7m5 4v6m4-6v6m1-10V4a1 1 0 00-1-1h-4a1 1 0 00-1 1v3M4 7h16" />
              </svg>
              解散办公室
            </button>
          </div>
        </div>
      </div>
    </Transition>

    <!-- 解散办公室二次确认弹窗 -->
    <Transition name="modal-fade">
      <div v-if="showDisbandConfirmModal" class="fixed inset-0 z-50 flex items-center justify-center bg-black/40 backdrop-blur-sm">
        <div class="bg-white rounded-2xl shadow-2xl w-full max-w-sm mx-4 p-6">
          <div class="flex items-center justify-center w-12 h-12 rounded-full bg-red-100 mx-auto mb-4">
            <svg class="w-6 h-6 text-red-600" fill="none" stroke="currentColor" viewBox="0 0 24 24">
              <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M12 9v2m0 4v2m0 4v2M6.343 3.665c-.256-.565.198-1.165.76-1.165h10.794c.562 0 1.016.6.76 1.165l-5.397 11.778c-.256.562-.76.917-1.38.917-.62 0-1.124-.355-1.38-.917L6.343 3.665z" />
            </svg>
          </div>
          <h3 class="text-lg font-bold text-slate-900 text-center mb-2">确认解散办公室？</h3>
          <p class="text-slate-600 text-center text-sm mb-6">
            解散后，所有成员将被移除，办公室数据将被永久删除，此操作无法撤销。
          </p>
          <div class="flex gap-3">
            <button 
              @click="showDisbandConfirmModal = false"
              class="flex-1 py-2.5 rounded-xl bg-slate-100 text-slate-700 font-bold hover:bg-slate-200 transition-all"
            >
              取消
            </button>
            <button 
              @click="confirmDisbandOffice"
              class="flex-1 py-2.5 rounded-xl bg-gradient-to-r from-red-400 to-red-500 text-white font-bold hover:shadow-lg hover:shadow-red-400/40 transition-all transform hover:scale-105 active:scale-95"
            >
              确认解散
            </button>
          </div>
        </div>
      </div>
    </Transition>

    <!-- 人物信息小卡片 -->
    <Transition name="pop-fade">
      <div v-if="showMemberInfoPanel && clickedMember" class="absolute z-50 bg-white/70 backdrop-blur-2xl rounded-2xl shadow-2xl p-5 w-56 border border-white/60" :style="memberInfoPanelStyle">
        <div class="flex items-center gap-3 mb-4">
          <img :src="clickedMember.avatar" class="w-12 h-12 rounded-xl shadow-md" />
          <div>
            <div class="font-bold text-slate-800 text-sm">{{ clickedMember.name }}</div>
            <div class="text-xs text-slate-500 font-medium">
              {{ clickedMember.role === 'admin' ? '👨‍💼 管理员' : '👤 普通成员' }}
            </div>
          </div>
        </div>
        <button 
          @click="doKickNow(clickedMember.id)"
          class="w-full py-2.5 rounded-xl bg-gradient-to-r from-red-400 to-red-500 text-white text-xs font-bold hover:shadow-lg hover:shadow-red-400/40 transition-all duration-200 transform hover:scale-105 active:scale-95"
        >
          🚪 踢出办公室
        </button>
      </div>
    </Transition>

    <!-- 空位邀请小列表 -->
    <Transition name="pop-fade">
      <div v-if="showInvitePanel && clickSeatIndex !== -1" class="absolute z-50 bg-white/70 backdrop-blur-2xl rounded-2xl shadow-2xl p-4 w-64 border border-white/60" :style="invitePanelStyle">
        <div class="text-xs font-bold text-slate-700 mb-3 flex items-center gap-2">
          <span>👥 邀请新成员入座</span>
        </div>
        <div class="space-y-2 max-h-56 overflow-y-auto">
          <div 
            v-for="guest in allGuests" 
            :key="guest.id"
            @click="doInviteToSeat(guest.id)"
            class="flex items-center p-2.5 bg-white/50 rounded-xl hover:bg-indigo-100/70 cursor-pointer transition-all duration-200 transform hover:scale-105 active:scale-95"
          >
            <img :src="guest.avatar" class="w-8 h-8 rounded-lg mr-2.5 shadow-sm" />
            <div class="flex-1">
              <div class="font-semibold text-slate-700 text-xs">{{ guest.name }}</div>
            </div>
            <div class="text-xs font-bold text-indigo-600 bg-indigo-100/60 px-2 py-1 rounded-lg">邀请</div>
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
import { ref, computed, onMounted, onUnmounted, nextTick, watch } from 'vue'
import { useRoute } from 'vue-router'
import { useChatStore } from '../../stores/chat'
import { storeToRefs } from 'pinia'
import type { OfficeMember } from '../../stores/chat'
import StickFigure from './StickFigure.vue'
import OfficeChair from './OfficeChair.vue'
import CreateOfficeModal from './CreateOfficeModal.vue'
import ChatMessage from '../chat/ChatMessage.vue'
import MessageInput from '../chat/MessageInput.vue'
import gsap from 'gsap'

const chatStore = useChatStore()
const { currentMessages, isLoading, currentTitle } = storeToRefs(chatStore)
const showMemberInfoPanel = ref(false)
const showInvitePanel = ref(false)
const showCreateModal = ref(false)
const showOwnerDetailModal = ref(false)
const showDisbandConfirmModal = ref(false)
const isChatOpen = ref(false)
const chatInputText = ref('')
const chatListRef = ref<HTMLElement | null>(null)

const route = useRoute()

onMounted(async () => {
  chatStore.initWebSocket()
  await chatStore.loadConversationList()

  // Reconstruct offices from group conversations
  chatStore.syncOfficesFromConversations()

  const convId = route.params.conversationId as string | undefined
  if (convId) {
    const office = offices.value.find(o => o.conversationId === convId)
    if (office) {
      switchOffice(office.id)
      isChatOpen.value = true
      nextTick(() => {
        chatStore.openOfficeChat(office.id)
      })
    }
  }
})

const toggleChat = () => {
  isChatOpen.value = !isChatOpen.value
  if (isChatOpen.value) {
    chatStore.openOfficeChat(currentOfficeId.value)
    nextTick(() => {
      if (chatListRef.value) {
        chatListRef.value.scrollTop = chatListRef.value.scrollHeight
      }
    })
  }
}

const handleOfficeSend = (content: string) => {
  if (!content.trim()) return
  chatStore.sendMessage(content.trim())
  nextTick(() => {
    if (chatListRef.value) {
      chatListRef.value.scrollTop = chatListRef.value.scrollHeight
    }
  })
}

// Auto-scroll when new messages arrive
watch(currentMessages, () => {
  nextTick(() => {
    if (chatListRef.value && isChatOpen.value) {
      chatListRef.value.scrollTop = chatListRef.value.scrollHeight
    }
  })
}, { deep: true })
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
  if (isChatOpen.value) {
    chatStore.openOfficeChat(officeId)
  }
}

// 角色状态跟踪
const memberShockedState = ref<Record<string, boolean>>({}) // 受惊状态
const isOwnerKicking = ref(false)
const ownerPos = ref({ x: 450, y: 140 })
const ownerChairPos = ref({ x: 450, y: 160 })
const isOwnerSitting = ref(true)
const isOwnerSelected = ref(false)
const ownerWalkTarget = ref<{ x: number; y: number } | null>(null)

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
  return currentOffice.value?.members.filter(m => m.role !== 'owner') || []
})
const nonOwnerMembersWithSeat = computed(() => {
  return nonOwnerMembers.value.filter(m => 
    m.seatIndex !== undefined && 
    m.id !== idToKick.value && 
    m.id !== idToAdd.value
  )
})
const allGuests = computed(() => {
  const memberIds = new Set((currentOffice.value?.members || []).map(m => m.id))
  return chatStore.officeAvailableAgents.filter(a => !memberIds.has(a.id))
})
const totalNumber = computed(() => currentOffice.value?.members.length || 0)

const getMemberTransformBySeat = (seatIdx: number) => {
  const pos = allSeats[seatIdx % 8]
  return `translate(${pos.x}, ${pos.y})`
}

const onMemberClick = (member: OfficeMember, evt: MouseEvent) => {
  if (member.role === 'owner') return
  // 使用 currentTarget 确保获取的是 StickFigure 的整体容器位置，而不是内部某个 path
  const rect = (evt.currentTarget as Element).getBoundingClientRect()
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
  const member = currentOffice.value?.members.find(m => m.id === memberId)
  if (!member || member.seatIndex === undefined) return

  flyingMemberRole.value = member.role as 'admin' | 'member'
  const startPos = allSeats[member.seatIndex]
  
  closeAllPanels()

  const tl = gsap.timeline()
  
  tl.to(ownerPos.value, {
    x: startPos.x + 40,
    y: startPos.y,
    duration: 0.6,
    ease: "power2.inOut",
    onStart: () => { isOwnerKicking.value = false }
  })
  
  .to({}, { 
    duration: 0.12, 
    onStart: () => { 
      isOwnerKicking.value = true
      memberShockedState.value[memberId] = true
      
      gsap.to(".pt-24", {
        x: (Math.random() - 0.5) * 15,
        y: (Math.random() - 0.5) * 15,
        duration: 0.08,
        repeat: 5,
        yoyo: true,
        ease: "power2.inOut",
        clearProps: "x,y"
      })
    } 
  })
  
  .add(() => {
    idToKick.value = memberId 
    delete memberShockedState.value[memberId]

    flyState.value = {
      x: startPos.x,
      y: startPos.y,
      rotation: 0,
      scale: 1,
      opacity: 1
    }
    showFlyingMan.value = true

    const angle = -Math.PI / 4
    const distance = 1400
    
    gsap.to(flyState.value, {
      duration: 0.9,
      x: startPos.x + Math.cos(angle) * distance,
      y: startPos.y + Math.sin(angle) * distance,
      rotation: 1800,
      scale: 0.01,
      opacity: 0,
      ease: "power2.in",
      onStart: () => {
        gsap.fromTo("#kick-impact", 
          { x: startPos.x, y: startPos.y, scale: 0, opacity: 1 }, 
          { scale: 3.5, opacity: 0, duration: 0.5, ease: "power2.out" }
        )
        
        gsap.fromTo("#dust-particles",
          { x: startPos.x, y: startPos.y, opacity: 1 },
          { 
            x: startPos.x + (Math.random() - 0.5) * 120,
            y: startPos.y + (Math.random() - 0.5) * 120,
            opacity: 0,
            duration: 0.7,
            ease: "power1.out"
          }
        )
      },
      onComplete: () => {
        chatStore.removeMember(memberId)
        showFlyingMan.value = false
        idToKick.value = ''
      }
    })
  })
  
  .to(ownerPos.value, {
    x: 450,
    y: 140,
    duration: 0.6,
    delay: 0.2,
    ease: "power2.inOut",
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

  const walkTl = gsap.timeline()
  
  walkTl.to(walkState.value, {
    duration: 1.8,
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

// 主管椅子交互
const onOwnerChairClick = () => {
  if (isOwnerSitting.value) {
    gsap.to(ownerPos.value, {
      x: 450,
      y: 100,
      duration: 0.6,
      ease: "power2.inOut",
      onComplete: () => {
        isOwnerSitting.value = false
      }
    })
  } else {
    gsap.to(ownerPos.value, {
      x: ownerChairPos.value.x,
      y: ownerChairPos.value.y + 20,
      duration: 0.6,
      ease: "power2.inOut",
      onComplete: () => {
        isOwnerSitting.value = true
      }
    })
  }
}

// 点击群主头像/名称
const onOwnerClick = () => {
  isOwnerSelected.value = !isOwnerSelected.value
}

// 场景点击处理
const onSceneClick = (evt: MouseEvent) => {
  if (!isOwnerSelected.value) return
  
  const svg = evt.currentTarget as SVGSVGElement
  const rect = svg.getBoundingClientRect()
  const x = ((evt.clientX - rect.left) / rect.width) * 900
  const y = ((evt.clientY - rect.top) / rect.height) * 550
  
  isOwnerSelected.value = false
  ownerWalkTarget.value = { x, y }
  
  const walkTl = gsap.timeline()
  walkTl.to(ownerPos.value, {
    duration: 1.5,
    x: x,
    y: y,
    ease: "power1.inOut",
    onComplete: () => {
      ownerWalkTarget.value = null
    }
  })
}

// 解散办公室
const confirmDisbandOffice = () => {
  if (!currentOffice.value) return
  
  const officeId = currentOffice.value.id
  chatStore.deleteOffice(officeId)
  showDisbandConfirmModal.value = false
  showOwnerDetailModal.value = false
}

// 处理新建办公室
const handleCreateOffice = async (data: { name: string; description: string; maxMembers: number }) => {
  await chatStore.createOffice(data)
  showCreateModal.value = false
  isChatOpen.value = false
}
</script>

<style scoped>
.pop-fade-enter-active, .pop-fade-leave-active {
  transition: all 0.3s cubic-bezier(0.34, 1.56, 0.64, 1);
}
.pop-fade-enter-from, .pop-fade-leave-to {
  opacity: 0;
  transform: scale(0.85) translateY(-10px);
}

.pop-fade-enter-to, .pop-fade-leave-from {
  opacity: 1;
  transform: scale(1) translateY(0);
}

.modal-fade-enter-active, .modal-fade-leave-active {
  transition: all 0.3s cubic-bezier(0.34, 1.56, 0.64, 1);
}
.modal-fade-enter-from, .modal-fade-leave-to {
  opacity: 0;
  transform: scale(0.9);
}

.modal-fade-enter-to, .modal-fade-leave-from {
  opacity: 1;
  transform: scale(1);
}

.drawer-enter-active, .drawer-leave-active {
  transition: all 0.35s cubic-bezier(0.4, 0, 0.2, 1);
}
.drawer-enter-from, .drawer-leave-to {
  transform: translateY(100%);
  opacity: 0;
}
</style>
