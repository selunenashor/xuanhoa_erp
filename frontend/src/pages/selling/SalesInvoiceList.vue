<template>
  <div class="space-y-6">
    <!-- Header -->
    <div class="flex flex-col sm:flex-row sm:items-center sm:justify-between gap-4">
      <div>
        <h1 class="text-2xl font-bold text-gray-900">Hóa đơn bán hàng</h1>
        <p class="text-gray-600">Quản lí hóa đơn bán hàng</p>
      </div>
      <router-link
        to="/selling/invoices/create"
        class="inline-flex items-center justify-center gap-2 px-4 py-2 bg-primary text-white rounded-lg hover:bg-primary-light transition-colors"
      >
        <svg xmlns="http://www.w3.org/2000/svg" class="h-5 w-5" fill="none" viewBox="0 0 24 24" stroke="currentColor">
          <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M12 4v16m8-8H4" />
        </svg>
        Tạo hóa đơn mới
      </router-link>
    </div>

    <!-- Filters -->
    <div class="bg-white rounded-lg shadow p-4">
      <div class="grid grid-cols-1 md:grid-cols-4 gap-4">
        <!-- Search -->
        <div class="relative">
          <input
            v-model="filters.search"
            type="text"
            placeholder="Tìm theo mã, khách hàng..."
            class="w-full pl-10 pr-4 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-primary focus:border-primary"
            @input="debouncedLoad"
          />
          <svg xmlns="http://www.w3.org/2000/svg" class="h-5 w-5 text-gray-400 absolute left-3 top-2.5" fill="none" viewBox="0 0 24 24" stroke="currentColor">
            <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M21 21l-6-6m2-5a7 7 0 11-14 0 7 7 0 0114 0z" />
          </svg>
        </div>

        <!-- Status Filter -->
        <select
          v-model="filters.status"
          class="w-full px-4 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-primary focus:border-primary"
          @change="loadInvoices"
        >
          <option value="">Tất cả trạng thái</option>
          <option value="Draft">Nháp</option>
          <option value="Unpaid">Chưa thanh toán</option>
          <option value="Paid">Đã thanh toán</option>
          <option value="Overdue">Quá hạn</option>
          <option value="Cancelled">Đã hủy</option>
        </select>

        <!-- From Date -->
        <input
          v-model="filters.from_date"
          type="date"
          class="w-full px-4 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-primary focus:border-primary"
          @change="loadInvoices"
        />

        <!-- To Date -->
        <input
          v-model="filters.to_date"
          type="date"
          class="w-full px-4 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-primary focus:border-primary"
          @change="loadInvoices"
        />
      </div>
    </div>

    <!-- Loading -->
    <div v-if="loading" class="flex justify-center py-12">
      <svg class="animate-spin h-8 w-8 text-primary" xmlns="http://www.w3.org/2000/svg" fill="none" viewBox="0 0 24 24">
        <circle class="opacity-25" cx="12" cy="12" r="10" stroke="currentColor" stroke-width="4"></circle>
        <path class="opacity-75" fill="currentColor" d="M4 12a8 8 0 018-8V0C5.373 0 0 5.373 0 12h4zm2 5.291A7.962 7.962 0 014 12H0c0 3.042 1.135 5.824 3 7.938l3-2.647z"></path>
      </svg>
    </div>

    <!-- Table -->
    <div v-else-if="invoices.length > 0" class="bg-white rounded-lg shadow overflow-hidden">
      <div class="overflow-x-auto">
        <table class="min-w-full divide-y divide-gray-200">
          <thead class="bg-gray-50">
            <tr>
              <th class="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">Mã hóa đơn</th>
              <th class="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">Khách hàng</th>
              <th class="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">Ngày</th>
              <th class="px-6 py-3 text-right text-xs font-medium text-gray-500 uppercase tracking-wider">Tổng tiền</th>
              <th class="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">Trạng thái</th>
              <th class="px-6 py-3 text-right text-xs font-medium text-gray-500 uppercase tracking-wider">Thao tác</th>
            </tr>
          </thead>
          <tbody class="bg-white divide-y divide-gray-200">
            <tr v-for="invoice in invoices" :key="invoice.name" class="hover:bg-gray-50">
              <td class="px-6 py-4 whitespace-nowrap">
                <router-link :to="`/selling/invoices/${invoice.name}`" class="text-primary hover:underline font-medium">
                  {{ invoice.name }}
                </router-link>
              </td>
              <td class="px-6 py-4 whitespace-nowrap">
                <div class="text-sm text-gray-900">{{ invoice.customer_name }}</div>
                <div class="text-xs text-gray-500">{{ invoice.customer }}</div>
              </td>
              <td class="px-6 py-4 whitespace-nowrap text-sm text-gray-500">
                {{ formatDate(invoice.posting_date) }}
              </td>
              <td class="px-6 py-4 whitespace-nowrap text-sm text-gray-900 text-right font-medium">
                {{ formatCurrency(invoice.grand_total) }}
              </td>
              <td class="px-6 py-4 whitespace-nowrap">
                <span
                  :class="[
                    'px-2 py-1 text-xs font-medium rounded-full',
                    getStatusClass(invoice.status_color)
                  ]"
                >
                  {{ invoice.status_display }}
                </span>
              </td>
              <td class="px-6 py-4 whitespace-nowrap text-right text-sm">
                <router-link
                  :to="`/selling/invoices/${invoice.name}`"
                  class="text-primary hover:underline"
                >
                  Chi tiết
                </router-link>
              </td>
            </tr>
          </tbody>
        </table>
      </div>

      <!-- Pagination -->
      <div class="px-6 py-4 border-t border-gray-200 flex items-center justify-between">
        <p class="text-sm text-gray-500">
          Hiển thị {{ (pagination.page - 1) * pagination.pageSize + 1 }} - 
          {{ Math.min(pagination.page * pagination.pageSize, pagination.total) }} 
          / {{ pagination.total }} hóa đơn
        </p>
        <div class="flex items-center gap-2">
          <button
            @click="changePage(pagination.page - 1)"
            :disabled="pagination.page <= 1"
            class="px-3 py-1 border border-gray-300 rounded-lg hover:bg-gray-50 disabled:opacity-50 disabled:cursor-not-allowed"
          >
            Trước
          </button>
          <span class="text-sm text-gray-600">
            Trang {{ pagination.page }} / {{ Math.ceil(pagination.total / pagination.pageSize) || 1 }}
          </span>
          <button
            @click="changePage(pagination.page + 1)"
            :disabled="pagination.page * pagination.pageSize >= pagination.total"
            class="px-3 py-1 border border-gray-300 rounded-lg hover:bg-gray-50 disabled:opacity-50 disabled:cursor-not-allowed"
          >
            Sau
          </button>
        </div>
      </div>
    </div>

    <!-- Empty State -->
    <div v-else class="bg-white rounded-lg shadow p-12 text-center">
      <svg xmlns="http://www.w3.org/2000/svg" class="h-16 w-16 mx-auto text-gray-300 mb-4" fill="none" viewBox="0 0 24 24" stroke="currentColor">
        <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M9 12h6m-6 4h6m2 5H7a2 2 0 01-2-2V5a2 2 0 012-2h5.586a1 1 0 01.707.293l5.414 5.414a1 1 0 01.293.707V19a2 2 0 01-2 2z" />
      </svg>
      <h3 class="text-lg font-medium text-gray-900 mb-1">Chưa có hóa đơn nào</h3>
      <p class="text-gray-500 mb-4">Bắt đầu bằng cách tạo hóa đơn bán hàng mới</p>
      <router-link
        to="/selling/invoices/create"
        class="inline-flex items-center gap-2 px-4 py-2 bg-primary text-white rounded-lg hover:bg-primary-light transition-colors"
      >
        <svg xmlns="http://www.w3.org/2000/svg" class="h-5 w-5" fill="none" viewBox="0 0 24 24" stroke="currentColor">
          <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M12 4v16m8-8H4" />
        </svg>
        Tạo hóa đơn mới
      </router-link>
    </div>
  </div>
</template>

<script setup>
import { ref, reactive, onMounted } from 'vue'
import { salesInvoiceAPI } from '@/api'

// State
const loading = ref(true)
const invoices = ref([])
const filters = reactive({
  search: '',
  status: '',
  from_date: '',
  to_date: ''
})
const pagination = reactive({
  page: 1,
  pageSize: 20,
  total: 0
})

// Debounce
let searchTimeout = null
const debouncedLoad = () => {
  clearTimeout(searchTimeout)
  searchTimeout = setTimeout(() => {
    pagination.page = 1
    loadInvoices()
  }, 300)
}

// Methods
const formatDate = (date) => {
  if (!date) return ''
  return new Date(date).toLocaleDateString('vi-VN')
}

const formatCurrency = (amount) => {
  if (!amount) return '0 ₫'
  return new Intl.NumberFormat('vi-VN', { style: 'currency', currency: 'VND' }).format(amount)
}

const getStatusClass = (color) => {
  const classes = {
    'warning': 'bg-yellow-100 text-yellow-700',
    'success': 'bg-green-100 text-green-700',
    'error': 'bg-red-100 text-red-700',
    'info': 'bg-blue-100 text-blue-700',
    'gray': 'bg-gray-100 text-gray-700'
  }
  return classes[color] || 'bg-gray-100 text-gray-700'
}

const loadInvoices = async () => {
  loading.value = true
  
  try {
    const result = await salesInvoiceAPI.getList({
      search: filters.search,
      status: filters.status,
      from_date: filters.from_date,
      to_date: filters.to_date,
      page: pagination.page,
      page_size: pagination.pageSize
    })
    
    if (result.success) {
      invoices.value = result.data || []
      pagination.total = result.total || 0
    } else {
      console.error('Failed to load invoices:', result.message)
      invoices.value = []
    }
  } catch (e) {
    console.error('Error loading invoices:', e)
    invoices.value = []
  } finally {
    loading.value = false
  }
}

const changePage = (newPage) => {
  pagination.page = newPage
  loadInvoices()
}

// Initialize
onMounted(() => {
  loadInvoices()
})
</script>
