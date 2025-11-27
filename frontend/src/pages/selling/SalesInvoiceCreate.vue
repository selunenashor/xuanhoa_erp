<template>
  <div class="space-y-6">
    <!-- Header -->
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
        <h1 class="text-2xl font-bold text-gray-900">Tạo hóa đơn bán hàng</h1>
        <p class="text-gray-600">Nhập thông tin hóa đơn bán hàng mới</p>
      </div>
    </div>

    <!-- Form -->
    <form @submit.prevent="handleSubmit" class="space-y-6">
      <!-- Basic Info -->
      <div class="bg-white rounded-lg shadow p-6">
        <h2 class="text-lg font-semibold text-gray-900 mb-4">Thông tin cơ bản</h2>
        
        <div class="grid grid-cols-1 md:grid-cols-2 gap-6">
          <!-- Customer -->
          <div>
            <label class="block text-sm font-medium text-gray-700 mb-1">
              Khách hàng <span class="text-error">*</span>
            </label>
            <div class="relative">
              <!-- Search Input (when no customer selected) -->
              <input
                v-if="!form.customer"
                type="text"
                v-model="customerSearch"
                @input="searchCustomers"
                @focus="showCustomerDropdown = true"
                @blur="hideCustomerDropdown"
                placeholder="Tìm khách hàng..."
                :class="[
                  'w-full px-4 py-2 border rounded-lg focus:ring-2 focus:ring-primary focus:border-primary',
                  !form.customer ? 'border-gray-300' : 'border-gray-300'
                ]"
              />
              
              <!-- Selected Customer Display -->
              <div
                v-else
                class="w-full px-4 py-2 border border-green-300 bg-green-50 rounded-lg flex justify-between items-center"
              >
                <div class="flex-1 min-w-0">
                  <span class="font-medium text-gray-900">{{ form.customer_name }}</span>
                  <span class="text-gray-500 text-sm ml-2">({{ form.customer }})</span>
                </div>
                <button
                  type="button"
                  @click="clearCustomer"
                  class="text-gray-400 hover:text-gray-600 ml-2"
                >
                  <svg xmlns="http://www.w3.org/2000/svg" class="h-4 w-4" fill="none" viewBox="0 0 24 24" stroke="currentColor">
                    <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M6 18L18 6M6 6l12 12" />
                  </svg>
                </button>
              </div>
              
              <!-- Dropdown -->
              <div
                v-if="showCustomerDropdown && customers.length > 0"
                class="absolute z-10 w-full mt-1 bg-white border border-gray-200 rounded-lg shadow-lg max-h-60 overflow-auto"
              >
                <button
                  v-for="customer in customers"
                  :key="customer.name"
                  type="button"
                  @mousedown.prevent="selectCustomer(customer)"
                  class="w-full px-4 py-2 text-left hover:bg-gray-50 border-b border-gray-100 last:border-b-0"
                >
                  <div class="font-medium text-gray-900">{{ customer.customer_name }}</div>
                  <div class="text-xs text-gray-500">{{ customer.name }}</div>
                </button>
              </div>
              
              <!-- Loading indicator -->
              <div
                v-if="isSearchingCustomer"
                class="absolute z-10 w-full mt-1 bg-white border border-gray-200 rounded-lg shadow-lg p-3 text-center text-gray-500"
              >
                <svg class="animate-spin h-5 w-5 mx-auto text-primary" xmlns="http://www.w3.org/2000/svg" fill="none" viewBox="0 0 24 24">
                  <circle class="opacity-25" cx="12" cy="12" r="10" stroke="currentColor" stroke-width="4"></circle>
                  <path class="opacity-75" fill="currentColor" d="M4 12a8 8 0 018-8V0C5.373 0 0 5.373 0 12h4zm2 5.291A7.962 7.962 0 014 12H0c0 3.042 1.135 5.824 3 7.938l3-2.647z"></path>
                </svg>
                Đang tìm kiếm...
              </div>
              
              <!-- No results -->
              <div
                v-if="showCustomerDropdown && !isSearchingCustomer && customerSearch.length >= 1 && customers.length === 0 && hasSearchedCustomer"
                class="absolute z-10 w-full mt-1 bg-white border border-gray-200 rounded-lg shadow-lg p-3 text-center text-gray-500"
              >
                Không tìm thấy khách hàng
              </div>
            </div>
          </div>

          <!-- Warehouse -->
          <div>
            <label class="block text-sm font-medium text-gray-700 mb-1">
              Kho xuất mặc định
            </label>
            <select
              v-model="form.set_warehouse"
              class="w-full px-4 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-primary focus:border-primary"
            >
              <option value="">-- Chọn kho --</option>
              <option v-for="wh in warehouses" :key="wh.name" :value="wh.name">
                {{ wh.warehouse_name }}
              </option>
            </select>
          </div>

          <!-- Posting Date -->
          <div>
            <label class="block text-sm font-medium text-gray-700 mb-1">
              Ngày hóa đơn <span class="text-error">*</span>
            </label>
            <input
              type="date"
              v-model="form.posting_date"
              required
              class="w-full px-4 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-primary focus:border-primary"
            />
          </div>

          <!-- Due Date -->
          <div>
            <label class="block text-sm font-medium text-gray-700 mb-1">
              Hạn thanh toán
            </label>
            <input
              type="date"
              v-model="form.due_date"
              class="w-full px-4 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-primary focus:border-primary"
            />
          </div>

          <!-- Remarks -->
          <div class="md:col-span-2">
            <label class="block text-sm font-medium text-gray-700 mb-1">
              Ghi chú
            </label>
            <textarea
              v-model="form.remarks"
              rows="2"
              placeholder="Ghi chú cho hóa đơn..."
              class="w-full px-4 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-primary focus:border-primary"
            ></textarea>
          </div>
        </div>
      </div>

      <!-- Items -->
      <div class="bg-white rounded-lg shadow p-6">
        <div class="flex items-center justify-between mb-4">
          <h2 class="text-lg font-semibold text-gray-900">Danh sách sản phẩm</h2>
          <button
            type="button"
            @click="addItem"
            class="inline-flex items-center gap-2 px-3 py-1.5 text-sm bg-primary text-white rounded-lg hover:bg-primary-light transition-colors"
          >
            <svg xmlns="http://www.w3.org/2000/svg" class="h-4 w-4" fill="none" viewBox="0 0 24 24" stroke="currentColor">
              <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M12 4v16m8-8H4" />
            </svg>
            Thêm sản phẩm
          </button>
        </div>

        <!-- Items List -->
        <div class="space-y-4">
          <div
            v-for="(item, index) in form.items"
            :key="index"
            class="border border-gray-200 rounded-lg p-4 relative"
          >
            <!-- Remove Button -->
            <button
              v-if="form.items.length > 1"
              type="button"
              @click="removeItem(index)"
              class="absolute top-2 right-2 p-1 text-gray-400 hover:text-red-500 transition-colors"
              title="Xóa sản phẩm"
            >
              <svg xmlns="http://www.w3.org/2000/svg" class="h-5 w-5" fill="none" viewBox="0 0 24 24" stroke="currentColor">
                <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M6 18L18 6M6 6l12 12" />
              </svg>
            </button>

            <div class="grid grid-cols-1 md:grid-cols-12 gap-4">
              <!-- Item Selection - 5 cols -->
              <div class="md:col-span-5">
                <label class="block text-sm font-medium text-gray-700 mb-1">
                  Sản phẩm <span class="text-red-500">*</span>
                </label>
                <div class="relative">
                  <!-- Search Input (when no item selected) -->
                  <input
                    v-if="!item.item_code"
                    type="text"
                    v-model="item.searchQuery"
                    @input="searchItems(index)"
                    @focus="onFocusSearch(index)"
                    @blur="hideDropdown(index)"
                    placeholder="Tìm kiếm sản phẩm..."
                    class="w-full px-3 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-primary focus:border-primary"
                  />
                  
                  <!-- Selected Item Display -->
                  <div
                    v-else
                    :class="[
                      'w-full px-3 py-2 border rounded-lg flex justify-between items-center',
                      item.available_qty === 0 && item.total_qty > 0 ? 'border-orange-300 bg-orange-50' : 'border-gray-300 bg-gray-50'
                    ]"
                  >
                    <div class="flex-1 min-w-0">
                      <span class="font-medium">{{ item.item_code }}</span>
                      <span class="text-gray-600 text-sm ml-2">{{ item.item_name }}</span>
                      <div class="text-xs mt-0.5" :class="item.available_qty > 0 ? 'text-green-600' : 'text-red-600'">
                        <template v-if="item.available_qty > 0">
                          Tồn kho: {{ formatNumber(item.available_qty) }} {{ translateUOM(item.uom) }}
                        </template>
                        <template v-else-if="item.total_qty > 0">
                          <span class="text-orange-600">⚠ Không có trong kho này</span>
                          <span class="text-gray-500 ml-1">(Tổng tồn: {{ formatNumber(item.total_qty) }} {{ translateUOM(item.uom) }})</span>
                        </template>
                        <template v-else>
                          Hết hàng
                        </template>
                      </div>
                    </div>
                    <button
                      type="button"
                      @click="clearItem(index)"
                      class="text-gray-400 hover:text-gray-600 ml-2"
                    >
                      <svg xmlns="http://www.w3.org/2000/svg" class="h-4 w-4" fill="none" viewBox="0 0 24 24" stroke="currentColor">
                        <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M6 18L18 6M6 6l12 12" />
                      </svg>
                    </button>
                  </div>

                  <!-- Dropdown -->
                  <div
                    v-if="item.showDropdown && item.searchResults.length > 0"
                    class="absolute z-50 w-full mt-1 bg-white border border-gray-200 rounded-lg shadow-lg max-h-60 overflow-auto"
                  >
                    <div
                      v-for="result in item.searchResults"
                      :key="result.item_code"
                      @mousedown.prevent="selectItem(index, result)"
                      class="px-4 py-2 hover:bg-gray-100 cursor-pointer border-b border-gray-100 last:border-b-0"
                    >
                      <div class="font-medium text-gray-900">{{ result.item_code }}</div>
                      <div class="text-sm text-gray-600">{{ result.item_name }}</div>
                      <div class="text-xs flex items-center gap-2 mt-0.5">
                        <span class="text-gray-400">{{ translateUOM(result.stock_uom) }}</span>
                        <!-- Giá bán -->
                        <span v-if="result.standard_selling_rate" class="text-blue-600">
                          Giá: {{ formatCurrency(result.standard_selling_rate) }}
                        </span>
                        <!-- Hiển thị tồn kho thông minh -->
                        <template v-if="form.set_warehouse && result.warehouse_qty !== null && result.warehouse_qty !== undefined">
                          <span :class="result.warehouse_qty > 0 ? 'text-green-600' : 'text-orange-500'">
                            Tồn: {{ formatNumber(result.warehouse_qty || 0) }}
                          </span>
                          <span v-if="result.actual_qty !== result.warehouse_qty" class="text-gray-400">
                            (Tổng: {{ formatNumber(result.actual_qty || 0) }})
                          </span>
                        </template>
                        <template v-else>
                          <span :class="result.actual_qty > 0 ? 'text-green-600' : 'text-red-500'">
                            Tồn: {{ formatNumber(result.actual_qty || 0) }}
                          </span>
                        </template>
                      </div>
                    </div>
                  </div>
                  
                  <!-- Loading indicator -->
                  <div
                    v-if="item.isSearching"
                    class="absolute z-50 w-full mt-1 bg-white border border-gray-200 rounded-lg shadow-lg p-3 text-center text-gray-500"
                  >
                    <svg class="animate-spin h-5 w-5 mx-auto text-primary" xmlns="http://www.w3.org/2000/svg" fill="none" viewBox="0 0 24 24">
                      <circle class="opacity-25" cx="12" cy="12" r="10" stroke="currentColor" stroke-width="4"></circle>
                      <path class="opacity-75" fill="currentColor" d="M4 12a8 8 0 018-8V0C5.373 0 0 5.373 0 12h4zm2 5.291A7.962 7.962 0 014 12H0c0 3.042 1.135 5.824 3 7.938l3-2.647z"></path>
                    </svg>
                    Đang tìm kiếm...
                  </div>
                  
                  <!-- No results -->
                  <div
                    v-if="item.showDropdown && !item.isSearching && item.searchQuery.length >= 1 && item.searchResults.length === 0 && item.hasSearched"
                    class="absolute z-50 w-full mt-1 bg-white border border-gray-200 rounded-lg shadow-lg p-3 text-center text-gray-500"
                  >
                    Không tìm thấy sản phẩm
                  </div>
                </div>
              </div>

              <!-- Quantity - 2 cols -->
              <div class="md:col-span-2">
                <label class="block text-sm font-medium text-gray-700 mb-1">
                  Số lượng <span class="text-red-500">*</span>
                </label>
                <div class="relative">
                  <input
                    type="number"
                    v-model.number="item.qty"
                    min="1"
                    step="1"
                    :max="item.available_qty || undefined"
                    required
                    @change="item.qty = Math.max(1, Math.floor(item.qty))"
                    :class="[
                      'w-full px-3 py-2 pr-16 border rounded-lg focus:ring-2 focus:ring-primary focus:border-primary',
                      item.qty > item.available_qty && item.available_qty > 0 ? 'border-red-300 bg-red-50' : 'border-gray-300',
                      item.available_qty === 0 && item.item_code ? 'border-orange-300 bg-orange-50' : ''
                    ]"
                    placeholder="0"
                  />
                  <span class="absolute right-3 top-1/2 -translate-y-1/2 text-gray-500 text-sm font-medium">
                    {{ translateUOM(item.uom) }}
                  </span>
                </div>
                <!-- Warning messages -->
                <p v-if="item.qty > item.available_qty && item.available_qty > 0" class="text-xs text-red-500 mt-1">
                  Vượt quá tồn kho ({{ formatNumber(item.available_qty) }})
                </p>
                <p v-else-if="item.available_qty === 0 && item.total_qty > 0 && item.item_code" class="text-xs text-orange-600 mt-1">
                  Chọn kho khác hoặc nhập thêm hàng
                </p>
                <p v-else-if="item.available_qty === 0 && item.item_code && item.total_qty === 0" class="text-xs text-red-500 mt-1">
                  Hết hàng trong tất cả kho
                </p>
              </div>

              <!-- Unit Price - 2 cols -->
              <div class="md:col-span-2">
                <label class="block text-sm font-medium text-gray-700 mb-1">
                  Đơn giá <span class="text-red-500">*</span>
                </label>
                <input
                  type="number"
                  v-model.number="item.rate"
                  min="0"
                  step="1000"
                  class="w-full px-3 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-primary focus:border-primary"
                  placeholder="0"
                />
                <p v-if="item.standard_rate && item.rate !== item.standard_rate" class="text-xs text-gray-400 mt-1">
                  Giá gốc: {{ formatCurrency(item.standard_rate) }}
                </p>
              </div>

              <!-- Amount - 3 cols -->
              <div class="md:col-span-3">
                <label class="block text-sm font-medium text-gray-700 mb-1">
                  Thành tiền
                </label>
                <div class="px-3 py-2 bg-gray-100 border border-gray-300 rounded-lg text-gray-900 font-medium">
                  {{ formatCurrency(item.qty * (item.rate || 0)) }}
                </div>
              </div>
            </div>
          </div>

          <!-- Empty state -->
          <div v-if="form.items.length === 0" class="text-center py-8 text-gray-500">
            Chưa có sản phẩm nào. Nhấn "Thêm sản phẩm" để bắt đầu.
          </div>
        </div>

        <!-- Total -->
        <div class="mt-4 pt-4 border-t border-gray-200 flex justify-between items-center">
          <div class="text-sm text-gray-600">
            <span class="font-medium">{{ form.items.filter(i => i.item_code).length }}</span> sản phẩm
          </div>
          <div class="text-right">
            <span class="text-gray-600">Tổng cộng:</span>
            <span class="ml-2 text-xl font-bold text-primary">{{ formatCurrency(grandTotal) }}</span>
          </div>
        </div>
      </div>

      <!-- Actions -->
      <div class="flex items-center justify-end gap-4">
        <button
          type="button"
          @click="router.back()"
          class="px-6 py-2 border border-gray-300 text-gray-700 rounded-lg hover:bg-gray-50 transition-colors"
        >
          Hủy
        </button>
        <button
          type="submit"
          :disabled="submitting || !isValid"
          class="px-6 py-2 bg-primary text-white rounded-lg hover:bg-primary-light disabled:opacity-50 disabled:cursor-not-allowed transition-colors flex items-center gap-2"
        >
          <svg v-if="submitting" class="animate-spin h-5 w-5" xmlns="http://www.w3.org/2000/svg" fill="none" viewBox="0 0 24 24">
            <circle class="opacity-25" cx="12" cy="12" r="10" stroke="currentColor" stroke-width="4"></circle>
            <path class="opacity-75" fill="currentColor" d="M4 12a8 8 0 018-8V0C5.373 0 0 5.373 0 12h4zm2 5.291A7.962 7.962 0 014 12H0c0 3.042 1.135 5.824 3 7.938l3-2.647z"></path>
          </svg>
          {{ submitting ? 'Đang tạo...' : 'Tạo hóa đơn' }}
        </button>
      </div>
    </form>

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
import { ref, reactive, computed, onMounted, watch } from 'vue'
import { useRouter } from 'vue-router'
import { salesInvoiceAPI, stockAPI } from '@/api'

const router = useRouter()

// UOM Translation Map
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
  'Pack': 'Gói',
  'pack': 'Gói',
  'Roll': 'Cuộn',
  'roll': 'Cuộn',
  'Liter': 'Lít',
  'liter': 'Lít',
  'L': 'Lít',
  'l': 'Lít',
}

// Translate UOM to Vietnamese
const translateUOM = (uom) => {
  if (!uom) return ''
  return UOM_TRANSLATIONS[uom] || uom
}

// State
const submitting = ref(false)
const customers = ref([])
const warehouses = ref([])
const customerSearch = ref('')
const showCustomerDropdown = ref(false)
const isSearchingCustomer = ref(false)
const hasSearchedCustomer = ref(false)
const toast = ref({ show: false, type: 'success', message: '' })

// Create empty item template
const createEmptyItem = () => ({
  item_code: '',
  item_name: '',
  uom: '',
  qty: 1,
  rate: 0,
  standard_rate: 0,
  available_qty: 0,
  total_qty: 0,
  searchQuery: '',
  searchResults: [],
  showDropdown: false,
  isSearching: false,
  hasSearched: false,
  searchTimeout: null
})

// Form state
const form = reactive({
  customer: '',
  customer_name: '',
  posting_date: new Date().toISOString().split('T')[0],
  due_date: '',
  set_warehouse: '',
  remarks: '',
  items: [createEmptyItem()]
})

// Computed
const grandTotal = computed(() => {
  return form.items.reduce((sum, item) => sum + (item.qty || 0) * (item.rate || 0), 0)
})

const isValid = computed(() => {
  if (!form.customer) return false
  
  const validItems = form.items.filter(item => 
    item.item_code && item.qty > 0 && item.rate > 0
  )
  if (validItems.length === 0) return false
  
  return true
})

// Watch warehouse change to update stock for all items
watch(() => form.set_warehouse, async (newWarehouse) => {
  if (newWarehouse) {
    for (const item of form.items) {
      if (item.item_code) {
        await updateItemStock(item)
      }
    }
  }
})

// Methods
const formatNumber = (num) => {
  if (!num) return '0'
  return new Intl.NumberFormat('vi-VN').format(num)
}

const formatCurrency = (amount) => {
  if (!amount) return '0 ₫'
  return new Intl.NumberFormat('vi-VN', { style: 'currency', currency: 'VND' }).format(amount)
}

const showToast = (type, message) => {
  toast.value = { show: true, type, message }
  setTimeout(() => {
    toast.value.show = false
  }, 3000)
}

// Customer search
let customerTimeout = null
const searchCustomers = () => {
  if (customerTimeout) clearTimeout(customerTimeout)
  
  if (!customerSearch.value || customerSearch.value.length < 1) {
    customers.value = []
    hasSearchedCustomer.value = false
    return
  }
  
  isSearchingCustomer.value = true
  showCustomerDropdown.value = true
  
  customerTimeout = setTimeout(async () => {
    try {
      const res = await fetch(`/api/method/xuanhoa_app.api.get_customers?query=${encodeURIComponent(customerSearch.value)}&limit=10`, {
        credentials: 'include'
      })
      const data = await res.json()
      if (data.message) {
        customers.value = data.message
        hasSearchedCustomer.value = true
      }
    } catch (e) {
      console.error('Error searching customers:', e)
      customers.value = []
      hasSearchedCustomer.value = true
    } finally {
      isSearchingCustomer.value = false
    }
  }, 300)
}

const hideCustomerDropdown = () => {
  setTimeout(() => {
    showCustomerDropdown.value = false
  }, 200)
}

const selectCustomer = (customer) => {
  form.customer = customer.name
  form.customer_name = customer.customer_name
  customerSearch.value = ''
  showCustomerDropdown.value = false
  customers.value = []
}

const clearCustomer = () => {
  form.customer = ''
  form.customer_name = ''
  customerSearch.value = ''
  customers.value = []
  hasSearchedCustomer.value = false
}

// Item functions
const addItem = () => {
  form.items.push(createEmptyItem())
}

const removeItem = (index) => {
  if (form.items.length > 1) {
    form.items.splice(index, 1)
  }
}

const clearItem = (index) => {
  const item = form.items[index]
  item.item_code = ''
  item.item_name = ''
  item.uom = ''
  item.qty = 1
  item.rate = 0
  item.standard_rate = 0
  item.available_qty = 0
  item.total_qty = 0
  item.searchQuery = ''
  item.searchResults = []
  item.hasSearched = false
}

const onFocusSearch = (index) => {
  const item = form.items[index]
  item.showDropdown = true
  if (item.searchQuery && item.searchQuery.length >= 1) {
    searchItems(index)
  }
}

const searchItems = (index) => {
  const item = form.items[index]
  
  if (item.searchTimeout) {
    clearTimeout(item.searchTimeout)
  }
  
  if (!item.searchQuery || item.searchQuery.length < 1) {
    item.searchResults = []
    item.hasSearched = false
    return
  }
  
  item.isSearching = true
  item.showDropdown = true
  
  item.searchTimeout = setTimeout(async () => {
    try {
      const results = await stockAPI.searchItems(item.searchQuery, null, form.set_warehouse || null)
      item.searchResults = results || []
      item.hasSearched = true
    } catch (error) {
      console.error('Error searching items:', error)
      item.searchResults = []
      item.hasSearched = true
    } finally {
      item.isSearching = false
    }
  }, 300)
}

const hideDropdown = (index) => {
  setTimeout(() => {
    form.items[index].showDropdown = false
  }, 200)
}

const updateItemStock = async (item) => {
  if (!item.item_code) {
    item.available_qty = 0
    item.total_qty = 0
    return
  }
  
  try {
    const stockInfo = await stockAPI.getItemStock(item.item_code, form.set_warehouse || null)
    
    if (!stockInfo) {
      item.available_qty = 0
      item.total_qty = 0
      return
    }
    
    item.total_qty = stockInfo.total_qty || 0
    
    if (form.set_warehouse) {
      if (stockInfo.warehouse_qty !== undefined) {
        item.available_qty = stockInfo.warehouse_qty || 0
      } else {
        const warehouseStock = stockInfo.by_warehouse?.find(w => w.warehouse === form.set_warehouse)
        if (warehouseStock) {
          item.available_qty = warehouseStock.actual_qty || 0
        } else {
          item.available_qty = 0
        }
      }
    } else {
      item.available_qty = stockInfo.total_qty || 0
    }
  } catch (error) {
    console.error('Error getting item stock:', error)
    item.available_qty = 0
    item.total_qty = 0
  }
}

const selectItem = async (index, selectedItem) => {
  const item = form.items[index]
  item.item_code = selectedItem.item_code
  item.item_name = selectedItem.item_name
  item.uom = selectedItem.stock_uom
  // Tự động điền đơn giá từ standard_selling_rate
  item.rate = selectedItem.standard_selling_rate || selectedItem.valuation_rate || 0
  item.standard_rate = selectedItem.standard_selling_rate || 0
  item.showDropdown = false
  item.searchQuery = ''
  item.searchResults = []
  
  // Update stock info
  await updateItemStock(item)
}

const loadWarehouses = async () => {
  try {
    warehouses.value = await stockAPI.getWarehouses()
  } catch (error) {
    console.error('Error loading warehouses:', error)
    showToast('error', 'Không thể tải danh sách kho')
  }
}

const handleSubmit = async () => {
  if (!isValid.value) return
  
  submitting.value = true
  
  try {
    const validItems = form.items
      .filter(item => item.item_code && item.qty > 0 && item.rate > 0)
      .map(item => ({
        item_code: item.item_code,
        qty: item.qty,
        rate: item.rate,
        warehouse: form.set_warehouse
      }))
    
    const result = await salesInvoiceAPI.create({
      customer: form.customer,
      posting_date: form.posting_date,
      due_date: form.due_date,
      set_warehouse: form.set_warehouse,
      remarks: form.remarks,
      items: validItems
    })
    
    if (result.success) {
      showToast('success', result.message)
      setTimeout(() => {
        router.push(`/selling/invoices/${result.name}`)
      }, 1000)
    } else {
      showToast('error', result.message)
    }
  } catch (e) {
    console.error('Error creating invoice:', e)
    showToast('error', 'Có lỗi xảy ra khi tạo hóa đơn')
  } finally {
    submitting.value = false
  }
}

// Click outside to close dropdowns
const handleClickOutside = (e) => {
  if (!e.target.closest('.relative')) {
    showCustomerDropdown.value = false
    form.items.forEach(item => {
      item.showDropdown = false
    })
  }
}

// Initialize
onMounted(() => {
  loadWarehouses()
  document.addEventListener('click', handleClickOutside)
})
</script>
