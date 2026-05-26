<template>
  <g :class="['stick-figure', isWalking ? 'walking' : '', isKicking ? 'kicking' : '']" ref="figureRef">
    <ellipse cx="0" cy="45" rx="22" ry="6" fill="rgba(15, 23, 42, 0.12)" />
    <ellipse cx="0" cy="45" rx="14" ry="3.5" fill="rgba(255, 255, 255, 0.18)" />

    <g class="body-group" ref="bodyRef">
      <ellipse cx="0" cy="-6" rx="4" ry="3.4" :fill="palette.skin" :stroke="outlineColor" stroke-width="1.1" />

      <g class="arms-group">
        <circle cx="-14.5" cy="6.5" r="3.3" :fill="palette.coat" :stroke="outlineColor" stroke-width="1.6" />
        <path d="M -14 7 Q -23 13 -20 26" fill="none" :stroke="outlineColor" stroke-width="3.2" stroke-linecap="round" class="arm-l" />
        <circle cx="-20" cy="27.5" r="2.8" :fill="palette.skin" :stroke="outlineColor" stroke-width="1.2" />

        <circle cx="14.5" cy="6.5" r="3.3" :fill="palette.coat" :stroke="outlineColor" stroke-width="1.6" />
        <path d="M 14 7 Q 23 13 20 26" fill="none" :stroke="outlineColor" stroke-width="3.2" stroke-linecap="round" class="arm-r" />
        <circle cx="20" cy="27.5" r="2.8" :fill="palette.skin" :stroke="outlineColor" stroke-width="1.2" />
      </g>

      <g class="clothing">
        <path
          d="M -14 3 Q -14 0 -11 -2 L -6 -6 Q 0 -10 6 -6 L 11 -2 Q 14 0 14 3 L 13 31 Q 9 36 0 37 Q -9 36 -13 31 Z"
          :fill="palette.coat"
          :stroke="outlineColor"
          stroke-width="2"
          stroke-linejoin="round"
        />
        <path
          d="M -8 -2 Q 0 4 8 -2 L 7 28 Q 0 31 -7 28 Z"
          :fill="palette.inner"
          opacity="0.96"
        />
        <path d="M -7 -1 L 0 10 L 7 -1" :fill="palette.collar" :stroke="outlineColor" stroke-width="1.1" stroke-linejoin="round" />
        <rect x="-2.1" y="8" width="4.2" height="13" rx="2.1" :fill="palette.accent" opacity="0.95" />
        <rect x="-7.5" y="30.5" width="15" height="2.8" rx="1.4" fill="rgba(255,255,255,0.18)" />
        <ellipse cx="-7" cy="8" rx="3.5" ry="7.5" fill="rgba(255,255,255,0.12)" />
        <circle cx="9.5" cy="11" r="2.2" :fill="palette.badge" :stroke="outlineColor" stroke-width="0.9" opacity="0.95" />
      </g>

      <g class="legs-group">
        <g class="leg-left-group" style="transform-origin: -5.5px 37px;">
          <path d="M -5.5 37 L -8 48" :stroke="palette.leg" stroke-width="3.5" stroke-linecap="round" class="leg-left" />
          <path d="M -10.5 48.5 Q -7.8 46.8 -4.8 48.4 Q -4.2 50.9 -8.6 51.2 Q -11.7 50.8 -10.5 48.5 Z" fill="#242938" :stroke="outlineColor" stroke-width="1" class="foot-left" />
        </g>
        <g class="leg-right-group" style="transform-origin: 5.5px 37px;">
          <path d="M 5.5 37 L 8 48" :stroke="palette.leg" stroke-width="3.5" stroke-linecap="round" class="leg-right" />
          <path d="M 4.8 48.4 Q 7.8 46.8 10.5 48.5 Q 11.7 50.8 8.6 51.2 Q 4.2 50.9 4.8 48.4 Z" fill="#242938" :stroke="outlineColor" stroke-width="1" class="foot-right" />
        </g>
      </g>
    </g>

    <g class="head-group" ref="headRef">
      <!-- 1. 后发层：最底层，在头后面 -->
      <g class="hair-back">
        <path v-if="role === 'owner'" d="M -15 -29 Q -16 -41 -8 -46 Q 0 -50 8 -46 Q 16 -41 15 -29 L 13 -12 Q 7 -6 0 -6 Q -7 -6 -13 -12 Z" :fill="palette.hair" />
        <path v-else-if="role === 'admin'" d="M -16 -29 Q -16 -40 -8 -45 Q 0 -49 8 -45 Q 16 -40 16 -29 L 15 -10 Q 10 -4 0 -4 Q -10 -4 -15 -10 Z" :fill="palette.hair" />
        <path v-else d="M -15 -29 Q -15 -39 -8 -43 Q 0 -46 8 -43 Q 15 -39 15 -29 L 14 -15 Q 8 -9 0 -9 Q -8 -9 -14 -15 Z" :fill="palette.hair" />
      </g>

      <!-- 2. 耳朵：在后发之上，头圆之下 -->
      <ellipse cx="-15.4" cy="-24.5" rx="2.8" ry="4.2" :fill="palette.skin" :stroke="outlineColor" stroke-width="1" />
      <ellipse cx="15.4" cy="-24.5" rx="2.8" ry="4.2" :fill="palette.skin" :stroke="outlineColor" stroke-width="1" />
      
      <!-- 3. 头部圆：皮肤层 -->
      <circle cx="0" cy="-25" r="16.8" :fill="palette.skin" :stroke="outlineColor" stroke-width="2.1" />
      <ellipse cx="-6.2" cy="-32.5" rx="5.2" ry="4.2" fill="rgba(255, 255, 255, 0.28)" />

      <!-- 4. 前发层：仅覆盖额头，不遮挡眼睛 -->
      <g class="hair-front">
        <path v-if="role === 'owner'" d="M -15 -29 Q -14 -38 -7 -42 Q 0 -45 7 -42 Q 14 -38 15 -29 L 12 -32 Q 6 -36 0 -35 Q -6 -36 -12 -32 Z" :fill="palette.hair" :stroke="palette.hairShade" stroke-width="1.2" stroke-linejoin="round" />
        <path v-else-if="role === 'admin'" d="M -15 -28 Q -14 -37 -7 -41 Q 0 -44 7 -41 Q 14 -37 15 -28 L 12 -31 Q 6 -35 0 -34 Q -6 -35 -12 -31 Z" :fill="palette.hair" :stroke="palette.hairShade" stroke-width="1.2" stroke-linejoin="round" />
        <path v-else d="M -14 -28 Q -13 -36 -7 -40 Q 0 -42 7 -40 Q 13 -36 14 -28 L 11 -31 Q 6 -34 0 -33 Q -6 -34 -11 -31 Z" :fill="palette.hair" :stroke="palette.hairShade" stroke-width="1.2" stroke-linejoin="round" />

        <!-- 角色特征发束：放在头两侧，不遮挡脸中心 -->
        <path v-if="role === 'owner'" d="M -15 -20 Q -18 -8 -15 2" fill="none" :stroke="palette.hair" stroke-width="3.6" stroke-linecap="round" />
        <path v-if="role === 'owner'" d="M 15 -20 Q 18 -8 15 2" fill="none" :stroke="palette.hair" stroke-width="3.6" stroke-linecap="round" />
        <path v-if="role === 'admin'" d="M -16 -18 Q -20 -6 -18 8" fill="none" :stroke="palette.hair" stroke-width="4" stroke-linecap="round" />
        <path v-if="role === 'admin'" d="M 16 -18 Q 20 -6 16 8" fill="none" :stroke="palette.hair" stroke-width="4" stroke-linecap="round" />

        <!-- 皇冠 -->
        <g v-if="role === 'owner'" transform="translate(0, -43)">
          <path d="M -10 4 L -7 -5 L -2 -8 L 0 -2 L 2 -8 L 7 -5 L 10 4 Z" fill="#f5c84c" stroke="#b7791f" stroke-width="1.5" stroke-linejoin="round" />
          <circle cx="-7" cy="-5" r="1.5" fill="#fff1a6" />
          <circle cx="0" cy="-2" r="1.7" fill="#fff1a6" />
          <circle cx="7" cy="-5" r="1.5" fill="#fff1a6" />
        </g>
      </g>

      <!-- 5. 面部特征：最顶层 -->
      <g class="face">
        <ellipse cx="-6" cy="-26" rx="4.1" ry="4.8" fill="#fff" />
        <ellipse cx="6" cy="-26" rx="4.1" ry="4.8" fill="#fff" />

        <g v-if="!isShocked" class="eyes">
          <ellipse cx="-6" cy="-26" rx="2.2" ry="2.8" fill="#222938" class="eye-l" />
          <ellipse cx="6" cy="-26" rx="2.2" ry="2.8" fill="#222938" class="eye-r" />
          <circle cx="-5.2" cy="-27.2" r="0.9" fill="#fff" />
          <circle cx="6.8" cy="-27.2" r="0.9" fill="#fff" />
          <path d="M -10.2 -31.2 Q -6 -33.6 -2.2 -30.8" fill="none" :stroke="outlineColor" stroke-width="1.3" stroke-linecap="round" />
          <path d="M 2.2 -30.8 Q 6 -33.6 10.2 -31.2" fill="none" :stroke="outlineColor" stroke-width="1.3" stroke-linecap="round" />
        </g>
        <g v-else class="eyes-shocked">
          <path d="M -8.7 -29 L -3.6 -24.1 M -8.7 -24.1 L -3.6 -29" :stroke="outlineColor" stroke-width="2.2" stroke-linecap="round" />
          <path d="M 3.6 -29 L 8.7 -24.1 M 3.6 -24.1 L 8.7 -29" :stroke="outlineColor" stroke-width="2.2" stroke-linecap="round" />
        </g>

        <ellipse cx="-9.4" cy="-20.8" rx="3.2" ry="2" :fill="palette.blush" opacity="0.55" />
        <ellipse cx="9.4" cy="-20.8" rx="3.2" ry="2" :fill="palette.blush" opacity="0.55" />
        <path d="M 0 -24 Q 1 -22.2 0 -20.5" fill="none" :stroke="outlineColor" stroke-width="0.95" opacity="0.4" stroke-linecap="round" />
        <path v-if="!isShocked" d="M -4.4 -17.4 Q 0 -14.3 4.4 -17.4" fill="none" :stroke="outlineColor" stroke-width="1.8" stroke-linecap="round" />
        <ellipse v-else cx="0" cy="-16.8" rx="3" ry="3.5" fill="none" :stroke="outlineColor" stroke-width="1.8" />
      </g>

      <g v-if="isShocked" transform="translate(24, -49)" class="exclamation">
        <path d="M 0 0 L 0 -15" :stroke="palette.accent" stroke-width="4" stroke-linecap="round" />
        <circle cx="0" cy="6" r="3.2" :fill="palette.accent" />
      </g>
    </g>
  </g>
</template>

<script setup lang="ts">
import { computed, onMounted, onUnmounted, ref, watch } from 'vue'
import gsap from 'gsap'

const props = defineProps<{
  role: 'owner' | 'admin' | 'member'
  color?: string
  isWalking?: boolean
  isKicking?: boolean
  isShocked?: boolean
}>()

const figureRef = ref<SVGElement | null>(null)
const headRef = ref<SVGElement | null>(null)
const bodyRef = ref<SVGElement | null>(null)
const legsRef = ref<SVGElement | null>(null)

const outlineColor = computed(() => props.color ?? '#394150')
const palette = computed(() => {
  if (props.role === 'owner') {
    return {
      skin: '#ffffff',
      blush: '#f5a3ab',
      coat: '#665cf6',
      inner: '#f8fafc',
      collar: '#eef2ff',
      accent: '#f6c453',
      badge: '#8b7cff',
      leg: '#454b61',
      hair: '#4a3458',
      hairShade: '#33213e'
    }
  }

  if (props.role === 'admin') {
    return {
      skin: '#ffffff',
      blush: '#f4b1b7',
      coat: '#14b8a6',
      inner: '#f7fffd',
      collar: '#dcfce7',
      accent: '#fb7185',
      badge: '#67e8f9',
      leg: '#465063',
      hair: '#8a5a42',
      hairShade: '#68412e'
    }
  }

  return {
    skin: '#ffffff',
    blush: '#f6b5bb',
    coat: '#5b8def',
    inner: '#f8fbff',
    collar: '#dbeafe',
    accent: '#38bdf8',
    badge: '#93c5fd',
    leg: '#4b5568',
    hair: '#374151',
    hairShade: '#1f2937'
  }
})

let idleTimeline: gsap.core.Timeline | null = null
let blinkTimer: number | null = null

watch(() => props.isKicking, (newVal) => {
  if (newVal) {
    const legLeftGroup = figureRef.value?.querySelector('.leg-left-group')
    const legRightGroup = figureRef.value?.querySelector('.leg-right-group')
    if (legLeftGroup && legRightGroup) {
      gsap.to([legLeftGroup, legRightGroup], {
        rotation: -48,
        duration: 0.12,
        yoyo: true,
        repeat: 1,
        ease: 'power2.inOut',
        onComplete: () => {
          gsap.killTweensOf([legLeftGroup, legRightGroup])
          legLeftGroup.removeAttribute('style')
          legRightGroup.removeAttribute('style')
          legLeftGroup.setAttribute('style', 'transform-origin: -5.5px 37px;')
          legRightGroup.setAttribute('style', 'transform-origin: 5.5px 37px;')
        }
      })
    }
  }
})

watch(() => props.isShocked, (newVal) => {
  if (newVal && figureRef.value) {
    gsap.to(figureRef.value, {
      x: '+=3',
      duration: 0.06,
      repeat: 6,
      yoyo: true,
      ease: 'power1.inOut'
    })
  }
})

onMounted(() => {
  if (!figureRef.value) return

  const eyes = figureRef.value.querySelectorAll('.eyes ellipse, .eyes circle')
  const exclamation = figureRef.value.querySelector('.exclamation')

  idleTimeline = gsap.timeline({ repeat: -1, yoyo: true })
  idleTimeline.to([bodyRef.value, headRef.value], {
    y: '-=2',
    duration: 2 + Math.random() * 0.5,
    ease: 'sine.inOut'
  }, 0)

  if (exclamation) {
    gsap.to(exclamation, {
      y: '-=2',
      duration: 0.3,
      repeat: -1,
      yoyo: true,
      ease: 'sine.inOut'
    })
  }

  const blink = () => {
    if (!props.isShocked && eyes.length > 0) {
      gsap.to(eyes, {
        scaleY: 0.08,
        duration: 0.08,
        repeat: 1,
        yoyo: true,
        transformOrigin: 'center center',
        ease: 'power1.inOut'
      })
    }
    blinkTimer = window.setTimeout(blink, 2800 + Math.random() * 2800)
  }

  blinkTimer = window.setTimeout(blink, 1400)
})

onUnmounted(() => {
  if (idleTimeline) idleTimeline.kill()
  if (blinkTimer) window.clearTimeout(blinkTimer)
  gsap.killTweensOf([figureRef.value, headRef.value, bodyRef.value, legsRef.value])
})
</script>

<style scoped>
.stick-figure {
  transition: opacity 0.3s ease;
  filter: drop-shadow(0 8px 10px rgba(30, 41, 59, 0.12));
}

.face,
.hair-front,
.clothing {
  pointer-events: none;
}

.stick-figure.kicking {
  animation: kick-shake 0.2s ease-out;
}

.walking .leg-left-group {
  animation: walk-leg-l 0.5s infinite alternate ease-in-out;
}

.walking .leg-right-group {
  animation: walk-leg-r 0.5s infinite alternate ease-in-out;
}

.walking .arm-l {
  animation: swing-arm-l 0.5s infinite alternate ease-in-out;
}

.walking .arm-r {
  animation: swing-arm-r 0.5s infinite alternate ease-in-out;
}

@keyframes walk-leg-l {
  from { 
    transform: rotate(-20deg); 
  }
  to { 
    transform: rotate(18deg); 
  }
}

@keyframes walk-leg-r {
  from { 
    transform: rotate(18deg); 
  }
  to { 
    transform: rotate(-20deg); 
  }
}

@keyframes swing-arm-l {
  from { transform: rotate(-14deg); transform-origin: -14px 8px; }
  to { transform: rotate(26deg); transform-origin: -14px 8px; }
}

@keyframes swing-arm-r {
  from { transform: rotate(14deg); transform-origin: 14px 8px; }
  to { transform: rotate(-26deg); transform-origin: 14px 8px; }
}

@keyframes kick-shake {
  0%, 100% { transform: scaleX(1); }
  50% { transform: scaleX(1.05); }
}
</style>
