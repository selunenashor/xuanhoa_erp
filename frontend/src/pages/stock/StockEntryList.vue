<template>
  <div class="space-y-6">
    <!-- Header -->
    <div class="flex flex-col sm:flex-row sm:items-center sm:justify-between gap-4">
      <div>
        <h1 class="text-2xl font-bold text-gray-900">Danh sách phiếu kho</h1>
        <p class="text-gray-600">Quản lý và tìm kiếm phiếu nhập/xuất kho</p>
      </div>
    </div>

    <!-- Filters -->
    <div class="bg-white rounded-lg shadow p-4">
      <div class="grid grid-cols-1 md:grid-cols-5 gap-4">
        <!-- Search -->
        <div class="md:col-span-2">
          <label class="block text-sm font-medium text-gray-700 mb-1">Tìm kiếm</label>
          <div class="relative">
            <input
              type="text"
              v-model="filters.search"
              @input="debouncedSearch"
              placeholder="Nhập mã phiếu..."
              class="w-full pl-10 pr-4 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-primary focus:border-primary"
            />
            <svg xmlns="http://www.w3.org/2000/svg" class="h-5 w-5 text-gray-400 absolute left-3 top-1/2 -translate-y-1/2" fill="none" viewBox="0 0 24 24" stroke="currentColor">
              <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M21 21l-6-6m2-5a7 7 0 11-14 0 7 7 0 0114 0z" />
            </svg>
          </div>
        </div>

        <!-- Entry Type Filter -->
        <div>
          <label class="block text-sm font-medium text-gray-700 mb-1">Loại phiếu</label>
          <select
            v-model="filters.stock_entry_type"
            @change="onFilterChange"
            class="w-full px-3 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-primary focus:border-primary"
          >
            <option value="">Tất cả loại</option>
            <option value="Material Receipt">Nhập kho</option>
            <option value="Material Issue">Xuất kho</option>
            <option value="Material Transfer">Chuyển kho</option>
            <option value="Manufacture">Sản xuất</option>
            <option value="Repack">Đóng gói lại</option>
          </select>
        </div>

        <!-- From Date -->
        <div>
          <label class="block text-sm font-medium text-gray-700 mb-1">Từ ngày</label>
          <input
            type="date"
            v-model="filters.from_date"
            @change="onFilterChange"
            class="w-full px-3 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-primary focus:border-primary"
          />
        </div>

        <!-- To Date -->
        <div>
          <label class="block text-sm font-medium text-gray-700 mb-1">Đến ngày</label>
          <input
            type="date"
            v-model="filters.to_date"
            @change="onFilterChange"
            class="w-full px-3 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-primary focus:border-primary"
          />
        </div>
      </div>
    </div>

    <!-- Results -->
    <div class="bg-white rounded-lg shadow">
      <!-- Loading -->
      <div v-if="loading" class="flex justify-center py-12">
        <svg class="animate-spin h-8 w-8 text-primary" xmlns="http://www.w3.org/2000/svg" fill="none" viewBox="0 0 24 24">
          <circle class="opacity-25" cx="12" cy="12" r="10" stroke="currentColor" stroke-width="4"></circle>
          <path class="opacity-75" fill="currentColor" d="M4 12a8 8 0 018-8V0C5.373 0 0 5.373 0 12h4zm2 5.291A7.962 7.962 0 014 12H0c0 3.042 1.135 5.824 3 7.938l3-2.647z"></path>
        </svg>
      </div>

      <!-- Empty state -->
      <div v-else-if="entries.length === 0" class="text-center py-12">
        <svg xmlns="http://www.w3.org/2000/svg" class="h-12 w-12 mx-auto text-gray-400 mb-4" fill="none" viewBox="0 0 24 24" stroke="currentColor">
          <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M20 7l-8-4-8 4m16 0l-8 4m8-4v10l-8 4m0-10L4 7m8 4v10M4 7v10l8 4" />
        </svg>
        <h3 class="text-lg font-medium text-gray-900 mb-1">Không tìm thấy phiếu nào</h3>
        <p class="text-gray-500">Thử thay đổi bộ lọc tìm kiếm</p>
      </div>

      <!-- Table -->
      <div v-else class="overflow-x-auto">
        <table class="min-w-full divide-y divide-gray-200">
          <thead class="bg-gray-50">
            <tr>
              <th class="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
                Mã phiếu
              </th>
              <th class="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
                Loại phiếu
              </th>
              <th class="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
                Ngày
              </th>
              <th class="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
                Kho
              </th>
              <th class="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
                Số SP
              </th>
              <th class="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
                Tổng giá trị
              </th>
              <th class="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
                Trạng thái
              </th>
              <th class="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
                Người tạo
              </th>
            </tr>
          </thead>
          <tbody class="bg-white divide-y divide-gray-200">
            <tr 
              v-for="entry in entries" 
              :key="entry.name"
              class="hover:bg-gray-50 cursor-pointer"
              @click="viewDetail(entry.name)"
            >
              <td class="px-6 py-4 whitespace-nowrap">
                <span class="text-sm font-medium text-primary">{{ entry.name }}</span>
              </td>
              <td class="px-6 py-4 whitespace-nowrap">
                <span
                  :class="[
                    'px-2 py-1 text-xs rounded-full',
                    getEntryTypeClass(entry.stock_entry_type)
                  ]"
                >
                  {{ getEntryTypeLabel(entry.stock_entry_type) }}
                </span>
              </td>
              <td class="px-6 py-4 whitespace-nowrap text-sm text-gray-500">
                {{ formatDate(entry.posting_date) }}
              </td>
              <td class="px-6 py-4 whitespace-nowrap text-sm text-gray-500">
                {{ getWarehouseDisplay(entry) }}
              </td>
              <td class="px-6 py-4 whitespace-nowrap text-sm text-gray-500">
                {{ entry.item_count || entry.items?.length || 0 }}
              </td>
              <td class="px-6 py-4 whitespace-nowrap text-sm text-gray-900 font-medium">
                {{ formatNumber(getTotalValue(entry)) }}
              </td>
              <td class="px-6 py-4 whitespace-nowrap">
                <span
                  :class="[
                    'px-2 py-1 text-xs rounded-full',
                    entry.docstatus === 1 
                      ? 'bg-green-100 text-green-700' 
                      : entry.docstatus === 2 
                        ? 'bg-red-100 text-red-700'
                        : 'bg-yellow-100 text-yellow-700'
                  ]"
                >
                  {{ getStatusText(entry.docstatus) }}
                </span>
              </td>
              <td class="px-6 py-4 whitespace-nowrap text-sm text-gray-500">
                {{ entry.owner_name }}
              </td>
            </tr>
          </tbody>
        </table>
      </div>

      <!-- Pagination -->
      <div v-if="entries.length > 0" class="px-6 py-4 border-t border-gray-200">
        <div class="flex flex-col sm:flex-row items-center justify-between gap-4">
          <!-- Info -->
          <div class="text-sm text-gray-500">
            Hiển thị {{ startIndex + 1 }} - {{ endIndex }} / {{ pagination.total }} phiếu
          </div>
          
          <!-- Page Size Select -->
          <div class="flex items-center gap-2">
            <span class="text-sm text-gray-500">Hiển thị:</span>
            <select
              v-model="pagination.pageSize"
              @change="changePageSize"
              class="px-2 py-1 border border-gray-300 rounded-lg text-sm focus:ring-2 focus:ring-primary focus:border-primary"
            >
              <option :value="10">10</option>
              <option :value="20">20</option>
              <option :value="50">50</option>
              <option :value="100">100</option>
            </select>
            <span class="text-sm text-gray-500">/ trang</span>
          </div>
          
          <!-- Pagination Controls -->
          <div class="flex items-center gap-1">
            <!-- First Page -->
            <button
              @click="goToPage(1)"
              :disabled="pagination.page === 1"
              class="p-2 rounded-lg border border-gray-300 hover:bg-gray-50 disabled:opacity-50 disabled:cursor-not-allowed transition-colors"
              title="Trang đầu"
            >
              <svg xmlns="http://www.w3.org/2000/svg" class="h-4 w-4" fill="none" viewBox="0 0 24 24" stroke="currentColor">
                <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M11 19l-7-7 7-7m8 14l-7-7 7-7" />
              </svg>
            </button>
            
            <!-- Previous Page -->
            <button
              @click="goToPage(pagination.page - 1)"
              :disabled="pagination.page === 1"
              class="p-2 rounded-lg border border-gray-300 hover:bg-gray-50 disabled:opacity-50 disabled:cursor-not-allowed transition-colors"
              title="Trang trước"
            >
              <svg xmlns="http://www.w3.org/2000/svg" class="h-4 w-4" fill="none" viewBox="0 0 24 24" stroke="currentColor">
                <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M15 19l-7-7 7-7" />
              </svg>
            </button>
            
            <!-- Page Numbers -->
            <template v-for="pageNum in visiblePages" :key="pageNum">
              <button
                v-if="pageNum === '...'"
                disabled
                class="px-3 py-1 text-sm text-gray-400"
              >
                ...
              </button>
              <button
                v-else
                @click="goToPage(pageNum)"
                :class="[
                  'px-3 py-1 text-sm rounded-lg border transition-colors',
                  pagination.page === pageNum
                    ? 'bg-primary text-white border-primary'
                    : 'border-gray-300 hover:bg-gray-50'
                ]"
              >
                {{ pageNum }}
              </button>
            </template>
            
            <!-- Next Page -->
            <button
              @click="goToPage(pagination.page + 1)"
              :disabled="pagination.page === pagination.totalPages"
              class="p-2 rounded-lg border border-gray-300 hover:bg-gray-50 disabled:opacity-50 disabled:cursor-not-allowed transition-colors"
              title="Trang sau"
            >
              <svg xmlns="http://www.w3.org/2000/svg" class="h-4 w-4" fill="none" viewBox="0 0 24 24" stroke="currentColor">
                <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M9 5l7 7-7 7" />
              </svg>
            </button>
            
            <!-- Last Page -->
            <button
              @click="goToPage(pagination.totalPages)"
              :disabled="pagination.page === pagination.totalPages"
              class="p-2 rounded-lg border border-gray-300 hover:bg-gray-50 disabled:opacity-50 disabled:cursor-not-allowed transition-colors"
              title="Trang cuối"
            >
              <svg xmlns="http://www.w3.org/2000/svg" class="h-4 w-4" fill="none" viewBox="0 0 24 24" stroke="currentColor">
                <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M13 5l7 7-7 7M5 5l7 7-7 7" />
              </svg>
            </button>
          </div>
        </div>
      </div>
    </div>
  </div>
</template>

<script setup>
import { ref, reactive, computed, onMounted } from 'vue'
import { useRouter } from 'vue-router'
import { stockAPI } from '@/api'

const router = useRouter()

// State
const loading = ref(false)
const entries = ref([])

// Pagination state
const pagination = reactive({
  page: 1,
  pageSize: 20,
  total: 0,
  totalPages: 0
})

// Filters
const filters = reactive({
  search: '',
  stock_entry_type: '',
  from_date: '',
  to_date: ''
})

// Computed
const startIndex = computed(() => (pagination.page - 1) * pagination.pageSize)
const endIndex = computed(() => Math.min(startIndex.value + entries.value.length, pagination.total))

// Tính toán các số trang hiển thị
const visiblePages = computed(() => {
  const total = pagination.totalPages
  const current = pagination.page
  const pages = []
  
  if (total <= 7) {
    // Hiển thị tất cả nếu ít trang
    for (let i = 1; i <= total; i++) {
      pages.push(i)
    }
  } else {
    // Luôn hiển thị trang đầu
    pages.push(1)
    
    if (current > 3) {
      pages.push('...')
    }
    
    // Các trang xung quanh trang hiện tại
    const start = Math.max(2, current - 1)
    const end = Math.min(total - 1, current + 1)
    
    for (let i = start; i <= end; i++) {
      if (!pages.includes(i)) {
        pages.push(i)
      }
    }
    
    if (current < total - 2) {
      pages.push('...')
    }
    
    // Luôn hiển thị trang cuối
    if (!pages.includes(total)) {
      pages.push(total)
    }
  }
  
  return pages
})

// Debounce timer
let searchTimeout = null

// Methods
const formatDate = (date) => {
  if (!date) return ''
  return new Date(date).toLocaleDateString('vi-VN')
}

const formatNumber = (num) => {
  if (!num) return '0'
  return new Intl.NumberFormat('vi-VN').format(num)
}

const formatWarehouse = (warehouse) => {
  if (!warehouse) return 'N/A'
  return warehouse.split(' - ')[0]
}

const getStatusText = (docstatus) => {
  switch (docstatus) {
    case 0: return 'Nháp'
    case 1: return 'Đã duyệt'
    case 2: return 'Đã hủy'
    default: return 'Không xác định'
  }
}

const getEntryTypeLabel = (type) => {
  const labels = {
    'Material Receipt': 'Nhập kho',
    'Material Issue': 'Xuất kho',
    'Material Transfer': 'Chuyển kho',
    'Manufacture': 'Sản xuất',
    'Repack': 'Đóng gói'
  }
  return labels[type] || type
}

const getEntryTypeClass = (type) => {
  const classes = {
    'Material Receipt': 'bg-blue-100 text-blue-700',
    'Material Issue': 'bg-orange-100 text-orange-700',
    'Material Transfer': 'bg-purple-100 text-purple-700',
    'Manufacture': 'bg-teal-100 text-teal-700',
    'Repack': 'bg-gray-100 text-gray-700'
  }
  return classes[type] || 'bg-gray-100 text-gray-700'
}

const getWarehouseDisplay = (entry) => {
  // Với nhập kho: hiển thị kho đích, xuất kho: hiển thị kho nguồn
  const warehouse = entry.to_warehouse || entry.from_warehouse
  return formatWarehouse(warehouse)
}

const getTotalValue = (entry) => {
  return entry.total_incoming_value || entry.total_outgoing_value || entry.total_amount || 0
}

const debouncedSearch = () => {
  if (searchTimeout) {
    clearTimeout(searchTimeout)
  }
  searchTimeout = setTimeout(() => {
    pagination.page = 1 // Reset về trang 1 khi search
    loadEntries()
  }, 300)
}

const loadEntries = async () => {
  loading.value = true
  try {
    const params = {
      page: pagination.page,
      page_size: pagination.pageSize
    }
    
    if (filters.stock_entry_type) {
      params.stock_entry_type = filters.stock_entry_type
    }
    if (filters.search) {
      params.search = filters.search
    }
    if (filters.from_date) {
      params.from_date = filters.from_date
    }
    if (filters.to_date) {
      params.to_date = filters.to_date
    }
    
    const result = await stockAPI.getStockEntries(params)
    
    // Hỗ trợ cả response cũ (array) và mới (object với pagination)
    if (Array.isArray(result)) {
      entries.value = result
      pagination.total = result.length
      pagination.totalPages = 1
    } else {
      entries.value = result.data || []
      pagination.total = result.total || 0
      pagination.page = result.page || 1
      pagination.totalPages = result.total_pages || 1
    }
  } catch (error) {
    console.error('Error loading entries:', error)
    entries.value = []
    pagination.total = 0
    pagination.totalPages = 1
  } finally {
    loading.value = false
  }
}

const goToPage = (page) => {
  if (page >= 1 && page <= pagination.totalPages) {
    pagination.page = page
    loadEntries()
  }
}

const changePageSize = () => {
  pagination.page = 1 // Reset về trang 1 khi thay đổi page size
  loadEntries()
}

const onFilterChange = () => {
  pagination.page = 1 // Reset về trang 1 khi thay đổi filter
  loadEntries()
}

const viewDetail = (name) => {
  router.push(`/stock/entries/${name}`)
}

// Initialize
onMounted(() => {
  loadEntries()
})
</script>

<style scoped>
.bg-primary {
  background-color: #055568;
}

.bg-primary-dark {
  background-color: #044454;
}

.text-primary {
  color: #055568;
}

.border-primary {
  border-color: #055568;
}

.focus\:ring-primary:focus {
  --tw-ring-color: #055568;
}

.focus\:border-primary:focus {
  border-color: #055568;
}

.hover\:bg-primary:hover {
  background-color: #055568;
}

.hover\:bg-primary-dark:hover {
  background-color: #044454;
}

.hover\:text-primary-dark:hover {
  color: #044454;
}

.hover\:border-primary:hover {
  border-color: #055568;
}
</style>
