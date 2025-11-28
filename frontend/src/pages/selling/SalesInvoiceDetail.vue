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
    <div v-else-if="errorMsg" class="text-center py-12">
      <svg xmlns="http://www.w3.org/2000/svg" class="h-12 w-12 mx-auto text-error mb-4" fill="none" viewBox="0 0 24 24" stroke="currentColor">
        <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M12 8v4m0 4h.01M21 12a9 9 0 11-18 0 9 9 0 0118 0z" />
      </svg>
      <h3 class="text-lg font-medium text-gray-900 mb-1">{{ errorMsg }}</h3>
      <button @click="router.back()" class="mt-4 text-primary hover:underline">← Quay lại</button>
    </div>

    <!-- Content -->
    <template v-else-if="invoice">
      <!-- Header -->
      <div class="flex flex-col sm:flex-row sm:items-center sm:justify-between gap-4">
        <div class="flex items-center gap-4">
          <button
            @click="router.back()"
            class="p-2 hover:bg-gray-100 rounded-lg transition-colors"
          >
            <svg xmlns="http://www.w3.org/2000/svg" class="h-5 w-5 text-gray-600" fill="none" viewBox="0 0 24 24" stroke="currentColor">
              <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M15 19l-7-7 7-7" />
            </svg>
          </button>
          <div>
            <h1 class="text-2xl font-bold text-gray-900">{{ invoice.name }}</h1>
            <p class="text-gray-600">Hóa đơn bán hàng cho {{ invoice.customer_name }}</p>
          </div>
        </div>
        
        <!-- Status Badge -->
        <span
          :class="[
            'px-3 py-1 text-sm font-medium rounded-full',
            getStatusClass(invoice.status_color)
          ]"
        >
          {{ invoice.status_display }}
        </span>
      </div>

      <!-- Info Cards -->
      <div class="grid grid-cols-1 md:grid-cols-3 gap-4">
        <!-- Customer Info -->
        <div class="bg-white rounded-lg shadow p-4">
          <h3 class="text-sm font-medium text-gray-500 mb-2">Khách hàng</h3>
          <p class="text-lg font-semibold text-gray-900">{{ invoice.customer_name }}</p>
          <p class="text-sm text-gray-500">{{ invoice.customer }}</p>
        </div>

        <!-- Total -->
        <div class="bg-white rounded-lg shadow p-4">
          <h3 class="text-sm font-medium text-gray-500 mb-2">Tổng tiền</h3>
          <p class="text-lg font-semibold text-gray-900">{{ formatCurrency(invoice.grand_total) }}</p>
          <p v-if="invoice.outstanding_amount > 0" class="text-sm text-error">
            Còn nợ: {{ formatCurrency(invoice.outstanding_amount) }}
          </p>
          <p v-else class="text-sm text-success">Đã thanh toán đủ</p>
        </div>

        <!-- Dates -->
        <div class="bg-white rounded-lg shadow p-4">
          <h3 class="text-sm font-medium text-gray-500 mb-2">Ngày</h3>
          <p class="text-sm text-gray-900">Ngày HĐ: {{ formatDate(invoice.posting_date) }}</p>
          <p v-if="invoice.due_date" class="text-sm text-gray-900">
            Hạn TT: {{ formatDate(invoice.due_date) }}
          </p>
        </div>
      </div>

      <!-- Actions -->
      <div class="bg-white rounded-lg shadow p-4">
        <div class="flex flex-wrap items-center gap-3">
          <!-- Submit Button - Khi còn draft -->
          <button
            v-if="invoice.docstatus === 0"
            @click="submitInvoice"
            :disabled="actionLoading"
            class="inline-flex items-center gap-2 px-4 py-2 bg-primary text-white rounded-lg hover:bg-primary-light disabled:opacity-50 transition-colors"
          >
            <svg xmlns="http://www.w3.org/2000/svg" class="h-5 w-5" fill="none" viewBox="0 0 24 24" stroke="currentColor">
              <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M5 13l4 4L19 7" />
            </svg>
            Duyệt hóa đơn
          </button>

          <!-- Payment Button - Chỉ hiển thị khi đã duyệt VÀ còn nợ -->
          <button
            v-if="invoice.docstatus === 1 && invoice.outstanding_amount > 0"
            @click="openPaymentModal"
            :disabled="actionLoading"
            class="inline-flex items-center gap-2 px-4 py-2 bg-green-600 text-white rounded-lg hover:bg-green-700 disabled:opacity-50 transition-colors"
          >
            <svg xmlns="http://www.w3.org/2000/svg" class="h-5 w-5" fill="none" viewBox="0 0 24 24" stroke="currentColor">
              <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M17 9V7a2 2 0 00-2-2H5a2 2 0 00-2 2v6a2 2 0 002 2h2m2 4h10a2 2 0 002-2v-6a2 2 0 00-2-2H9a2 2 0 00-2 2v6a2 2 0 002 2zm7-5a2 2 0 11-4 0 2 2 0 014 0z" />
            </svg>
            Thu tiền
          </button>

          <!-- Create Stock Entry Button - Chỉ hiển thị khi đã thanh toán đủ VÀ chưa có phiếu xuất kho -->
          <button
            v-if="invoice.docstatus === 1 && invoice.outstanding_amount <= 0 && !hasStockEntry && !invoice.update_stock"
            @click="createStockEntry"
            :disabled="actionLoading"
            class="inline-flex items-center gap-2 px-4 py-2 bg-warning text-white rounded-lg hover:bg-yellow-600 disabled:opacity-50 transition-colors"
          >
            <svg xmlns="http://www.w3.org/2000/svg" class="h-5 w-5" fill="none" viewBox="0 0 24 24" stroke="currentColor">
              <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M20 7l-8-4-8 4m16 0l-8 4m8-4v10l-8 4m0-10L4 7m8 4v10M4 7v10l8 4" />
            </svg>
            Tạo phiếu xuất kho
          </button>

          <!-- Completed Badge - Hiển thị khi đã thanh toán đủ VÀ đã có phiếu xuất kho -->
          <div
            v-if="isCompleted"
            class="inline-flex items-center gap-2 px-4 py-2 bg-green-100 text-green-700 rounded-lg"
          >
            <svg xmlns="http://www.w3.org/2000/svg" class="h-5 w-5" fill="none" viewBox="0 0 24 24" stroke="currentColor">
              <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M9 12l2 2 4-4m6 2a9 9 0 11-18 0 9 9 0 0118 0z" />
            </svg>
            Hóa đơn hoàn tất
          </div>

          <!-- Stock Entry Link - Hiển thị khi đã có phiếu xuất kho -->
          <router-link
            v-if="hasStockEntry"
            :to="`/stock/entries/${invoice.stock_entries[0]?.name}`"
            class="inline-flex items-center gap-2 px-4 py-2 bg-gray-100 text-gray-700 rounded-lg hover:bg-gray-200 transition-colors"
          >
            <svg xmlns="http://www.w3.org/2000/svg" class="h-5 w-5" fill="none" viewBox="0 0 24 24" stroke="currentColor">
              <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M20 7l-8-4-8 4m16 0l-8 4m8-4v10l-8 4m0-10L4 7m8 4v10M4 7v10l8 4" />
            </svg>
            Xem phiếu xuất kho
          </router-link>

          <!-- Cancel Button - Chỉ hiển thị khi draft HOẶC (đã duyệt + chưa thanh toán + chưa xuất kho) -->
          <button
            v-if="canCancel"
            @click="showCancelConfirm = true"
            :disabled="actionLoading"
            class="inline-flex items-center gap-2 px-4 py-2 border border-error text-error rounded-lg hover:bg-red-50 disabled:opacity-50 transition-colors"
          >
            <svg xmlns="http://www.w3.org/2000/svg" class="h-5 w-5" fill="none" viewBox="0 0 24 24" stroke="currentColor">
              <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M6 18L18 6M6 6l12 12" />
            </svg>
            {{ invoice.docstatus === 0 ? 'Xóa' : 'Hủy' }}
          </button>
        </div>
      </div>

      <!-- Items Table -->
      <div class="bg-white rounded-lg shadow">
        <div class="px-6 py-4 border-b border-gray-200">
          <h2 class="text-lg font-semibold text-gray-900">Danh sách sản phẩm</h2>
        </div>
        <div class="overflow-x-auto">
          <table class="min-w-full divide-y divide-gray-200">
            <thead class="bg-gray-50">
              <tr>
                <th class="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase">#</th>
                <th class="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase">Sản phẩm</th>
                <th class="px-6 py-3 text-right text-xs font-medium text-gray-500 uppercase">Số lượng</th>
                <th class="px-6 py-3 text-right text-xs font-medium text-gray-500 uppercase">Đơn giá</th>
                <th class="px-6 py-3 text-right text-xs font-medium text-gray-500 uppercase">Thành tiền</th>
                <th class="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase">Kho</th>
              </tr>
            </thead>
            <tbody class="bg-white divide-y divide-gray-200">
              <tr v-for="(item, index) in invoice.items" :key="index">
                <td class="px-6 py-4 text-sm text-gray-500">{{ index + 1 }}</td>
                <td class="px-6 py-4">
                  <div class="text-sm font-medium text-gray-900">{{ item.item_name }}</div>
                  <div class="text-xs text-gray-500">{{ item.item_code }}</div>
                </td>
                <td class="px-6 py-4 text-sm text-gray-900 text-right">
                  {{ item.qty }} {{ item.uom }}
                </td>
                <td class="px-6 py-4 text-sm text-gray-900 text-right">
                  {{ formatCurrency(item.rate) }}
                </td>
                <td class="px-6 py-4 text-sm font-medium text-gray-900 text-right">
                  {{ formatCurrency(item.amount) }}
                </td>
                <td class="px-6 py-4 text-sm text-gray-500">
                  {{ formatWarehouse(item.warehouse) }}
                </td>
              </tr>
            </tbody>
            <tfoot class="bg-gray-50">
              <tr>
                <td colspan="4" class="px-6 py-4 text-right font-medium text-gray-700">Tổng cộng:</td>
                <td class="px-6 py-4 text-right font-bold text-gray-900">{{ formatCurrency(invoice.grand_total) }}</td>
                <td></td>
              </tr>
            </tfoot>
          </table>
        </div>
      </div>

      <!-- Stock Entries -->
      <div v-if="invoice.stock_entries?.length > 0" class="bg-white rounded-lg shadow">
        <div class="px-6 py-4 border-b border-gray-200">
          <h2 class="text-lg font-semibold text-gray-900">Phiếu xuất kho liên quan</h2>
        </div>
        <div class="divide-y divide-gray-200">
          <router-link
            v-for="entry in invoice.stock_entries"
            :key="entry.name"
            :to="`/stock/entries/${entry.name}`"
            class="flex items-center justify-between px-6 py-4 hover:bg-gray-50 transition-colors"
          >
            <div>
              <span class="text-sm font-medium text-primary">{{ entry.name }}</span>
              <span class="text-sm text-gray-500 ml-2">{{ entry.purpose }}</span>
            </div>
            <div class="flex items-center gap-2">
              <span class="text-sm text-gray-500">{{ formatDate(entry.posting_date) }}</span>
              <span
                :class="[
                  'px-2 py-1 text-xs rounded-full',
                  entry.docstatus === 1 ? 'bg-green-100 text-green-700' : 'bg-yellow-100 text-yellow-700'
                ]"
              >
                {{ entry.docstatus === 1 ? 'Đã duyệt' : 'Nháp' }}
              </span>
            </div>
          </router-link>
        </div>
      </div>

      <!-- Remarks -->
      <div v-if="invoice.remarks" class="bg-white rounded-lg shadow p-6">
        <h2 class="text-lg font-semibold text-gray-900 mb-2">Ghi chú</h2>
        <p class="text-gray-600 whitespace-pre-wrap">{{ invoice.remarks }}</p>
      </div>

      <!-- Meta Info -->
      <div class="bg-white rounded-lg shadow p-6">
        <h2 class="text-lg font-semibold text-gray-900 mb-4">Thông tin khác</h2>
        <div class="grid grid-cols-2 md:grid-cols-4 gap-4 text-sm">
          <div>
            <span class="text-gray-500">Người tạo:</span>
            <p class="font-medium text-gray-900">{{ invoice.owner_name }}</p>
          </div>
          <div>
            <span class="text-gray-500">Ngày tạo:</span>
            <p class="font-medium text-gray-900">{{ formatDateTime(invoice.creation) }}</p>
          </div>
          <div>
            <span class="text-gray-500">Cập nhật:</span>
            <p class="font-medium text-gray-900">{{ formatDateTime(invoice.modified) }}</p>
          </div>
          <div>
            <span class="text-gray-500">Kho mặc định:</span>
            <p class="font-medium text-gray-900">{{ formatWarehouse(invoice.set_warehouse) || 'N/A' }}</p>
          </div>
        </div>
      </div>
    </template>

    <!-- Cancel Confirm Modal -->
    <div v-if="showCancelConfirm" class="fixed inset-0 z-50 flex items-center justify-center p-4 bg-black/50">
      <div class="bg-white rounded-xl shadow-xl max-w-md w-full p-6">
        <h3 class="text-lg font-semibold text-gray-900 mb-2">
          {{ invoice?.docstatus === 0 ? 'Xác nhận xóa' : 'Xác nhận hủy' }}
        </h3>
        <p class="text-gray-600 mb-6">
          {{ invoice?.docstatus === 0 
            ? 'Bạn có chắc muốn xóa hóa đơn này? Thao tác này không thể hoàn tác.'
            : 'Bạn có chắc muốn hủy hóa đơn này? Thao tác này không thể hoàn tác.' 
          }}
        </p>
        <div class="flex justify-end gap-3">
          <button
            @click="showCancelConfirm = false"
            class="px-4 py-2 border border-gray-300 text-gray-700 rounded-lg hover:bg-gray-50"
          >
            Không
          </button>
          <button
            @click="cancelInvoice"
            :disabled="actionLoading"
            class="px-4 py-2 bg-error text-white rounded-lg hover:bg-red-600 disabled:opacity-50"
          >
            {{ invoice?.docstatus === 0 ? 'Xóa' : 'Hủy hóa đơn' }}
          </button>
        </div>
      </div>
    </div>

    <!-- Payment Modal -->
    <div v-if="showPaymentModal" class="fixed inset-0 z-50 flex items-center justify-center p-4 bg-black/50">
      <div class="bg-white rounded-xl shadow-xl max-w-lg w-full p-6">
        <h3 class="text-lg font-semibold text-gray-900 mb-4">Thu tiền khách hàng</h3>
        
        <div class="space-y-4">
          <!-- Outstanding Amount Info -->
          <div class="bg-green-50 border border-green-200 rounded-lg p-4">
            <div class="flex justify-between items-center">
              <span class="text-green-700">Số tiền còn nợ:</span>
              <span class="text-lg font-bold text-green-700">{{ formatCurrency(invoice?.outstanding_amount) }}</span>
            </div>
          </div>

          <!-- Payment Amount -->
          <div>
            <label class="block text-sm font-medium text-gray-700 mb-1">Số tiền thu</label>
            <input
              v-model.number="paymentForm.amount"
              type="number"
              min="0"
              :max="invoice?.outstanding_amount"
              step="1000"
              class="w-full px-4 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-primary focus:border-primary"
              :placeholder="`Tối đa ${formatCurrency(invoice?.outstanding_amount)}`"
            />
          </div>

          <!-- Mode of Payment -->
          <div>
            <label class="block text-sm font-medium text-gray-700 mb-1">Hình thức thanh toán</label>
            <select
              v-model="paymentForm.mode"
              class="w-full px-4 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-primary focus:border-primary"
            >
              <option value="Cash">Tiền mặt</option>
              <option value="Bank Draft">Chuyển khoản ngân hàng</option>
              <option value="Wire Transfer">Chuyển khoản điện tử (Wire Transfer)</option>
            </select>
            <p v-if="paymentForm.mode === 'Wire Transfer'" class="mt-1 text-xs text-gray-500">
              Wire Transfer là hình thức chuyển khoản điện tử giữa các ngân hàng, thường dùng cho giao dịch quốc tế hoặc số tiền lớn.
            </p>
          </div>

          <!-- Reference No -->
          <div>
            <label class="block text-sm font-medium text-gray-700 mb-1">
              Số tham chiếu 
              <span v-if="paymentForm.mode !== 'Cash'" class="text-error">*</span>
              <span v-else class="text-gray-400">(tùy chọn)</span>
            </label>
            <input
              v-model="paymentForm.referenceNo"
              type="text"
              :required="paymentForm.mode !== 'Cash'"
              class="w-full px-4 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-primary focus:border-primary"
              placeholder="Số phiếu thu, số chứng từ ngân hàng..."
            />
          </div>

          <!-- Reference Date (required for Bank transactions) -->
          <div v-if="paymentForm.mode !== 'Cash'">
            <label class="block text-sm font-medium text-gray-700 mb-1">
              Ngày chứng từ <span class="text-error">*</span>
            </label>
            <input
              v-model="paymentForm.referenceDate"
              type="date"
              required
              class="w-full px-4 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-primary focus:border-primary"
            />
          </div>
        </div>

        <!-- Payment Error -->
        <div v-if="paymentError" class="mt-4 bg-red-50 border border-red-200 rounded-lg p-3">
          <div class="flex items-start gap-2">
            <svg xmlns="http://www.w3.org/2000/svg" class="h-5 w-5 text-red-500 flex-shrink-0" fill="none" viewBox="0 0 24 24" stroke="currentColor">
              <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M12 8v4m0 4h.01M21 12a9 9 0 11-18 0 9 9 0 0118 0z" />
            </svg>
            <p class="text-sm text-red-600">{{ paymentError }}</p>
          </div>
        </div>

        <div class="flex justify-end gap-3 mt-6">
          <button
            @click="closePaymentModal"
            class="px-4 py-2 border border-gray-300 text-gray-700 rounded-lg hover:bg-gray-50"
          >
            Hủy
          </button>
          <button
            @click="processPayment"
            :disabled="actionLoading || !paymentForm.amount || paymentForm.amount <= 0"
            class="px-4 py-2 bg-green-600 text-white rounded-lg hover:bg-green-700 disabled:opacity-50"
          >
            <span v-if="actionLoading" class="flex items-center gap-2">
              <svg class="animate-spin h-4 w-4" xmlns="http://www.w3.org/2000/svg" fill="none" viewBox="0 0 24 24">
                <circle class="opacity-25" cx="12" cy="12" r="10" stroke="currentColor" stroke-width="4"></circle>
                <path class="opacity-75" fill="currentColor" d="M4 12a8 8 0 018-8V0C5.373 0 0 5.373 0 12h4zm2 5.291A7.962 7.962 0 014 12H0c0 3.042 1.135 5.824 3 7.938l3-2.647z"></path>
              </svg>
              Đang xử lý...
            </span>
            <span v-else>Xác nhận thu tiền</span>
          </button>
        </div>
      </div>
    </div>

    <!-- Toast -->
    <div v-if="toast.show" :class="[
      'fixed bottom-4 right-4 max-w-md rounded-lg p-4 shadow-lg transition-all',
      toast.type === 'success' ? 'bg-green-50 border border-green-200' : 'bg-red-50 border border-red-200'
    ]">
      <div class="flex items-start gap-3">
        <svg v-if="toast.type === 'success'" xmlns="http://www.w3.org/2000/svg" class="h-5 w-5 text-success flex-shrink-0" fill="none" viewBox="0 0 24 24" stroke="currentColor">
          <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M5 13l4 4L19 7" />
        </svg>
        <svg v-else xmlns="http://www.w3.org/2000/svg" class="h-5 w-5 text-error flex-shrink-0" fill="none" viewBox="0 0 24 24" stroke="currentColor">
          <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M12 8v4m0 4h.01M21 12a9 9 0 11-18 0 9 9 0 0118 0z" />
        </svg>
        <p :class="toast.type === 'success' ? 'text-success' : 'text-error'" class="text-sm">{{ toast.message }}</p>
      </div>
    </div>
  </div>
</template>

<script setup>
import { ref, computed, onMounted } from 'vue'
import { useRoute, useRouter } from 'vue-router'
import { salesInvoiceAPI } from '@/api'

const route = useRoute()
const router = useRouter()

// State
const loading = ref(true)
const errorMsg = ref('')
const invoice = ref(null)
const actionLoading = ref(false)
const showCancelConfirm = ref(false)
const toast = ref({ show: false, type: 'success', message: '' })

// Payment state
const showPaymentModal = ref(false)
const paymentError = ref('')
const paymentForm = ref({
  amount: 0,
  mode: 'Cash',
  referenceNo: '',
  referenceDate: new Date().toISOString().split('T')[0]
})

// Computed
const hasStockEntry = computed(() => {
  return invoice.value?.stock_entries?.length > 0
})

// Hóa đơn hoàn tất khi: đã duyệt + đã thanh toán đủ + đã có phiếu xuất kho
const isCompleted = computed(() => {
  return invoice.value?.docstatus === 1 && 
         invoice.value?.outstanding_amount <= 0 && 
         hasStockEntry.value
})

// Có thể hủy khi: draft HOẶC (đã duyệt + chưa thanh toán gì + chưa có phiếu xuất kho)
const canCancel = computed(() => {
  if (!invoice.value) return false
  if (invoice.value.docstatus === 2) return false // Đã hủy rồi
  if (invoice.value.docstatus === 0) return true // Draft có thể xóa
  // Đã duyệt: chỉ hủy được nếu chưa thanh toán gì và chưa xuất kho
  return invoice.value.outstanding_amount === invoice.value.grand_total && !hasStockEntry.value
})

// Methods
const formatDate = (date) => {
  if (!date) return ''
  return new Date(date).toLocaleDateString('vi-VN')
}

const formatDateTime = (date) => {
  if (!date) return ''
  return new Date(date).toLocaleString('vi-VN')
}

const formatCurrency = (amount) => {
  if (!amount) return '0 ₫'
  return new Intl.NumberFormat('vi-VN', { style: 'currency', currency: 'VND' }).format(amount)
}

const formatWarehouse = (warehouse) => {
  if (!warehouse) return ''
  return warehouse.split(' - ')[0]
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

const showToast = (type, message) => {
  toast.value = { show: true, type, message }
  setTimeout(() => {
    toast.value.show = false
  }, 3000)
}

const loadInvoice = async () => {
  loading.value = true
  errorMsg.value = ''
  
  try {
    const result = await salesInvoiceAPI.getDetail(route.params.name)
    
    if (result.success) {
      invoice.value = result
    } else {
      errorMsg.value = result.message || 'Không tìm thấy hóa đơn'
    }
  } catch (e) {
    console.error('Error loading invoice:', e)
    errorMsg.value = 'Có lỗi xảy ra khi tải dữ liệu'
  } finally {
    loading.value = false
  }
}

const submitInvoice = async () => {
  actionLoading.value = true
  
  try {
    const result = await salesInvoiceAPI.submit(invoice.value.name)
    
    if (result.success) {
      showToast('success', result.message)
      await loadInvoice()
    } else {
      showToast('error', result.message)
    }
  } catch (e) {
    console.error('Error submitting invoice:', e)
    showToast('error', 'Có lỗi xảy ra khi duyệt hóa đơn')
  } finally {
    actionLoading.value = false
  }
}

const createStockEntry = async () => {
  actionLoading.value = true
  
  try {
    const result = await salesInvoiceAPI.createStockEntry(invoice.value.name)
    
    if (result.success) {
      showToast('success', 'Đã tạo phiếu xuất kho thành công. Hóa đơn hoàn tất!')
      // Reload invoice to update stock_entries
      await loadInvoice()
    } else {
      showToast('error', result.message)
    }
  } catch (e) {
    console.error('Error creating stock entry:', e)
    showToast('error', 'Có lỗi xảy ra khi tạo phiếu xuất kho')
  } finally {
    actionLoading.value = false
  }
}

const cancelInvoice = async () => {
  actionLoading.value = true
  
  try {
    const result = await salesInvoiceAPI.cancel(invoice.value.name)
    
    if (result.success) {
      showToast('success', result.message)
      showCancelConfirm.value = false
      
      if (invoice.value.docstatus === 0) {
        // Was draft, now deleted - go back
        router.push('/selling/invoices')
      } else {
        // Was submitted, now cancelled - reload
        await loadInvoice()
      }
    } else {
      showToast('error', result.message)
    }
  } catch (e) {
    console.error('Error cancelling invoice:', e)
    showToast('error', 'Có lỗi xảy ra')
  } finally {
    actionLoading.value = false
    showCancelConfirm.value = false
  }
}

const openPaymentModal = () => {
  // Set default amount to outstanding amount
  paymentForm.value.amount = invoice.value?.outstanding_amount || 0
  paymentForm.value.mode = 'Cash'
  paymentForm.value.referenceNo = ''
  paymentForm.value.referenceDate = new Date().toISOString().split('T')[0]
  paymentError.value = ''
  showPaymentModal.value = true
}

const closePaymentModal = () => {
  showPaymentModal.value = false
  paymentError.value = ''
}

const processPayment = async () => {
  paymentError.value = ''
  
  if (!paymentForm.value.amount || paymentForm.value.amount <= 0) {
    paymentError.value = 'Vui lòng nhập số tiền thu'
    return
  }
  
  if (paymentForm.value.amount > invoice.value.outstanding_amount) {
    paymentError.value = 'Số tiền thu không được lớn hơn số tiền còn nợ'
    return
  }
  
  // Validate reference fields for bank transactions
  if (paymentForm.value.mode !== 'Cash') {
    if (!paymentForm.value.referenceNo) {
      paymentError.value = 'Vui lòng nhập số tham chiếu cho giao dịch ngân hàng'
      return
    }
    if (!paymentForm.value.referenceDate) {
      paymentError.value = 'Vui lòng nhập ngày chứng từ cho giao dịch ngân hàng'
      return
    }
  }
  
  actionLoading.value = true
  
  try {
    const result = await salesInvoiceAPI.createPayment(
      invoice.value.name,
      paymentForm.value.amount,
      paymentForm.value.mode,
      paymentForm.value.referenceNo || null,
      paymentForm.value.mode !== 'Cash' ? paymentForm.value.referenceDate : null
    )
    
    if (result.success) {
      showToast('success', result.message)
      closePaymentModal()
      await loadInvoice()
    } else {
      paymentError.value = result.message || 'Có lỗi xảy ra'
    }
  } catch (e) {
    console.error('Error processing payment:', e)
    paymentError.value = 'Có lỗi xảy ra khi xử lý thanh toán. Vui lòng thử lại.'
  } finally {
    actionLoading.value = false
  }
}

// Initialize
onMounted(() => {
  loadInvoice()
})
</script>
