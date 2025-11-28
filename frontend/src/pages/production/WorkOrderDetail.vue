<template>
  <div class="h-full">
    <!-- Loading -->
    <div v-if="loading && !workOrder" class="flex items-center justify-center h-full">
      <div class="animate-spin rounded-full h-8 w-8 border-b-2 border-primary"></div>
    </div>

    <!-- Error -->
    <div v-else-if="error" class="flex flex-col items-center justify-center h-full">
      <svg class="w-16 h-16 text-gray-400 mb-4" fill="none" stroke="currentColor" viewBox="0 0 24 24">
        <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M9.172 16.172a4 4 0 015.656 0M9 10h.01M15 10h.01M21 12a9 9 0 11-18 0 9 9 0 0118 0z" />
      </svg>
      <p class="text-gray-600 mb-4">{{ error }}</p>
      <router-link to="/production/orders" class="text-primary hover:underline">
        ← Quay lại danh sách
      </router-link>
    </div>

    <!-- Content -->
    <div v-else-if="workOrder" class="p-6 overflow-auto">
      <div class="max-w-4xl mx-auto space-y-6">
        <!-- Header -->
        <div class="flex flex-col md:flex-row md:items-start md:justify-between gap-4">
          <div class="flex items-start gap-4">
            <router-link 
              to="/production/orders"
              class="p-2 text-gray-500 hover:text-gray-700 hover:bg-gray-100 rounded-lg transition-colors"
            >
              <svg class="w-5 h-5" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M15 19l-7-7 7-7" />
              </svg>
            </router-link>
            <div>
              <h1 class="text-2xl font-bold text-gray-900">{{ workOrder.name }}</h1>
              <p class="text-gray-600">{{ workOrder.production_item }} - {{ workOrder.item_name }}</p>
            </div>
          </div>
          
          <!-- Status Badge -->
          <span :class="[
            'px-3 py-1 rounded-full text-sm font-medium whitespace-nowrap',
            statusBadgeClass
          ]">
            {{ statusDisplay }}
          </span>
        </div>

        <!-- Action Buttons -->
        <div class="bg-white rounded-lg shadow p-4">
          <div class="flex flex-wrap gap-3">
            <!-- Approve (Draft -> Submitted) -->
            <button
              v-if="canApprove"
              @click="approveWorkOrder"
              :disabled="actionLoading"
              class="px-4 py-2 bg-success text-white rounded-lg hover:bg-success-dark transition-colors flex items-center gap-2 disabled:opacity-50"
            >
              <svg class="w-5 h-5" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M9 12l2 2 4-4m6 2a9 9 0 11-18 0 9 9 0 0118 0z" />
              </svg>
              Duyệt lệnh sản xuất
            </button>

            <!-- Start Production (Not Started -> In Process) -->
            <button
              v-if="canStart"
              @click="startProduction"
              :disabled="actionLoading"
              class="px-4 py-2 bg-primary text-white rounded-lg hover:bg-primary-dark transition-colors flex items-center gap-2 disabled:opacity-50"
            >
              <svg class="w-5 h-5" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M14.752 11.168l-3.197-2.132A1 1 0 0010 9.87v4.263a1 1 0 001.555.832l3.197-2.132a1 1 0 000-1.664z" />
                <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M21 12a9 9 0 11-18 0 9 9 0 0118 0z" />
              </svg>
              Cấp phát NVL &amp; Bắt đầu
            </button>

            <!-- Complete (In Process -> Completed) -->
            <button
              v-if="canComplete"
              @click="showCompleteModal = true"
              :disabled="actionLoading"
              class="px-4 py-2 bg-success text-white rounded-lg hover:bg-success-dark transition-colors flex items-center gap-2 disabled:opacity-50"
            >
              <svg class="w-5 h-5" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M5 13l4 4L19 7" />
              </svg>
              Hoàn thành sản xuất
            </button>

            <!-- Stop (In Process -> Stopped) -->
            <button
              v-if="canStop"
              @click="stopProduction"
              :disabled="actionLoading"
              class="px-4 py-2 bg-gray-500 text-white rounded-lg hover:bg-gray-600 transition-colors flex items-center gap-2 disabled:opacity-50"
            >
              <svg class="w-5 h-5" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M21 12a9 9 0 11-18 0 9 9 0 0118 0z" />
                <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M9 10a1 1 0 011-1h4a1 1 0 011 1v4a1 1 0 01-1 1h-4a1 1 0 01-1-1v-4z" />
              </svg>
              Dừng sản xuất
            </button>

            <!-- Cancel (Draft or Not Started) -->
            <button
              v-if="canCancel"
              @click="cancelWorkOrder"
              :disabled="actionLoading"
              class="px-4 py-2 bg-red-500 text-white rounded-lg hover:bg-red-600 transition-colors flex items-center gap-2 disabled:opacity-50"
            >
              <svg class="w-5 h-5" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M19 7l-.867 12.142A2 2 0 0116.138 21H7.862a2 2 0 01-1.995-1.858L5 7m5 4v6m4-6v6m1-10V4a1 1 0 00-1-1h-4a1 1 0 00-1 1v3M4 7h16" />
              </svg>
              Hủy lệnh
            </button>

            <!-- Info when no actions available -->
            <div v-if="!canApprove && !canStart && !canComplete && !canStop && !canCancel" class="text-gray-500 text-sm">
              <span v-if="workOrder.status === 'Completed'">✅ Lệnh sản xuất đã hoàn thành</span>
              <span v-else-if="workOrder.status === 'Stopped'">⏹️ Lệnh sản xuất đã dừng</span>
              <span v-else-if="workOrder.docstatus === 2">🚫 Lệnh sản xuất đã bị hủy</span>
            </div>
          </div>
        </div>

        <!-- Main Info -->
        <div class="grid grid-cols-1 md:grid-cols-2 gap-6">
          <!-- Quantity Info -->
          <div class="bg-white rounded-lg shadow p-6">
            <h2 class="text-lg font-semibold text-gray-900 mb-4">Tiến độ sản xuất</h2>
            
            <div class="space-y-4">
              <div class="grid grid-cols-3 gap-4 text-center">
                <div class="bg-gray-50 rounded-lg p-3">
                  <div class="text-2xl font-bold text-gray-900">{{ formatNumber(workOrder.qty) }}</div>
                  <div class="text-sm text-gray-500">Kế hoạch</div>
                </div>
                <div class="bg-primary/10 rounded-lg p-3">
                  <div class="text-2xl font-bold text-primary">{{ formatNumber(workOrder.produced_qty) }}</div>
                  <div class="text-sm text-gray-500">Đã SX</div>
                </div>
                <div class="bg-warning/10 rounded-lg p-3">
                  <div class="text-2xl font-bold text-warning">{{ formatNumber(workOrder.qty - workOrder.produced_qty) }}</div>
                  <div class="text-sm text-gray-500">Còn lại</div>
                </div>
              </div>

              <!-- Progress Bar -->
              <div>
                <div class="flex justify-between text-sm text-gray-600 mb-1">
                  <span>Tiến độ</span>
                  <span>{{ progressPercent }}%</span>
                </div>
                <div class="h-3 bg-gray-200 rounded-full overflow-hidden">
                  <div 
                    class="h-full bg-primary transition-all duration-300"
                    :style="{ width: progressPercent + '%' }"
                  ></div>
                </div>
              </div>
            </div>
          </div>

          <!-- Dates & Warehouses -->
          <div class="bg-white rounded-lg shadow p-6">
            <h2 class="text-lg font-semibold text-gray-900 mb-4">Thông tin chung</h2>
            
            <div class="space-y-3">
              <div class="flex justify-between">
                <span class="text-gray-500">BOM</span>
                <span class="font-medium">{{ workOrder.bom_no }}</span>
              </div>
              <div class="flex justify-between">
                <span class="text-gray-500">Đơn vị tính</span>
                <span class="font-medium">{{ translateUOM(workOrder.stock_uom) }}</span>
              </div>
              <div class="flex justify-between">
                <span class="text-gray-500">Ngày bắt đầu dự kiến</span>
                <span class="font-medium">{{ formatDate(workOrder.planned_start_date) || '-' }}</span>
              </div>
              <div class="flex justify-between">
                <span class="text-gray-500">Ngày hoàn thành dự kiến</span>
                <span class="font-medium">{{ formatDate(workOrder.expected_delivery_date) || '-' }}</span>
              </div>
              <div class="flex justify-between">
                <span class="text-gray-500">Kho nguyên liệu</span>
                <span class="font-medium">{{ extractWarehouseName(workOrder.source_warehouse) || '-' }}</span>
              </div>
              <div class="flex justify-between">
                <span class="text-gray-500">Kho WIP</span>
                <span class="font-medium">{{ extractWarehouseName(workOrder.wip_warehouse) || '-' }}</span>
              </div>
              <div class="flex justify-between">
                <span class="text-gray-500">Kho thành phẩm</span>
                <span class="font-medium">{{ extractWarehouseName(workOrder.fg_warehouse) || '-' }}</span>
              </div>
            </div>
          </div>
        </div>

        <!-- Required Items -->
        <div class="bg-white rounded-lg shadow overflow-hidden">
          <div class="px-6 py-4 border-b border-gray-200">
            <h2 class="text-lg font-semibold text-gray-900">Nguyên liệu cần thiết</h2>
          </div>
          
          <div class="overflow-x-auto">
            <table class="min-w-full divide-y divide-gray-200">
              <thead class="bg-gray-50">
                <tr>
                  <th class="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase">Mã NVL</th>
                  <th class="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase">Tên</th>
                  <th class="px-6 py-3 text-right text-xs font-medium text-gray-500 uppercase">Cần thiết</th>
                  <th class="px-6 py-3 text-right text-xs font-medium text-gray-500 uppercase">Đã cấp</th>
                  <th class="px-6 py-3 text-right text-xs font-medium text-gray-500 uppercase">Tồn kho</th>
                  <th class="px-6 py-3 text-center text-xs font-medium text-gray-500 uppercase">Trạng thái</th>
                </tr>
              </thead>
              <tbody class="bg-white divide-y divide-gray-200">
                <tr v-for="item in workOrder.required_items" :key="item.item_code">
                  <td class="px-6 py-4 whitespace-nowrap text-sm text-gray-900 font-mono">
                    {{ item.item_code }}
                  </td>
                  <td class="px-6 py-4 text-sm text-gray-900">
                    {{ item.item_name }}
                  </td>
                  <td class="px-6 py-4 whitespace-nowrap text-sm text-right font-medium text-gray-900">
                    {{ formatNumber(item.required_qty) }} {{ translateUOM(item.uom) }}
                  </td>
                  <td class="px-6 py-4 whitespace-nowrap text-sm text-right text-gray-600">
                    {{ formatNumber(item.transferred_qty || 0) }} {{ translateUOM(item.uom) }}
                  </td>
                  <td class="px-6 py-4 whitespace-nowrap text-sm text-right" :class="item.available_qty >= item.required_qty ? 'text-success' : 'text-error'">
                    {{ formatNumber(item.available_qty || 0) }} {{ translateUOM(item.uom) }}
                  </td>
                  <td class="px-6 py-4 whitespace-nowrap text-center">
                    <span v-if="(item.transferred_qty || 0) >= item.required_qty" class="px-2 py-1 bg-success/10 text-success text-xs rounded-full">
                      Đã cấp đủ
                    </span>
                    <span v-else-if="(item.transferred_qty || 0) > 0" class="px-2 py-1 bg-warning/10 text-warning text-xs rounded-full">
                      Cấp một phần
                    </span>
                    <span v-else class="px-2 py-1 bg-gray-100 text-gray-600 text-xs rounded-full">
                      Chưa cấp
                    </span>
                  </td>
                </tr>
                <tr v-if="!workOrder.required_items?.length">
                  <td colspan="6" class="px-6 py-8 text-center text-gray-500">
                    Không có dữ liệu nguyên liệu
                  </td>
                </tr>
              </tbody>
            </table>
          </div>
        </div>

        <!-- Stock Entries History -->
        <div v-if="workOrder.stock_entries?.length" class="bg-white rounded-lg shadow overflow-hidden">
          <div class="px-6 py-4 border-b border-gray-200">
            <h2 class="text-lg font-semibold text-gray-900">Lịch sử xuất nhập kho</h2>
          </div>
          
          <div class="overflow-x-auto">
            <table class="min-w-full divide-y divide-gray-200">
              <thead class="bg-gray-50">
                <tr>
                  <th class="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase">Mã phiếu</th>
                  <th class="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase">Loại</th>
                  <th class="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase">Ngày</th>
                  <th class="px-6 py-3 text-center text-xs font-medium text-gray-500 uppercase">Trạng thái</th>
                </tr>
              </thead>
              <tbody class="bg-white divide-y divide-gray-200">
                <tr v-for="entry in workOrder.stock_entries" :key="entry.name">
                  <td class="px-6 py-4 whitespace-nowrap text-sm text-primary font-mono">
                    {{ entry.name }}
                  </td>
                  <td class="px-6 py-4 whitespace-nowrap text-sm text-gray-900">
                    {{ translateStockEntryType(entry.stock_entry_type) }}
                  </td>
                  <td class="px-6 py-4 whitespace-nowrap text-sm text-gray-600">
                    {{ formatDate(entry.posting_date) }}
                  </td>
                  <td class="px-6 py-4 whitespace-nowrap text-center">
                    <span :class="[
                      'px-2 py-1 text-xs rounded-full',
                      entry.docstatus === 1 ? 'bg-success/10 text-success' : 
                      entry.docstatus === 2 ? 'bg-error/10 text-error' : 'bg-gray-100 text-gray-600'
                    ]">
                      {{ entry.docstatus === 1 ? 'Đã hoàn thành' : entry.docstatus === 2 ? 'Đã hủy' : 'Nháp' }}
                    </span>
                  </td>
                </tr>
              </tbody>
            </table>
          </div>
        </div>
      </div>
    </div>

    <!-- Complete Modal -->
    <div 
      v-if="showCompleteModal"
      class="fixed inset-0 bg-black bg-opacity-50 flex items-center justify-center z-50 p-4"
      @click.self="showCompleteModal = false"
    >
      <div class="bg-white rounded-lg shadow-xl w-full max-w-md">
        <div class="px-6 py-4 border-b border-gray-200">
          <h3 class="text-lg font-semibold text-gray-900">Hoàn thành sản xuất</h3>
        </div>
        <div class="p-6">
          <div class="mb-4">
            <label class="block text-sm font-medium text-gray-700 mb-1">
              Số lượng thành phẩm
            </label>
            <input
              type="number"
              v-model.number="completeQty"
              :max="workOrder.qty - workOrder.produced_qty"
              min="1"
              step="1"
              class="w-full px-3 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-primary focus:border-primary"
            />
            <p class="text-xs text-gray-500 mt-1">
              Tối đa: {{ formatNumber(workOrder.qty - workOrder.produced_qty) }} {{ translateUOM(workOrder.stock_uom) }}
            </p>
          </div>
        </div>
        <div class="px-6 py-4 border-t border-gray-200 flex justify-end gap-3">
          <button
            @click="showCompleteModal = false"
            class="px-4 py-2 text-gray-700 bg-gray-100 rounded-lg hover:bg-gray-200 transition-colors"
          >
            Hủy
          </button>
          <button
            @click="completeProduction"
            :disabled="actionLoading || !completeQty || completeQty <= 0"
            class="px-4 py-2 bg-success text-white rounded-lg hover:bg-success-dark transition-colors disabled:opacity-50"
          >
            {{ actionLoading ? 'Đang xử lý...' : 'Xác nhận hoàn thành' }}
          </button>
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

    <!-- Confirm Modal -->
    <ConfirmModal
      v-model="confirmModal.show"
      :title="confirmModal.title"
      :message="confirmModal.message"
      :type="confirmModal.type"
      :confirm-text="confirmModal.confirmText"
      :loading="actionLoading"
      @confirm="handleConfirmAction"
    />

    <!-- Error Modal -->
    <ConfirmModal
      v-model="errorModal.show"
      :title="errorModal.title"
      :message="errorModal.message"
      type="danger"
      confirm-text="Đã hiểu"
      cancel-text=""
      @confirm="errorModal.show = false"
    />
  </div>
</template>

<script setup>
import { ref, reactive, computed, onMounted, watch } from 'vue'
import { useRoute, useRouter } from 'vue-router'
import { workOrderAPI } from '@/api'
import ConfirmModal from '@/components/ConfirmModal.vue'

const route = useRoute()
const router = useRouter()

// UOM & Status Translation
const UOM_TRANSLATIONS = {
  'Nos': 'Cái', 'nos': 'Cái', 'Unit': 'Cái',
  'Kg': 'Kg', 'kg': 'Kg',
  'Meter': 'Mét', 'm': 'Mét',
  'Set': 'Bộ', 'Box': 'Hộp', 'Roll': 'Cuộn',
  'Liter': 'Lít', 'L': 'Lít'
}
const translateUOM = (uom) => UOM_TRANSLATIONS[uom] || uom || ''

const translateStockEntryType = (type) => {
  const map = {
    'Material Transfer for Manufacture': 'Cấp phát NVL',
    'Manufacture': 'Hoàn thành SX'
  }
  return map[type] || type
}

// State
const loading = ref(true)
const actionLoading = ref(false)
const error = ref(null)
const workOrder = ref(null)
const showCompleteModal = ref(false)
const completeQty = ref(0)

// Confirm Modal State
const confirmModal = reactive({
  show: false,
  title: '',
  message: '',
  type: 'info',
  confirmText: 'Xác nhận',
  action: null
})

// Error Modal State
const errorModal = reactive({
  show: false,
  title: 'Lỗi',
  message: ''
})

// Toast
const toast = reactive({ show: false, type: 'success', message: '' })

// Computed
const statusDisplay = computed(() => {
  if (!workOrder.value) return ''
  const wo = workOrder.value
  if (wo.docstatus === 0) return 'Chờ duyệt'
  const map = {
    'Not Started': 'Chưa bắt đầu',
    'In Process': 'Đang sản xuất',
    'Completed': 'Hoàn thành',
    'Stopped': 'Đã dừng'
  }
  return map[wo.status] || wo.status
})

const statusBadgeClass = computed(() => {
  if (!workOrder.value) return ''
  const wo = workOrder.value
  if (wo.docstatus === 0) return 'bg-warning/10 text-warning'
  const map = {
    'Not Started': 'bg-blue-100 text-blue-700',
    'In Process': 'bg-primary/10 text-primary',
    'Completed': 'bg-success/10 text-success',
    'Stopped': 'bg-gray-100 text-gray-600'
  }
  return map[wo.status] || 'bg-gray-100 text-gray-600'
})

const progressPercent = computed(() => {
  if (!workOrder.value || !workOrder.value.qty) return 0
  return Math.round((workOrder.value.produced_qty / workOrder.value.qty) * 100)
})

// Action permissions
const canApprove = computed(() => {
  return workOrder.value?.docstatus === 0
})

const canStart = computed(() => {
  return workOrder.value?.docstatus === 1 && workOrder.value?.status === 'Not Started'
})

const canComplete = computed(() => {
  return workOrder.value?.docstatus === 1 && 
         workOrder.value?.status === 'In Process' &&
         workOrder.value?.produced_qty < workOrder.value?.qty
})

const canStop = computed(() => {
  return workOrder.value?.docstatus === 1 && workOrder.value?.status === 'In Process'
})

// Can cancel: Draft (docstatus=0) hoặc Submitted nhưng chưa bắt đầu (Not Started và chưa có produced_qty)
const canCancel = computed(() => {
  if (!workOrder.value) return false
  const wo = workOrder.value
  // Draft - luôn có thể hủy
  if (wo.docstatus === 0) return true
  // Submitted nhưng chưa bắt đầu sản xuất
  if (wo.docstatus === 1 && wo.status === 'Not Started' && wo.produced_qty === 0) return true
  return false
})

// Methods
const formatNumber = (num) => {
  if (num === null || num === undefined) return '0'
  return new Intl.NumberFormat('vi-VN').format(num)
}

const formatDate = (dateStr) => {
  if (!dateStr) return null
  return new Date(dateStr).toLocaleDateString('vi-VN')
}

const extractWarehouseName = (fullName) => {
  if (!fullName) return null
  const parts = fullName.split(' - ')
  return parts[0]
}

const showToast = (type, message) => {
  toast.type = type
  toast.message = message
  toast.show = true
  setTimeout(() => { toast.show = false }, 3000)
}

// Show confirm modal helper
const showConfirm = (title, message, type, confirmText, action) => {
  confirmModal.title = title
  confirmModal.message = message
  confirmModal.type = type
  confirmModal.confirmText = confirmText
  confirmModal.action = action
  confirmModal.show = true
}

// Show error modal helper
const showError = (title, message) => {
  errorModal.title = title
  errorModal.message = message
  errorModal.show = true
}

// Handle confirm action
const handleConfirmAction = async () => {
  if (confirmModal.action) {
    await confirmModal.action()
  }
  confirmModal.show = false
}

const loadWorkOrder = async () => {
  loading.value = true
  error.value = null
  
  try {
    const data = await workOrderAPI.getDetail(route.params.name)
    if (data.success === false) {
      error.value = data.message || 'Không tìm thấy lệnh sản xuất'
    } else {
      workOrder.value = data
      completeQty.value = data.qty - data.produced_qty
    }
  } catch (err) {
    console.error('Error loading work order:', err)
    error.value = 'Không thể tải thông tin lệnh sản xuất'
  } finally {
    loading.value = false
  }
}

const approveWorkOrder = async () => {
  showConfirm(
    'Duyệt lệnh sản xuất',
    'Bạn có chắc chắn muốn duyệt lệnh sản xuất này?\n\nSau khi duyệt, có thể tiến hành cấp phát nguyên vật liệu.',
    'success',
    'Duyệt',
    doApproveWorkOrder
  )
}

const doApproveWorkOrder = async () => {
  actionLoading.value = true
  try {
    const result = await workOrderAPI.submit(workOrder.value.name)
    if (result.success) {
      showToast('success', result.message || 'Đã duyệt lệnh sản xuất')
      await loadWorkOrder()
    } else {
      showError('Không thể duyệt', result.message || 'Đã xảy ra lỗi')
    }
  } catch (err) {
    console.error('Error approving:', err)
    showError('Lỗi hệ thống', err.response?.data?.message || 'Không thể duyệt lệnh sản xuất')
  } finally {
    actionLoading.value = false
  }
}

const startProduction = async () => {
  // Kiểm tra xem có NVL nào thiếu không
  const insufficientItems = workOrder.value.required_items?.filter(item => {
    const available = item.available_qty || 0
    const required = item.required_qty - (item.transferred_qty || 0)
    return available < required
  }) || []

  if (insufficientItems.length > 0) {
    const itemsList = insufficientItems.map(item => 
      `• ${item.item_name}: Cần ${item.required_qty - (item.transferred_qty || 0)}, Tồn kho ${item.available_qty || 0}`
    ).join('\n')
    
    showConfirm(
      'Cảnh báo: Thiếu nguyên vật liệu',
      `Một số nguyên vật liệu không đủ số lượng:\n\n${itemsList}\n\nBạn vẫn muốn tiếp tục?`,
      'warning',
      'Vẫn tiếp tục',
      doStartProduction
    )
  } else {
    showConfirm(
      'Cấp phát nguyên vật liệu',
      'Hệ thống sẽ tự động xuất nguyên vật liệu từ kho nguồn sang kho sản xuất (WIP).\n\nBạn có muốn tiếp tục?',
      'info',
      'Cấp phát & Bắt đầu',
      doStartProduction
    )
  }
}

const doStartProduction = async () => {
  actionLoading.value = true
  try {
    const result = await workOrderAPI.start(workOrder.value.name)
    if (result.success) {
      showToast('success', result.message || 'Đã bắt đầu sản xuất')
      await loadWorkOrder()
    } else {
      // Hiển thị lỗi chi tiết trong modal
      showError('Không thể cấp phát nguyên vật liệu', result.message || 'Đã xảy ra lỗi')
    }
  } catch (err) {
    console.error('Error starting:', err)
    showError('Lỗi hệ thống', err.response?.data?.message || 'Không thể bắt đầu sản xuất')
  } finally {
    actionLoading.value = false
  }
}

const completeProduction = async () => {
  actionLoading.value = true
  try {
    const result = await workOrderAPI.complete(workOrder.value.name, completeQty.value)
    if (result.success) {
      showToast('success', result.message || 'Đã hoàn thành sản xuất')
      showCompleteModal.value = false
      await loadWorkOrder()
    } else {
      showCompleteModal.value = false
      showError('Không thể hoàn thành', result.message || 'Đã xảy ra lỗi')
    }
  } catch (err) {
    console.error('Error completing:', err)
    showCompleteModal.value = false
    showError('Lỗi hệ thống', err.response?.data?.message || 'Không thể hoàn thành sản xuất')
  } finally {
    actionLoading.value = false
  }
}

const stopProduction = async () => {
  showConfirm(
    'Dừng sản xuất',
    'Bạn có chắc chắn muốn dừng lệnh sản xuất này?\n\nLệnh sản xuất sẽ chuyển sang trạng thái "Đã dừng" và không thể tiếp tục.',
    'danger',
    'Dừng sản xuất',
    doStopProduction
  )
}

const doStopProduction = async () => {
  actionLoading.value = true
  try {
    const result = await workOrderAPI.stop(workOrder.value.name)
    if (result.success) {
      showToast('success', result.message || 'Đã dừng sản xuất')
      await loadWorkOrder()
    } else {
      showError('Không thể dừng', result.message || 'Đã xảy ra lỗi')
    }
  } catch (err) {
    console.error('Error stopping:', err)
    showError('Lỗi hệ thống', err.response?.data?.message || 'Không thể dừng sản xuất')
  } finally {
    actionLoading.value = false
  }
}

const cancelWorkOrder = async () => {
  const isDraft = workOrder.value?.docstatus === 0
  showConfirm(
    'Hủy lệnh sản xuất',
    isDraft 
      ? 'Bạn có chắc chắn muốn hủy lệnh sản xuất này?\n\nLệnh sản xuất sẽ bị xóa vĩnh viễn.'
      : 'Bạn có chắc chắn muốn hủy lệnh sản xuất này?\n\nHành động này không thể hoàn tác.',
    'danger',
    'Hủy lệnh',
    doCancelWorkOrder
  )
}

const doCancelWorkOrder = async () => {
  actionLoading.value = true
  try {
    const result = await workOrderAPI.cancel(workOrder.value.name)
    if (result.success) {
      showToast('success', result.message || 'Đã hủy lệnh sản xuất')
      // Nếu là Draft thì redirect về danh sách vì đã bị xóa
      if (workOrder.value?.docstatus === 0) {
        setTimeout(() => {
          router.push('/production/orders')
        }, 1000)
      } else {
        await loadWorkOrder()
      }
    } else {
      showError('Không thể hủy', result.message || 'Đã xảy ra lỗi')
    }
  } catch (err) {
    console.error('Error cancelling:', err)
    showError('Lỗi hệ thống', err.response?.data?.message || 'Không thể hủy lệnh sản xuất')
  } finally {
    actionLoading.value = false
  }
}

// Watch route changes
watch(() => route.params.name, (newName) => {
  if (newName) loadWorkOrder()
})

// Initialize
onMounted(() => {
  loadWorkOrder()
})
</script>

<style scoped>
.bg-primary { background-color: #055568; }
.bg-primary-dark { background-color: #044454; }
.text-primary { color: #055568; }
.bg-primary\/10 { background-color: rgba(5, 85, 104, 0.1); }
.bg-success { background-color: #4CAF50; }
.bg-success-dark { background-color: #388E3C; }
.text-success { color: #4CAF50; }
.bg-success\/10 { background-color: rgba(76, 175, 80, 0.1); }
.bg-warning\/10 { background-color: rgba(255, 152, 0, 0.1); }
.text-warning { color: #FF9800; }
.text-error { color: #f44336; }
.bg-error\/10 { background-color: rgba(244, 67, 54, 0.1); }
</style>
