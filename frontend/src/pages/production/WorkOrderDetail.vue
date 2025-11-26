<template>
  <div class="space-y-6">
    <div class="flex items-center gap-4">
      <router-link 
        to="/production/orders"
        class="p-2 text-gray-500 hover:text-gray-700 hover:bg-gray-100 rounded-lg transition-colors"
      >
        <svg class="w-5 h-5" fill="none" stroke="currentColor" viewBox="0 0 24 24">
          <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M15 19l-7-7 7-7" />
        </svg>
      </router-link>
      <h2 class="text-xl font-semibold text-gray-800">Chi tiết lệnh sản xuất: {{ $route.params.name }}</h2>
    </div>
    
    <div class="bg-white rounded-xl p-8 shadow-sm border border-gray-100 text-center">
      <div class="w-16 h-16 bg-gray-100 rounded-full mx-auto mb-4 flex items-center justify-center">
        <svg class="w-8 h-8 text-gray-400" fill="none" stroke="currentColor" viewBox="0 0 24 24">
          <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" 
                d="M9 12h6m-6 4h6m2 5H7a2 2 0 01-2-2V5a2 2 0 012-2h5.586a1 1 0 01.707.293l5.414 5.414a1 1 0 01.293.707V19a2 2 0 01-2 2z" />
        </svg>
      </div>
      <h3 class="text-lg font-medium text-gray-800 mb-2">Chức năng đang phát triển</h3>
      <p class="text-gray-500">Trang Chi tiết lệnh sản xuất sẽ sớm được hoàn thiện.</p>
    </div>
  </div>
</template>

<script setup>
// Placeholder - will implement later
</script>
