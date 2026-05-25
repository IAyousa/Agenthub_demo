<template>
  <g :class="['stick-figure', isWalking ? 'walking' : '']" ref="figureRef">
    <!-- 底部阴影 -->
    <ellipse cx="0" cy="42" rx="15" ry="4" fill="rgba(0,0,0,0.06)" />

    <!-- 角色主体 -->
    <g class="body-group" ref="bodyRef">
      <!-- 身体/躯干 -->
      <path 
        d="M -12 10 Q -14 38 -10 40 L 10 40 Q 14 38 12 10 L 10 -11 Q 0 -16 -10 -11 Z" 
        fill="#fff" 
        :stroke="color" 
        stroke-width="2.5" 
      />
      
      <!-- 手臂 -->
      <g class="arms-group">
        <path d="M -11 8 Q -18 11 -16 21" fill="none" :stroke="color" stroke-width="2.8" stroke-linecap="round" class="arm-l" />
        <path d="M 11 8 Q 18 11 16 21" fill="none" :stroke="color" stroke-width="2.8" stroke-linecap="round" class="arm-r" />
      </g>

      <!-- 腿部 -->
      <g class="legs-group" ref="legsRef">
        <path d="M -6 40 L -8 48" :stroke="color" stroke-width="3" stroke-linecap="round" class="leg-left" />
        <path d="M 6 40 L 8 48" :stroke="color" stroke-width="3" stroke-linecap="round" class="leg-right" />
      </g>
    </g>

    <!-- 头部组 -->
    <g class="head-group" ref="headRef">
      <!-- 耳朵形象 -->
      <g v-if="role === 'owner'" transform="translate(0, -38)">
        <path d="M -7 -8 C -12 -28, -2 -28, -3 -8" fill="#fff" :stroke="color" stroke-width="1.8" />
        <path d="M 7 -8 C 12 -25, 2 -25, 3 -8" fill="#fff" :stroke="color" stroke-width="1.8" />
        <path d="M -10 2 L -6 -12 L 0 -2 L 6 -12 L 10 2 Z" fill="#fcd34d" stroke="#d97706" stroke-width="1.5" />
        <circle cx="0" cy="-2" r="2" fill="#ef4444" />
      </g>
      
      <g v-else-if="role === 'admin'" transform="translate(0, -35)">
        <path d="M -6 -5 C -13 -32, -1 -32, -2 -5" fill="#fff" :stroke="color" stroke-width="2" />
        <path d="M 6 -5 C 13 -32, 1 -32, 2 -5" fill="#fff" :stroke="color" stroke-width="2" />
        <path d="M -6 -10 C -9 -24, -4 -24, -4 -10" fill="#fee2e2" opacity="0.8" />
        <path d="M 6 -10 C 9 -24, 4 -24, 4 -10" fill="#fee2e2" opacity="0.8" />
      </g>
      
      <g v-else transform="translate(0, -35)">
        <path d="M -11 5 L -15 -10 L -2 1 Z" fill="#fff" :stroke="color" stroke-width="2" />
        <path d="M 11 5 L 15 -10 L 2 1 Z" fill="#fff" :stroke="color" stroke-width="2" />
        <path d="M -10 2 L -12 -4 L -5 1 Z" fill="#fecaca" opacity="0.8" />
        <path d="M 10 2 L 12 -4 L 5 1 Z" fill="#fecaca" opacity="0.8" />
      </g>

      <!-- 头部圆 -->
      <circle cx="0" cy="-25" r="14" fill="#fff" :stroke="color" stroke-width="2.5" />
      
      <!-- 表情系统 -->
      <g class="face">
        <!-- 正常眼睛 -->
        <g v-if="!isShocked" class="eyes">
          <circle cx="-5" cy="-27" r="1.8" :fill="color" class="eye-l" />
          <circle cx="5" cy="-27" r="1.8" :fill="color" class="eye-r" />
        </g>
        <!-- 受惊/伤心眼睛 -->
        <g v-else class="eyes-shocked">
          <path d="M -7 -29 L -3 -25 M -7 -25 L -3 -29" :stroke="color" stroke-width="1.5" stroke-linecap="round" />
          <path d="M 3 -29 L 7 -25 M 3 -25 L 7 -29" :stroke="color" stroke-width="1.5" stroke-linecap="round" />
        </g>
        
        <!-- 嘴巴：正常笑脸 vs 受惊圆嘴 -->
        <path v-if="!isShocked" d="M -2 -21 Q 0 -19 2 -21" fill="none" :stroke="color" stroke-width="1.5" stroke-linecap="round" />
        <circle v-else cx="0" cy="-20" r="2.5" fill="none" :stroke="color" stroke-width="1.5" />
      </g>

      <!-- 感叹号特效 -->
      <g v-if="isShocked" transform="translate(20, -45)" class="exclamation">
        <path d="M 0 0 L 0 -12" :stroke="color" stroke-width="3" stroke-linecap="round" />
        <circle cx="0" cy="4" r="2" :fill="color" />
      </g>
    </g>
  </g>
</template>

<script setup lang="ts">
import { onMounted, ref, onUnmounted, watch } from 'vue'
import gsap from 'gsap'

const props = defineProps<{
  role: 'owner' | 'admin' | 'member'
  color?: string
  isWalking?: boolean
  isKicking?: boolean
  isShocked?: boolean // 新增：受惊/被踢状态
}>()

const figureRef = ref<SVGElement | null>(null)
const headRef = ref<SVGElement | null>(null)
const bodyRef = ref<SVGElement | null>(null)
const legsRef = ref<SVGElement | null>(null)

let idleTimeline: gsap.core.Timeline | null = null

// 监听踢腿动作 (群主用)
watch(() => props.isKicking, (newVal) => {
  if (newVal && legsRef.value) {
    gsap.to(legsRef.value, {
      rotation: -45,
      duration: 0.15,
      yoyo: true,
      repeat: 1,
      transformOrigin: "top center"
    })
  }
})

// 监听受惊状态 (被踢者用)
watch(() => props.isShocked, (newVal) => {
  if (newVal && figureRef.value) {
    // 受惊时的抖动
    gsap.to(figureRef.value, {
      x: "+=2",
      duration: 0.05,
      repeat: 5,
      yoyo: true
    })
  }
})

onMounted(() => {
  if (!figureRef.value) return

  idleTimeline = gsap.timeline({ repeat: -1, yoyo: true })
  const eyes = figureRef.value.querySelectorAll('.eyes circle')

  idleTimeline.to([bodyRef.value, headRef.value], {
    y: "-=1.5",
    duration: 1.5 + Math.random(),
    ease: "sine.inOut"
  })

  const blink = () => {
    if (!props.isShocked && eyes.length > 0) {
      gsap.to(eyes, {
        scaleY: 0.1,
        duration: 0.1,
        repeat: 1,
        yoyo: true,
        transformOrigin: "center center"
      })
    }
    setTimeout(blink, 2000 + Math.random() * 4000)
  }
  setTimeout(blink, 1000)
})

onUnmounted(() => {
  if (idleTimeline) idleTimeline.kill()
})
</script>


<style scoped>
.stick-figure {
  transition: opacity 0.3s ease;
}

.walking .leg-left {
  animation: walk-leg-l 0.4s infinite alternate ease-in-out;
}
.walking .leg-right {
  animation: walk-leg-r 0.4s infinite alternate ease-in-out;
}
.walking .arm-l {
  animation: swing-arm-l 0.4s infinite alternate ease-in-out;
}
.walking .arm-r {
  animation: swing-arm-r 0.4s infinite alternate ease-in-out;
}

@keyframes walk-leg-l {
  from { transform: rotate(-15deg); transform-origin: -6px 40px; }
  to { transform: rotate(15deg); transform-origin: -6px 40px; }
}
@keyframes walk-leg-r {
  from { transform: rotate(15deg); transform-origin: 6px 40px; }
  to { transform: rotate(-15deg); transform-origin: 6px 40px; }
}
@keyframes swing-arm-l {
  from { transform: rotate(-10deg); transform-origin: -11px 12px; }
  to { transform: rotate(20deg); transform-origin: -11px 12px; }
}
@keyframes swing-arm-r {
  from { transform: rotate(10deg); transform-origin: 11px 12px; }
  to { transform: rotate(-20deg); transform-origin: 11px 12px; }
}
</style>
