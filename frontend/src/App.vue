<script setup>
/**
 * Manufacturing App - Main App Component
 * Uses Vue Router for navigation
 */
import { onMounted, ref } from 'vue'
import { useUserStore } from './stores/user'

const userStore = useUserStore()
const isInitialized = ref(false)

onMounted(async () => {
  // Initialize user store on app start
  await userStore.init()
  isInitialized.value = true
})
</script>

<template>
  <!-- Loading state while initializing -->
  <div v-if="!isInitialized" class="min-h-screen flex items-center justify-center bg-gray-50">
    <div class="text-center">
      <div class="w-12 h-12 border-4 border-primary border-t-transparent rounded-full animate-spin mx-auto mb-4"></div>
      <p class="text-gray-500">Đang tải...</p>
    </div>
  </div>
  
  <!-- App content -->
  <router-view v-else />
</template>

<style>
/* App-level styles handled by Tailwind in style.css */
</style>
