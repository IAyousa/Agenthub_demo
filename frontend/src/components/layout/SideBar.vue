<template>
  <div class="w-16 h-full bg-[#2e2e2e] flex flex-col items-center py-6 space-y-6">
    <!-- User Avatar -->
    <div class="w-9 h-9 bg-gray-400 rounded-sm mb-2 overflow-hidden">
      <img src="https://api.dicebear.com/7.x/avataaars/svg?seed=Felix" alt="avatar" />
    </div>

    <!-- Nav Icons -->
    <div class="flex flex-col space-y-6 flex-1 text-[#9a9a9a]">
      <div class="cursor-pointer hover:text-[#07c160] transition-colors text-[#07c160]">
        <MessageSquareIcon :size="22" />
      </div>
      <div class="cursor-pointer hover:text-[#07c160] transition-colors">
        <UserIcon :size="22" />
      </div>
      <div class="cursor-pointer hover:text-[#07c160] transition-colors">
        <LayoutGridIcon :size="22" />
      </div>
    </div>

    <!-- Bottom Icons -->
    <div class="flex flex-col space-y-6 text-[#9a9a9a] pb-4">
      <div class="cursor-pointer hover:text-[#07c160] transition-colors">
        <SettingsIcon :size="22" />
      </div>
    </div>
  </div>
</template>

<script setup lang="ts">
import { 
  MessageSquare as MessageSquareIcon, 
  User as UserIcon, 
  LayoutGrid as LayoutGridIcon,
  Settings as SettingsIcon 
} from 'lucide-vue-next'
</script>
