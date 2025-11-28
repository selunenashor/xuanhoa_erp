<template>
  <div class="min-h-[60vh] flex flex-col items-center justify-center">
    <div class="text-center">
      <div class="text-8xl font-bold text-gray-200 mb-4">404</div>
      <h1 class="text-2xl font-bold text-gray-800 mb-2">Không tìm thấy trang</h1>
      <p class="text-gray-500 mb-6">Trang bạn đang tìm kiếm không tồn tại hoặc đã bị xóa.</p>
      <router-link 
        to="/"
        class="inline-flex items-center gap-2 px-6 py-3 bg-primary text-white rounded-lg 
               hover:bg-primary-light transition-colors"
      >
        <svg class="w-5 h-5" fill="none" stroke="currentColor" viewBox="0 0 24 24">
          <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" 
                d="M3 12l2-2m0 0l7-7 7 7M5 10v10a1 1 0 001 1h3m10-11l2 2m-2-2v10a1 1 0 01-1 1h-3m-6 0a1 1 0 001-1v-4a1 1 0 011-1h2a1 1 0 011 1v4a1 1 0 001 1m-6 0h6" />
        </svg>
        <span>Về trang chủ</span>
      </router-link>
    </div>
  </div>
</template>

<script setup>
// No logic needed for 404 page
</script>
