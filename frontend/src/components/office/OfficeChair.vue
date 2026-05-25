<template>
  <g class="office-chair" :transform="`translate(${x}, ${y})`">
    <!-- 椅子支架 -->
    <path d="M -10 35 L -15 45 M 10 35 L 15 45 M 0 35 L 0 42 M -8 42 L 8 42" stroke="#64748b" stroke-width="2" stroke-linecap="round" />
    
    <!-- 椅子坐垫 -->
    <rect x="-22" y="25" width="44" height="12" rx="4" fill="#fff" stroke="#94a3b8" stroke-width="2" />
    
    <!-- 椅子靠背 (放在人物后面) -->
    <slot name="back">
      <path d="M -20 25 L -20 0 Q -20 -15 0 -15 Q 20 -15 20 0 L 20 25" fill="#fff" stroke="#94a3b8" stroke-width="2" />
    </slot>
  </g>
</template>

<script setup lang="ts">
defineProps<{
  x: number
  y: number
}>()
</script>
