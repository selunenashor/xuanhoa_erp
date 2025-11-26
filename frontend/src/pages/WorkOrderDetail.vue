<template>
  <div class="min-h-screen bg-gray-100">
    <!-- Header -->
    <header class="bg-xh-red text-white shadow-lg">
      <div class="container mx-auto px-4 py-4 flex items-center">
        <router-link to="/production/orders" class="mr-4">
          <svg class="w-6 h-6" fill="none" stroke="currentColor" viewBox="0 0 24 24">
            <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M15 19l-7-7 7-7" />
          </svg>
        </router-link>
        <div>
          <div class="text-sm opacity-75">Chi tiết lệnh sản xuất</div>
          <h1 class="text-xl font-bold">{{ workOrder.name }}</h1>
        </div>
      </div>
    </header>

    <!-- Main Content -->
    <main class="container mx-auto px-4 py-6">
      <!-- Loading -->
      <div v-if="loading" class="text-center py-8 text-gray-500">
        Đang tải...
      </div>

      <!-- Work Order Details -->
      <div v-else class="space-y-6">
        <!-- Status Card -->
        <div class="bg-white rounded-lg shadow p-6">
          <div class="flex justify-between items-center mb-4">
            <h2 class="text-lg font-bold text-xh-black">Trạng thái</h2>
            <span :class="getStatusClass(workOrder.status)" class="px-3 py-1 rounded-full text-sm font-medium">
              {{ getStatusLabel(workOrder.status) }}
            </span>
          </div>

          <!-- Progress -->
          <div class="mb-4">
            <div class="flex justify-between text-sm text-gray-600 mb-1">
              <span>Tiến độ</span>
              <span>{{ workOrder.produced_qty }} / {{ workOrder.qty }} sản phẩm</span>
            </div>
            <div class="h-4 bg-gray-200 rounded-full overflow-hidden">
              <div 
                class="h-full bg-xh-gold transition-all duration-300"
                :style="{ width: `${workOrder.progress}%` }"
              ></div>
            </div>
          </div>
        </div>

        <!-- Product Info Card -->
        <div class="bg-white rounded-lg shadow p-6">
          <h2 class="text-lg font-bold text-xh-black mb-4">Thông tin sản phẩm</h2>
          
          <div class="space-y-3">
            <div class="flex justify-between">
              <span class="text-gray-600">Mã SP</span>
              <span class="font-medium">{{ workOrder.production_item }}</span>
            </div>
            <div class="flex justify-between">
              <span class="text-gray-600">Tên SP</span>
              <span class="font-medium">{{ workOrder.item_name }}</span>
            </div>
            <div class="flex justify-between">
              <span class="text-gray-600">SL yêu cầu</span>
              <span class="font-medium">{{ workOrder.qty }}</span>
            </div>
            <div class="flex justify-between">
              <span class="text-gray-600">Kho thành phẩm</span>
              <span class="font-medium">{{ workOrder.fg_warehouse }}</span>
            </div>
          </div>
        </div>

        <!-- BOM Info (if available) -->
        <div v-if="workOrder.bom_no" class="bg-white rounded-lg shadow p-6">
          <h2 class="text-lg font-bold text-xh-black mb-4">BOM: {{ workOrder.bom_no }}</h2>
          
          <div v-if="bomItems.length > 0" class="space-y-2">
            <div 
              v-for="item in bomItems" 
              :key="item.item_code"
              class="flex justify-between items-center py-2 border-b border-gray-100 last:border-0"
            >
              <div>
                <div class="font-medium text-sm">{{ item.item_name }}</div>
                <div class="text-xs text-gray-500">{{ item.item_code }}</div>
              </div>
              <div class="text-right">
                <div class="font-medium">{{ item.qty_required }}</div>
                <div class="text-xs text-gray-500">{{ item.uom }}</div>
              </div>
            </div>
          </div>
        </div>

        <!-- Action Buttons -->
        <div class="space-y-3">
          <!-- Start Production -->
          <button
            v-if="workOrder.status === 'Not Started'"
            @click="startProduction"
            :disabled="actionLoading"
            class="w-full bg-xh-gold text-xh-black font-bold py-4 rounded-lg shadow hover:bg-opacity-90 transition disabled:opacity-50"
          >
            {{ actionLoading ? 'Đang xử lý...' : 'Bắt đầu sản xuất' }}
          </button>

          <!-- Complete Production -->
          <template v-if="workOrder.status === 'In Process'">
            <div class="bg-white rounded-lg shadow p-4">
              <label class="block text-sm font-medium text-gray-700 mb-2">
                Số lượng hoàn thành
              </label>
              <input
                v-model.number="completeQty"
                type="number"
                min="1"
                :max="workOrder.qty - workOrder.produced_qty"
                class="w-full border border-gray-300 rounded-lg px-4 py-3 focus:outline-none focus:ring-2 focus:ring-xh-red"
                placeholder="Nhập số lượng"
              />
            </div>
            
            <button
              @click="completeProduction"
              :disabled="actionLoading || !completeQty"
              class="w-full bg-green-600 text-white font-bold py-4 rounded-lg shadow hover:bg-green-700 transition disabled:opacity-50"
            >
              {{ actionLoading ? 'Đang xử lý...' : 'Hoàn thành sản xuất' }}
            </button>
          </template>

          <!-- Completed State -->
          <div v-if="workOrder.status === 'Completed'" class="bg-green-50 border border-green-200 rounded-lg p-4 text-center">
            <svg class="w-12 h-12 text-green-500 mx-auto mb-2" fill="none" stroke="currentColor" viewBox="0 0 24 24">
              <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M9 12l2 2 4-4m6 2a9 9 0 11-18 0 9 9 0 0118 0z" />
            </svg>
            <div class="text-green-700 font-medium">Lệnh sản xuất đã hoàn thành</div>
          </div>
        </div>
      </div>

      <!-- Success Message -->
      <div 
        v-if="successMessage"
        class="fixed bottom-4 left-4 right-4 bg-green-500 text-white px-4 py-3 rounded-lg shadow-lg text-center"
      >
        {{ successMessage }}
      </div>

      <!-- Error Message -->
      <div 
        v-if="errorMessage"
        class="fixed bottom-4 left-4 right-4 bg-red-500 text-white px-4 py-3 rounded-lg shadow-lg text-center"
      >
        {{ errorMessage }}
      </div>
    </main>
  </div>
</template>

<script setup>
import { ref, onMounted } from 'vue'
import { useRoute, useRouter } from 'vue-router'
import { xuanhoaAPI } from '@/api/client'

const route = useRoute()
const router = useRouter()

const workOrder = ref({})
const bomItems = ref([])
const loading = ref(true)
const actionLoading = ref(false)
const completeQty = ref(null)
const successMessage = ref('')
const errorMessage = ref('')

// Load work order details
const loadWorkOrder = async () => {
  loading.value = true
  try {
    const woName = route.params.name
    workOrder.value = await xuanhoaAPI.getWorkOrder(woName)
    
    // Load BOM items if available
    if (workOrder.value.bom_no) {
      bomItems.value = await xuanhoaAPI.getBOMItems(workOrder.value.bom_no)
    }
  } catch (e) {
    console.error('Error loading work order:', e)
    errorMessage.value = 'Không thể tải thông tin lệnh sản xuất'
  } finally {
    loading.value = false
  }
}

// Start production
const startProduction = async () => {
  actionLoading.value = true
  errorMessage.value = ''
  try {
    await xuanhoaAPI.startWorkOrder(workOrder.value.name)
    successMessage.value = 'Đã bắt đầu sản xuất!'
    setTimeout(() => {
      successMessage.value = ''
      loadWorkOrder()
    }, 2000)
  } catch (e) {
    errorMessage.value = e.message || 'Lỗi khi bắt đầu sản xuất'
    setTimeout(() => errorMessage.value = '', 3000)
  } finally {
    actionLoading.value = false
  }
}

// Complete production
const completeProduction = async () => {
  if (!completeQty.value) return
  
  actionLoading.value = true
  errorMessage.value = ''
  try {
    await xuanhoaAPI.completeWorkOrder(workOrder.value.name, completeQty.value)
    successMessage.value = `Đã hoàn thành ${completeQty.value} sản phẩm!`
    setTimeout(() => {
      successMessage.value = ''
      completeQty.value = null
      loadWorkOrder()
    }, 2000)
  } catch (e) {
    errorMessage.value = e.message || 'Lỗi khi hoàn thành sản xuất'
    setTimeout(() => errorMessage.value = '', 3000)
  } finally {
    actionLoading.value = false
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
    'Not Started': 'Chờ sản xuất',
    'In Process': 'Đang sản xuất',
    'Completed': 'Hoàn thành',
    'Stopped': 'Đã dừng'
  }
  return labels[status] || status
}

onMounted(() => loadWorkOrder())
</script>
