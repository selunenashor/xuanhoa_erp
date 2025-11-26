<script setup>
/**
 * Xuân Hòa Manufacturing - Main App Component
 * Uses Vue Router for navigation
 */
import { onMounted } from 'vue'
import { useRouter } from 'vue-router'
import { useUserStore } from './stores/user'

const router = useRouter()
const userStore = useUserStore()

onMounted(async () => {
  // Check if user is logged in on app start
  await userStore.checkAuth()
})
</script>

<template>
  <router-view />
</template>

<style>
/* App-level styles handled by Tailwind in style.css */
</style>
