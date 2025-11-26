<template>
  <div class="min-h-screen bg-gray-100">
    <!-- Header -->
    <header class="bg-xh-red text-white shadow-lg">
      <div class="container mx-auto px-4 py-4 flex items-center justify-between">
        <div class="flex items-center">
          <router-link to="/" class="mr-4">
            <svg class="w-6 h-6" fill="none" stroke="currentColor" viewBox="0 0 24 24">
              <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M15 19l-7-7 7-7" />
            </svg>
          </router-link>
          <h1 class="text-xl font-bold">Lệnh sản xuất</h1>
        </div>
        
        <!-- Filter -->
        <select
          v-model="statusFilter"
          class="bg-white bg-opacity-20 text-white border-0 rounded px-3 py-1 text-sm"
        >
          <option value="">Tất cả</option>
          <option value="Not Started">Chờ SX</option>
          <option value="In Process">Đang SX</option>
          <option value="Completed">Hoàn thành</option>
        </select>
      </div>
    </header>

    <!-- Main Content -->
    <main class="container mx-auto px-4 py-6">
      <!-- Loading -->
      <div v-if="loading" class="text-center py-8 text-gray-500">
        Đang tải...
      </div>

      <!-- Empty State -->
      <div v-else-if="workOrders.length === 0" class="text-center py-8 text-gray-500">
        Không có lệnh sản xuất nào
      </div>

      <!-- Work Order List -->
      <div v-else class="space-y-4">
        <router-link
          v-for="wo in workOrders"
          :key="wo.name"
          :to="`/production/orders/${wo.name}`"
          class="block bg-white rounded-lg shadow p-4 hover:shadow-lg transition"
        >
          <div class="flex justify-between items-start">
            <div class="flex-1">
              <div class="text-sm text-gray-500">{{ wo.name }}</div>
              <div class="font-medium text-xh-black">{{ wo.item_name }}</div>
              <div class="text-sm text-gray-600 mt-1">
                {{ wo.produced_qty }} / {{ wo.qty }} sản phẩm
              </div>
            </div>
            
            <!-- Status Badge -->
            <span :class="getStatusClass(wo.status)" class="px-3 py-1 rounded-full text-sm font-medium">
              {{ getStatusLabel(wo.status) }}
            </span>
          </div>

          <!-- Progress Bar -->
          <div class="mt-3">
            <div class="h-2 bg-gray-200 rounded-full overflow-hidden">
              <div 
                class="h-full bg-xh-gold transition-all duration-300"
                :style="{ width: `${wo.progress}%` }"
              ></div>
            </div>
            <div class="text-xs text-gray-500 mt-1 text-right">{{ wo.progress }}%</div>
          </div>
        </router-link>
      </div>
    </main>
  </div>
</template>

<script setup>
import { ref, watch, onMounted } from 'vue'
import { xuanhoaAPI } from '@/api/client'

const workOrders = ref([])
const loading = ref(true)
const statusFilter = ref('')

const loadWorkOrders = async () => {
  loading.value = true
  try {
    workOrders.value = await xuanhoaAPI.getWorkOrders(statusFilter.value || null)
  } catch (e) {
    console.error('Error loading work orders:', e)
  } finally {
    loading.value = false
  }
}

// Status helpers
const getStatusClass = (status) => {
  const classes = {
    'Not Started': 'bg-gray-100 text-gray-600',
    'In Process': 'bg-xh-gold bg-opacity-20 text-yellow-700',
    'Completed': 'bg-green-100 text-green-600',
    'Stopped': 'bg-red-100 text-red-600'
  }
  return classes[status] || 'bg-gray-100 text-gray-600'
}

const getStatusLabel = (status) => {
  const labels = {
    'Not Started': 'Chờ SX',
    'In Process': 'Đang SX',
    'Completed': 'Hoàn thành',
    'Stopped': 'Đã dừng'
  }
  return labels[status] || status
}

// Watch filter change
watch(statusFilter, () => loadWorkOrders())

// Initial load
onMounted(() => loadWorkOrders())
</script>
