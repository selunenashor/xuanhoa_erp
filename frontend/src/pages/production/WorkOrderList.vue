<template>
  <div class="h-full">
    <div class="p-6 overflow-auto">
      <div class="max-w-6xl mx-auto">
        <!-- Header -->
        <div class="flex flex-col md:flex-row md:items-center md:justify-between gap-4 mb-6">
          <div>
            <h1 class="text-2xl font-bold text-gray-900">Lệnh sản xuất</h1>
            <p class="text-gray-600">Quản lý các lệnh sản xuất</p>
          </div>
          <router-link
            to="/production/orders/create"
            class="inline-flex items-center gap-2 px-4 py-2 text-white bg-primary rounded-lg hover:bg-primary-dark transition-colors"
          >
            <svg xmlns="http://www.w3.org/2000/svg" class="h-5 w-5" fill="none" viewBox="0 0 24 24" stroke="currentColor">
              <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M12 4v16m8-8H4" />
            </svg>
            Tạo lệnh mới
          </router-link>
        </div>

        <!-- Filters -->
        <div class="bg-white rounded-lg shadow p-4 mb-6">
          <div class="flex flex-wrap gap-4">
            <!-- Status Filter -->
            <div class="flex-1 min-w-[200px]">
              <label class="block text-sm font-medium text-gray-700 mb-1">Trạng thái</label>
              <select
                v-model="filters.status"
                @change="loadWorkOrders"
                class="w-full px-3 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-primary focus:border-primary"
              >
                <option value="">Tất cả</option>
                <option value="Draft">Chờ duyệt</option>
                <option value="Not Started">Chưa bắt đầu</option>
                <option value="In Process">Đang sản xuất</option>
                <option value="Completed">Hoàn thành</option>
                <option value="Stopped">Đã dừng</option>
              </select>
            </div>

            <!-- Refresh Button -->
            <div class="flex items-end">
              <button
                @click="loadWorkOrders"
                class="px-4 py-2 border border-gray-300 rounded-lg hover:bg-gray-50 flex items-center gap-2"
              >
                <svg xmlns="http://www.w3.org/2000/svg" class="h-5 w-5" fill="none" viewBox="0 0 24 24" stroke="currentColor">
                  <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M4 4v5h.582m15.356 2A8.001 8.001 0 004.582 9m0 0H9m11 11v-5h-.581m0 0a8.003 8.003 0 01-15.357-2m15.357 2H15" />
                </svg>
                Làm mới
              </button>
            </div>
          </div>
        </div>

        <!-- Loading -->
        <div v-if="loading" class="bg-white rounded-lg shadow p-8 text-center">
          <svg class="animate-spin h-8 w-8 mx-auto text-primary" xmlns="http://www.w3.org/2000/svg" fill="none" viewBox="0 0 24 24">
            <circle class="opacity-25" cx="12" cy="12" r="10" stroke="currentColor" stroke-width="4"></circle>
            <path class="opacity-75" fill="currentColor" d="M4 12a8 8 0 018-8V0C5.373 0 0 5.373 0 12h4zm2 5.291A7.962 7.962 0 014 12H0c0 3.042 1.135 5.824 3 7.938l3-2.647z"></path>
          </svg>
          <p class="mt-2 text-gray-500">Đang tải...</p>
        </div>

        <!-- Empty State -->
        <div v-else-if="workOrders.length === 0" class="bg-white rounded-lg shadow p-8 text-center">
          <div class="w-16 h-16 bg-gray-100 rounded-full mx-auto mb-4 flex items-center justify-center">
            <svg class="w-8 h-8 text-gray-400" fill="none" stroke="currentColor" viewBox="0 0 24 24">
              <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" 
                    d="M19.428 15.428a2 2 0 00-1.022-.547l-2.387-.477a6 6 0 00-3.86.517l-.318.158a6 6 0 01-3.86.517L6.05 15.21a2 2 0 00-1.806.547M8 4h8l-1 1v5.172a2 2 0 00.586 1.414l5 5c1.26 1.26.367 3.414-1.415 3.414H4.828c-1.782 0-2.674-2.154-1.414-3.414l5-5A2 2 0 009 10.172V5L8 4z" />
            </svg>
          </div>
          <h3 class="text-lg font-medium text-gray-800 mb-2">Chưa có lệnh sản xuất</h3>
          <p class="text-gray-500 mb-4">Bắt đầu bằng việc tạo lệnh sản xuất mới</p>
          <router-link
            to="/production/orders/create"
            class="inline-flex items-center gap-2 px-4 py-2 text-white bg-primary rounded-lg hover:bg-primary-dark"
          >
            <svg xmlns="http://www.w3.org/2000/svg" class="h-5 w-5" fill="none" viewBox="0 0 24 24" stroke="currentColor">
              <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M12 4v16m8-8H4" />
            </svg>
            Tạo lệnh mới
          </router-link>
        </div>

        <!-- Work Orders Table -->
        <div v-else class="bg-white rounded-lg shadow overflow-hidden">
          <div class="overflow-x-auto">
            <table class="w-full">
              <thead class="bg-gray-50">
                <tr>
                  <th class="px-4 py-3 text-left text-sm font-medium text-gray-600">Mã lệnh</th>
                  <th class="px-4 py-3 text-left text-sm font-medium text-gray-600">Sản phẩm</th>
                  <th class="px-4 py-3 text-center text-sm font-medium text-gray-600">Số lượng</th>
                  <th class="px-4 py-3 text-center text-sm font-medium text-gray-600">Tiến độ</th>
                  <th class="px-4 py-3 text-center text-sm font-medium text-gray-600">Trạng thái</th>
                  <th class="px-4 py-3 text-left text-sm font-medium text-gray-600">Ngày tạo</th>
                  <th class="px-4 py-3 text-center text-sm font-medium text-gray-600">Thao tác</th>
                </tr>
              </thead>
              <tbody class="divide-y divide-gray-200">
                <tr 
                  v-for="order in workOrders" 
                  :key="order.name"
                  @click="goToDetail(order.name)"
                  class="hover:bg-gray-50 cursor-pointer transition-colors"
                >
                  <td class="px-4 py-3">
                    <span class="font-medium text-primary">{{ order.name }}</span>
                  </td>
                  <td class="px-4 py-3">
                    <div class="font-medium text-gray-900">{{ order.production_item }}</div>
                    <div class="text-sm text-gray-500">{{ order.item_name }}</div>
                  </td>
                  <td class="px-4 py-3 text-center">
                    <span class="font-medium">{{ formatNumber(order.produced_qty) }}</span>
                    <span class="text-gray-400"> / {{ formatNumber(order.qty) }}</span>
                  </td>
                  <td class="px-4 py-3">
                    <div class="flex items-center justify-center gap-2">
                      <div class="flex-1 max-w-[100px] bg-gray-200 rounded-full h-2">
                        <div 
                          class="h-2 rounded-full transition-all"
                          :class="getProgressColor(order.progress)"
                          :style="{ width: order.progress + '%' }"
                        ></div>
                      </div>
                      <span class="text-sm text-gray-600 w-12 text-right">{{ order.progress }}%</span>
                    </div>
                  </td>
                  <td class="px-4 py-3 text-center">
                    <span 
                      :class="[
                        'px-2 py-1 rounded-full text-xs font-medium',
                        getStatusClass(order.status_color)
                      ]"
                    >
                      {{ order.status_display }}
                    </span>
                  </td>
                  <td class="px-4 py-3 text-sm text-gray-500">
                    {{ formatDate(order.creation) }}
                  </td>
                  <td class="px-4 py-3 text-center" @click.stop>
                    <div class="flex justify-center gap-2">
                      <button
                        @click="goToDetail(order.name)"
                        class="p-1.5 text-gray-400 hover:text-primary hover:bg-gray-100 rounded transition-colors"
                        title="Xem chi tiết"
                      >
                        <svg xmlns="http://www.w3.org/2000/svg" class="h-5 w-5" fill="none" viewBox="0 0 24 24" stroke="currentColor">
                          <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M15 12a3 3 0 11-6 0 3 3 0 016 0z" />
                          <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M2.458 12C3.732 7.943 7.523 5 12 5c4.478 0 8.268 2.943 9.542 7-1.274 4.057-5.064 7-9.542 7-4.477 0-8.268-2.943-9.542-7z" />
                        </svg>
                      </button>
                    </div>
                  </td>
                </tr>
              </tbody>
            </table>
          </div>

          <!-- Pagination -->
          <div v-if="pagination.total_pages > 1" class="px-4 py-3 border-t border-gray-200 flex items-center justify-between">
            <div class="text-sm text-gray-600">
              Hiển thị {{ (pagination.page - 1) * pagination.page_size + 1 }} - 
              {{ Math.min(pagination.page * pagination.page_size, pagination.total) }} 
              / {{ pagination.total }} kết quả
            </div>
            <div class="flex gap-2">
              <button
                @click="goToPage(pagination.page - 1)"
                :disabled="pagination.page <= 1"
                class="px-3 py-1 border rounded-lg text-sm disabled:opacity-50 disabled:cursor-not-allowed hover:bg-gray-50"
              >
                Trước
              </button>
              <span class="px-3 py-1 text-sm text-gray-600">
                Trang {{ pagination.page }} / {{ pagination.total_pages }}
              </span>
              <button
                @click="goToPage(pagination.page + 1)"
                :disabled="pagination.page >= pagination.total_pages"
                class="px-3 py-1 border rounded-lg text-sm disabled:opacity-50 disabled:cursor-not-allowed hover:bg-gray-50"
              >
                Sau
              </button>
            </div>
          </div>
        </div>
      </div>
    </div>

    <!-- Toast -->
    <div
      v-if="toast.show"
      :class="[
        'fixed bottom-4 right-4 px-4 py-3 rounded-lg shadow-lg flex items-center gap-2 z-50',
        toast.type === 'success' ? 'bg-green-500 text-white' : 'bg-red-500 text-white'
      ]"
    >
      {{ toast.message }}
    </div>
  </div>
</template>

<script setup>
import { ref, reactive, onMounted } from 'vue'
import { useRouter } from 'vue-router'
import { workOrderAPI } from '@/api'

const router = useRouter()

// State
const loading = ref(false)
const workOrders = ref([])
const pagination = reactive({
  page: 1,
  page_size: 20,
  total: 0,
  total_pages: 1
})
const filters = reactive({
  status: ''
})

// Toast
const toast = reactive({
  show: false,
  type: 'success',
  message: ''
})

// Methods
const formatNumber = (num) => {
  if (!num) return '0'
  return new Intl.NumberFormat('vi-VN').format(num)
}

const formatDate = (dateStr) => {
  if (!dateStr) return ''
  const date = new Date(dateStr)
  return date.toLocaleDateString('vi-VN', { day: '2-digit', month: '2-digit', year: 'numeric' })
}

const getProgressColor = (progress) => {
  if (progress >= 100) return 'bg-success'
  if (progress >= 50) return 'bg-primary'
  if (progress > 0) return 'bg-warning'
  return 'bg-gray-300'
}

const getStatusClass = (color) => {
  const classes = {
    'warning': 'bg-warning/20 text-warning',
    'info': 'bg-info/20 text-info',
    'primary': 'bg-primary/20 text-primary',
    'success': 'bg-success/20 text-success',
    'error': 'bg-error/20 text-error',
    'gray': 'bg-gray-200 text-gray-600'
  }
  return classes[color] || classes['gray']
}

const showToast = (type, message) => {
  toast.type = type
  toast.message = message
  toast.show = true
  setTimeout(() => { toast.show = false }, 3000)
}

const loadWorkOrders = async () => {
  loading.value = true
  try {
    const params = {
      page: pagination.page,
      limit: pagination.page_size
    }
    
    if (filters.status) {
      params.status = filters.status
    }
    
    const result = await workOrderAPI.getList(params)
    
    workOrders.value = result.data || []
    pagination.total = result.total || 0
    pagination.total_pages = result.total_pages || 1
    pagination.page = result.page || 1
    pagination.page_size = result.page_size || 20
  } catch (error) {
    console.error('Error loading work orders:', error)
    showToast('error', 'Không thể tải danh sách lệnh sản xuất')
  } finally {
    loading.value = false
  }
}

const goToPage = (page) => {
  pagination.page = page
  loadWorkOrders()
}

const goToDetail = (name) => {
  router.push(`/production/orders/${name}`)
}

// Initialize
onMounted(() => {
  loadWorkOrders()
})
</script>

<style scoped>
.bg-primary { background-color: #055568; }
.bg-primary-dark { background-color: #044454; }
.text-primary { color: #055568; }
.text-info { color: #2090AC; }
.text-success { color: #33CAB1; }
.text-warning { color: #FF9800; }
.text-error { color: #F12B2B; }
.bg-primary\/20 { background-color: rgba(5, 85, 104, 0.2); }
.bg-info\/20 { background-color: rgba(32, 144, 172, 0.2); }
.bg-success\/20 { background-color: rgba(51, 202, 177, 0.2); }
.bg-warning\/20 { background-color: rgba(255, 152, 0, 0.2); }
.bg-error\/20 { background-color: rgba(241, 43, 43, 0.2); }
.ring-primary { --tw-ring-color: #055568; }
.hover\:bg-primary-dark:hover { background-color: #044454; }
.focus\:ring-primary:focus { --tw-ring-color: #055568; }
.focus\:border-primary:focus { border-color: #055568; }
</style>
