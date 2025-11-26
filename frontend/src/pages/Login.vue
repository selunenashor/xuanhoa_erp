<template>
  <div class="min-h-screen bg-gray-100 flex items-center justify-center">
    <div class="bg-white rounded-lg shadow-lg p-8 w-full max-w-md">
      <!-- Logo -->
      <div class="text-center mb-8">
        <div class="w-20 h-20 bg-xh-red rounded-full mx-auto flex items-center justify-center mb-4">
          <span class="text-white text-2xl font-bold">XH</span>
        </div>
        <h1 class="text-2xl font-bold text-xh-black">Xuân Hòa</h1>
        <p class="text-gray-500">Hệ thống quản lý sản xuất</p>
      </div>

      <!-- Login Form -->
      <form @submit.prevent="handleLogin" class="space-y-4">
        <div>
          <label class="block text-sm font-medium text-gray-700 mb-1">Email / Username</label>
          <input
            v-model="form.username"
            type="text"
            required
            class="w-full px-4 py-3 border border-gray-300 rounded-lg focus:outline-none focus:ring-2 focus:ring-xh-red focus:border-transparent"
            placeholder="admin@xuanhoa.com"
          />
        </div>

        <div>
          <label class="block text-sm font-medium text-gray-700 mb-1">Mật khẩu</label>
          <input
            v-model="form.password"
            type="password"
            required
            class="w-full px-4 py-3 border border-gray-300 rounded-lg focus:outline-none focus:ring-2 focus:ring-xh-red focus:border-transparent"
            placeholder="••••••••"
          />
        </div>

        <!-- Error Message -->
        <div v-if="error" class="bg-red-50 border border-red-200 text-red-600 px-4 py-3 rounded-lg text-sm">
          {{ error }}
        </div>

        <button
          type="submit"
          :disabled="loading"
          class="w-full bg-xh-red text-white py-3 rounded-lg font-medium hover:bg-red-700 transition disabled:opacity-50 disabled:cursor-not-allowed"
        >
          <span v-if="loading">Đang đăng nhập...</span>
          <span v-else>Đăng nhập</span>
        </button>
      </form>
    </div>
  </div>
</template>

<script setup>
import { ref, reactive } from 'vue'
import { useRouter } from 'vue-router'
import { useUserStore } from '@/stores/user'

const router = useRouter()
const userStore = useUserStore()

const form = reactive({
  username: '',
  password: ''
})
const loading = ref(false)
const error = ref('')

const handleLogin = async () => {
  error.value = ''
  loading.value = true
  
  try {
    const result = await userStore.login(form.username, form.password)
    if (result.success) {
      router.push('/')
    } else {
      error.value = result.message || 'Đăng nhập thất bại'
    }
  } catch (e) {
    error.value = e.message || 'Đăng nhập thất bại'
  } finally {
    loading.value = false
  }
}
</script>
