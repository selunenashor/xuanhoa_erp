<template>
  <div class="space-y-6">
    <!-- Loading -->
    <div v-if="loading" class="flex justify-center py-12">
      <svg class="animate-spin h-8 w-8 text-primary" xmlns="http://www.w3.org/2000/svg" fill="none" viewBox="0 0 24 24">
        <circle class="opacity-25" cx="12" cy="12" r="10" stroke="currentColor" stroke-width="4"></circle>
        <path class="opacity-75" fill="currentColor" d="M4 12a8 8 0 018-8V0C5.373 0 0 5.373 0 12h4zm2 5.291A7.962 7.962 0 014 12H0c0 3.042 1.135 5.824 3 7.938l3-2.647z"></path>
      </svg>
    </div>

    <!-- Error -->
    <div v-else-if="error" class="bg-red-50 border border-red-200 rounded-lg p-6 text-center">
      <svg xmlns="http://www.w3.org/2000/svg" class="h-12 w-12 mx-auto text-red-400 mb-4" fill="none" viewBox="0 0 24 24" stroke="currentColor">
        <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M12 9v2m0 4h.01m-6.938 4h13.856c1.54 0 2.502-1.667 1.732-3L13.732 4c-.77-1.333-2.694-1.333-3.464 0L3.34 16c-.77 1.333.192 3 1.732 3z" />
      </svg>
      <h3 class="text-lg font-medium text-red-800 mb-2">Không tìm thấy phiếu</h3>
      <p class="text-red-600 mb-4">{{ error }}</p>
      <router-link
        to="/stock/entries"
        class="inline-flex items-center gap-2 px-4 py-2 bg-red-100 text-red-700 rounded-lg hover:bg-red-200 transition-colors"
      >
        <svg xmlns="http://www.w3.org/2000/svg" class="h-5 w-5" fill="none" viewBox="0 0 24 24" stroke="currentColor">
          <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M10 19l-7-7m0 0l7-7m-7 7h18" />
        </svg>
        Quay lại danh sách
      </router-link>
    </div>

    <!-- Content -->
    <template v-else-if="entry">
      <!-- Header -->
      <div class="flex flex-col sm:flex-row sm:items-center sm:justify-between gap-4">
        <div class="flex items-center gap-4">
          <router-link
            to="/stock/entries"
            class="p-2 text-gray-500 hover:text-gray-700 hover:bg-gray-100 rounded-lg transition-colors"
          >
            <svg xmlns="http://www.w3.org/2000/svg" class="h-5 w-5" fill="none" viewBox="0 0 24 24" stroke="currentColor">
              <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M10 19l-7-7m0 0l7-7m-7 7h18" />
            </svg>
          </router-link>
          <div>
            <h1 class="text-2xl font-bold text-gray-900">{{ entry.name }}</h1>
            <p class="text-gray-600">{{ getEntryTypeLabel(entry.stock_entry_type) }}</p>
          </div>
        </div>
        <div class="flex items-center gap-3">
          <span
            :class="[
              'px-3 py-1 text-sm rounded-full font-medium',
              entry.docstatus === 1 
                ? 'bg-green-100 text-green-700' 
                : entry.docstatus === 2 
                  ? 'bg-red-100 text-red-700'
                  : 'bg-yellow-100 text-yellow-700'
            ]"
          >
            {{ getStatusText(entry.docstatus) }}
          </span>
          <button
            @click="printEntry"
            class="inline-flex items-center gap-2 px-4 py-2 border border-gray-300 text-gray-700 rounded-lg hover:bg-gray-50 transition-colors"
          >
            <svg xmlns="http://www.w3.org/2000/svg" class="h-5 w-5" fill="none" viewBox="0 0 24 24" stroke="currentColor">
              <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M17 17h2a2 2 0 002-2v-4a2 2 0 00-2-2H5a2 2 0 00-2 2v4a2 2 0 002 2h2m2 4h6a2 2 0 002-2v-4a2 2 0 00-2-2H9a2 2 0 00-2 2v4a2 2 0 002 2zm8-12V5a2 2 0 00-2-2H9a2 2 0 00-2 2v4h10z" />
            </svg>
            In phiếu
          </button>
        </div>
      </div>

      <!-- Info Cards -->
      <div class="grid grid-cols-1 md:grid-cols-3 gap-4">
        <!-- Basic Info -->
        <div class="bg-white rounded-lg shadow p-6">
          <h3 class="text-sm font-medium text-gray-500 uppercase tracking-wider mb-4">Thông tin chung</h3>
          <dl class="space-y-3">
            <div class="flex justify-between">
              <dt class="text-sm text-gray-500">Ngày:</dt>
              <dd class="text-sm font-medium text-gray-900">{{ formatDate(entry.posting_date) }}</dd>
            </div>
            <div class="flex justify-between">
              <dt class="text-sm text-gray-500">Giờ:</dt>
              <dd class="text-sm font-medium text-gray-900">{{ formatTime(entry.posting_time) }}</dd>
            </div>
            <div class="flex justify-between">
              <dt class="text-sm text-gray-500">Kho:</dt>
              <dd class="text-sm font-medium text-gray-900">{{ getWarehouseDisplay(entry) }}</dd>
            </div>
            <div class="flex justify-between">
              <dt class="text-sm text-gray-500">Công ty:</dt>
              <dd class="text-sm font-medium text-gray-900">{{ entry.company }}</dd>
            </div>
          </dl>
        </div>

        <!-- Value Info -->
        <div class="bg-white rounded-lg shadow p-6">
          <h3 class="text-sm font-medium text-gray-500 uppercase tracking-wider mb-4">Giá trị</h3>
          <dl class="space-y-3">
            <div class="flex justify-between">
              <dt class="text-sm text-gray-500">Số sản phẩm:</dt>
              <dd class="text-sm font-medium text-gray-900">{{ entry.items?.length || 0 }}</dd>
            </div>
            <div class="flex justify-between">
              <dt class="text-sm text-gray-500">Tổng số lượng:</dt>
              <dd class="text-sm font-medium text-gray-900">{{ formatNumber(totalQty) }}</dd>
            </div>
            <div class="flex justify-between">
              <dt class="text-sm text-gray-500">Tổng giá trị:</dt>
              <dd class="text-sm font-medium text-primary text-lg">{{ formatNumber(getTotalValue(entry)) }} VND</dd>
            </div>
          </dl>
        </div>

        <!-- User Info -->
        <div class="bg-white rounded-lg shadow p-6">
          <h3 class="text-sm font-medium text-gray-500 uppercase tracking-wider mb-4">Người thực hiện</h3>
          <dl class="space-y-3">
            <div class="flex justify-between">
              <dt class="text-sm text-gray-500">Người tạo:</dt>
              <dd class="text-sm font-medium text-gray-900">{{ entry.owner_name }}</dd>
            </div>
            <div class="flex justify-between">
              <dt class="text-sm text-gray-500">Ngày tạo:</dt>
              <dd class="text-sm font-medium text-gray-900">{{ formatDateTime(entry.creation) }}</dd>
            </div>
            <div class="flex justify-between">
              <dt class="text-sm text-gray-500">Cập nhật bởi:</dt>
              <dd class="text-sm font-medium text-gray-900">{{ entry.modified_by_name }}</dd>
            </div>
            <div class="flex justify-between">
              <dt class="text-sm text-gray-500">Ngày cập nhật:</dt>
              <dd class="text-sm font-medium text-gray-900">{{ formatDateTime(entry.modified) }}</dd>
            </div>
          </dl>
        </div>
      </div>

      <!-- Remarks -->
      <div v-if="entry.remarks" class="bg-white rounded-lg shadow p-6">
        <h3 class="text-sm font-medium text-gray-500 uppercase tracking-wider mb-2">Ghi chú</h3>
        <p class="text-gray-700">{{ entry.remarks }}</p>
      </div>

      <!-- Items Table -->
      <div class="bg-white rounded-lg shadow">
        <div class="px-6 py-4 border-b border-gray-200">
          <h3 class="text-lg font-semibold text-gray-900">Chi tiết sản phẩm</h3>
        </div>
        <div class="overflow-x-auto">
          <table class="min-w-full divide-y divide-gray-200">
            <thead class="bg-gray-50">
              <tr>
                <th class="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
                  STT
                </th>
                <th class="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
                  Mã sản phẩm
                </th>
                <th class="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
                  Tên sản phẩm
                </th>
                <th class="px-6 py-3 text-right text-xs font-medium text-gray-500 uppercase tracking-wider">
                  Số lượng
                </th>
                <th class="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
                  ĐVT
                </th>
                <th class="px-6 py-3 text-right text-xs font-medium text-gray-500 uppercase tracking-wider">
                  Đơn giá
                </th>
                <th class="px-6 py-3 text-right text-xs font-medium text-gray-500 uppercase tracking-wider">
                  Thành tiền
                </th>
                <th class="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
                  Kho
                </th>
              </tr>
            </thead>
            <tbody class="bg-white divide-y divide-gray-200">
              <tr v-for="(item, index) in entry.items" :key="index" class="hover:bg-gray-50">
                <td class="px-6 py-4 whitespace-nowrap text-sm text-gray-500">
                  {{ index + 1 }}
                </td>
                <td class="px-6 py-4 whitespace-nowrap">
                  <span class="text-sm font-medium text-primary">{{ item.item_code }}</span>
                </td>
                <td class="px-6 py-4 whitespace-nowrap text-sm text-gray-900">
                  {{ item.item_name }}
                </td>
                <td class="px-6 py-4 whitespace-nowrap text-sm text-gray-900 text-right font-medium">
                  {{ formatNumber(item.qty) }}
                </td>
                <td class="px-6 py-4 whitespace-nowrap text-sm text-gray-500">
                  {{ translateUOM(item.uom) }}
                </td>
                <td class="px-6 py-4 whitespace-nowrap text-sm text-gray-900 text-right">
                  {{ formatNumber(item.basic_rate || item.valuation_rate || 0) }}
                </td>
                <td class="px-6 py-4 whitespace-nowrap text-sm text-gray-900 text-right font-medium">
                  {{ formatNumber(item.amount || 0) }}
                </td>
                <td class="px-6 py-4 whitespace-nowrap text-sm text-gray-500">
                  {{ formatWarehouse(item.t_warehouse || item.s_warehouse) }}
                </td>
              </tr>
            </tbody>
            <tfoot class="bg-gray-50">
              <tr>
                <td colspan="3" class="px-6 py-4 text-sm font-medium text-gray-900">
                  Tổng cộng
                </td>
                <td class="px-6 py-4 text-sm font-bold text-gray-900 text-right">
                  {{ formatNumber(totalQty) }}
                </td>
                <td colspan="2"></td>
                <td class="px-6 py-4 text-sm font-bold text-primary text-right">
                  {{ formatNumber(getTotalValue(entry)) }}
                </td>
                <td></td>
              </tr>
            </tfoot>
          </table>
        </div>
      </div>
    </template>
  </div>
</template>

<script setup>
import { ref, computed, onMounted } from 'vue'
import { useRoute } from 'vue-router'
import { stockAPI } from '@/api'

const route = useRoute()

// State
const loading = ref(true)
const error = ref(null)
const entry = ref(null)

// UOM Translation
const UOM_TRANSLATIONS = {
  'Nos': 'Cái',
  'nos': 'Cái',
  'Unit': 'Cái',
  'unit': 'Cái',
  'Kg': 'Kg',
  'kg': 'Kg',
  'Kilogram': 'Kg',
  'Meter': 'Mét',
  'meter': 'Mét',
  'm': 'Mét',
  'Piece': 'Cái',
  'piece': 'Cái',
  'Pcs': 'Cái',
  'pcs': 'Cái',
  'Set': 'Bộ',
  'set': 'Bộ',
  'Box': 'Hộp',
  'box': 'Hộp',
  'Roll': 'Cuộn',
  'roll': 'Cuộn',
  'Liter': 'Lít',
  'liter': 'Lít',
}

// Computed
const totalQty = computed(() => {
  if (!entry.value?.items) return 0
  return entry.value.items.reduce((sum, item) => sum + (item.qty || 0), 0)
})

// Methods
const translateUOM = (uom) => {
  if (!uom) return ''
  return UOM_TRANSLATIONS[uom] || uom
}

const getEntryTypeLabel = (type) => {
  const labels = {
    'Material Receipt': 'Phiếu nhập kho',
    'Material Issue': 'Phiếu xuất kho',
    'Material Transfer': 'Phiếu chuyển kho',
    'Manufacture': 'Phiếu sản xuất',
    'Repack': 'Phiếu đóng gói'
  }
  return labels[type] || type
}

const getWarehouseDisplay = (entry) => {
  const warehouse = entry.to_warehouse || entry.from_warehouse
  return formatWarehouse(warehouse)
}

const getTotalValue = (entry) => {
  return entry.total_incoming_value || entry.total_outgoing_value || entry.total_amount || 0
}

const formatDate = (date) => {
  if (!date) return ''
  return new Date(date).toLocaleDateString('vi-VN')
}

const formatTime = (time) => {
  if (!time) return ''
  return time.substring(0, 5)
}

const formatDateTime = (datetime) => {
  if (!datetime) return ''
  const dt = new Date(datetime)
  return dt.toLocaleDateString('vi-VN') + ' ' + dt.toLocaleTimeString('vi-VN', { hour: '2-digit', minute: '2-digit' })
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

const printEntry = () => {
  // Open ERPNext print view
  const printUrl = `/printview?doctype=Stock%20Entry&name=${entry.value.name}&format=Standard`
  window.open(printUrl, '_blank')
}

const loadEntry = async () => {
  loading.value = true
  error.value = null
  
  try {
    const name = route.params.name
    const result = await stockAPI.getStockEntryDetail(name)
    
    if (result.success === false) {
      error.value = result.message
    } else {
      entry.value = result
    }
  } catch (err) {
    console.error('Error loading entry:', err)
    error.value = 'Không thể tải thông tin phiếu'
  } finally {
    loading.value = false
  }
}

// Initialize
onMounted(() => {
  loadEntry()
})
</script>

<style scoped>
.bg-primary {
  background-color: #055568;
}

.text-primary {
  color: #055568;
}
</style>
