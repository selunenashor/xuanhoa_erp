<template>
  <div class="min-h-screen bg-gray-100">
    <!-- Header -->
    <header class="bg-xh-red text-white shadow-lg">
      <div class="container mx-auto px-4 py-4 flex items-center justify-between">
        <h1 class="text-xl font-bold">Xuân Hòa Manufacturing</h1>
        <span class="text-sm opacity-80">Tổng quan</span>
      </div>
    </header>

    <!-- Main Content -->
    <main class="container mx-auto px-4 py-6">
      <!-- KPI Cards -->
      <div class="grid grid-cols-2 md:grid-cols-4 gap-4 mb-6">
        <!-- Work Orders In Process -->
        <div class="bg-white rounded-lg shadow p-4 border-l-4 border-xh-gold">
          <div class="text-sm text-gray-500">Đang sản xuất</div>
          <div class="text-2xl font-bold text-xh-black">{{ kpi.work_orders?.['In Process'] || 0 }}</div>
        </div>
        
        <!-- Work Orders Not Started -->
        <div class="bg-white rounded-lg shadow p-4 border-l-4 border-gray-400">
          <div class="text-sm text-gray-500">Chờ sản xuất</div>
          <div class="text-2xl font-bold text-xh-black">{{ kpi.work_orders?.['Not Started'] || 0 }}</div>
        </div>
        
        <!-- Today's Receipts -->
        <div class="bg-white rounded-lg shadow p-4 border-l-4 border-green-500">
          <div class="text-sm text-gray-500">Nhập kho hôm nay</div>
          <div class="text-2xl font-bold text-xh-black">{{ kpi.receipts_today || 0 }}</div>
        </div>
        
        <!-- Stock Value -->
        <div class="bg-white rounded-lg shadow p-4 border-l-4 border-blue-500">
          <div class="text-sm text-gray-500">Giá trị tồn kho</div>
          <div class="text-lg font-bold text-xh-black">{{ formatCurrency(kpi.stock_value) }}</div>
        </div>
      </div>

      <!-- Quick Actions -->
      <h2 class="text-lg font-semibold text-xh-black mb-4">Thao tác nhanh</h2>
      <div class="grid grid-cols-2 gap-4">
        <router-link 
          to="/stock/receipt" 
          class="bg-white rounded-lg shadow p-6 flex flex-col items-center hover:shadow-lg transition"
        >
          <div class="w-12 h-12 bg-green-100 rounded-full flex items-center justify-center mb-3">
            <svg class="w-6 h-6 text-green-600" fill="none" stroke="currentColor" viewBox="0 0 24 24">
              <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M12 4v16m8-8H4" />
            </svg>
          </div>
          <span class="font-medium text-xh-black">Nhập kho</span>
        </router-link>

        <router-link 
          to="/stock/issue" 
          class="bg-white rounded-lg shadow p-6 flex flex-col items-center hover:shadow-lg transition"
        >
          <div class="w-12 h-12 bg-red-100 rounded-full flex items-center justify-center mb-3">
            <svg class="w-6 h-6 text-red-600" fill="none" stroke="currentColor" viewBox="0 0 24 24">
              <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M20 12H4" />
            </svg>
          </div>
          <span class="font-medium text-xh-black">Xuất kho</span>
        </router-link>

        <router-link 
          to="/production/orders" 
          class="bg-white rounded-lg shadow p-6 flex flex-col items-center hover:shadow-lg transition"
        >
          <div class="w-12 h-12 bg-xh-gold bg-opacity-20 rounded-full flex items-center justify-center mb-3">
            <svg class="w-6 h-6 text-xh-gold" fill="none" stroke="currentColor" viewBox="0 0 24 24">
              <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M19 21V5a2 2 0 00-2-2H7a2 2 0 00-2 2v16m14 0h2m-2 0h-5m-9 0H3m2 0h5M9 7h1m-1 4h1m4-4h1m-1 4h1m-5 10v-5a1 1 0 011-1h2a1 1 0 011 1v5m-4 0h4" />
            </svg>
          </div>
          <span class="font-medium text-xh-black">Lệnh sản xuất</span>
        </router-link>

        <div class="bg-white rounded-lg shadow p-6 flex flex-col items-center opacity-50">
          <div class="w-12 h-12 bg-gray-100 rounded-full flex items-center justify-center mb-3">
            <svg class="w-6 h-6 text-gray-400" fill="none" stroke="currentColor" viewBox="0 0 24 24">
              <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M9 17v-2m3 2v-4m3 4v-6m2 10H7a2 2 0 01-2-2V5a2 2 0 012-2h5.586a1 1 0 01.707.293l5.414 5.414a1 1 0 01.293.707V19a2 2 0 01-2 2z" />
            </svg>
          </div>
          <span class="font-medium text-gray-400">Báo cáo</span>
          <span class="text-xs text-gray-400">(Sắp có)</span>
        </div>
      </div>
    </main>
  </div>
</template>

<script setup>
import { ref, onMounted } from 'vue'
import { xuanhoaAPI } from '@/api/client'

const kpi = ref({})
const loading = ref(true)

const formatCurrency = (value) => {
  if (!value) return '0 ₫'
  return new Intl.NumberFormat('vi-VN', { 
    style: 'currency', 
    currency: 'VND',
    maximumFractionDigits: 0
  }).format(value)
}

onMounted(async () => {
  try {
    kpi.value = await xuanhoaAPI.getDashboardKPI()
  } catch (error) {
    console.error('Error loading KPI:', error)
  } finally {
    loading.value = false
  }
})
</script>
