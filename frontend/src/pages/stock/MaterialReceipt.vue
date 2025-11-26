<template>
  <div class="h-full">
    <!-- Main Form -->
    <div class="p-6 overflow-auto">
      <div class="max-w-4xl mx-auto">
        <!-- Header -->
        <div class="mb-6">
          <h1 class="text-2xl font-bold text-gray-900">Nhập kho</h1>
          <p class="text-gray-600">Tạo phiếu nhập kho nguyên vật liệu</p>
        </div>

        <!-- Form -->
        <form @submit.prevent="submitForm" class="space-y-6">
          <!-- Basic Info Card -->
          <div class="bg-white rounded-lg shadow p-6">
            <h2 class="text-lg font-semibold text-gray-900 mb-4">Thông tin chung</h2>
            
            <div class="grid grid-cols-1 md:grid-cols-2 gap-4">
              <!-- Target Warehouse -->
              <div>
                <label class="block text-sm font-medium text-gray-700 mb-1">
                  Kho nhập <span class="text-red-500">*</span>
                </label>
                <select
                  v-model="form.target_warehouse"
                  required
                  class="w-full px-3 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-primary focus:border-primary"
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
                  Ngày nhập <span class="text-red-500">*</span>
                </label>
                <input
                  type="date"
                  v-model="form.posting_date"
                  required
                  class="w-full px-3 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-primary focus:border-primary"
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
                  class="w-full px-3 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-primary focus:border-primary"
                  placeholder="Ghi chú cho phiếu nhập kho..."
                ></textarea>
              </div>
            </div>
          </div>

          <!-- Items Card -->
          <div class="bg-white rounded-lg shadow p-6">
            <div class="flex justify-between items-center mb-4">
              <h2 class="text-lg font-semibold text-gray-900">Danh sách sản phẩm</h2>
              <button
                type="button"
                @click="addItem"
                class="flex items-center gap-2 px-3 py-2 text-sm font-medium text-white bg-primary rounded-lg hover:bg-primary-dark transition-colors"
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
                        class="w-full px-3 py-2 border border-gray-300 rounded-lg bg-gray-50 flex justify-between items-center"
                      >
                        <div>
                          <span class="font-medium">{{ item.item_code }}</span>
                          <span class="text-gray-600 text-sm ml-2">{{ item.item_name }}</span>
                        </div>
                        <button
                          type="button"
                          @click="clearItem(index)"
                          class="text-gray-400 hover:text-gray-600"
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
                          <div class="text-xs text-gray-400">
                            {{ translateUOM(result.stock_uom) }} | Tồn: {{ result.actual_qty || 0 }}
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

                  <!-- Quantity - 3 cols -->
                  <div class="md:col-span-3">
                    <label class="block text-sm font-medium text-gray-700 mb-1">
                      Số lượng <span class="text-red-500">*</span>
                    </label>
                    <div class="relative">
                      <input
                        type="number"
                        v-model.number="item.qty"
                        min="0.01"
                        step="0.01"
                        required
                        class="w-full px-3 py-2 pr-16 border border-gray-300 rounded-lg focus:ring-2 focus:ring-primary focus:border-primary"
                        placeholder="0"
                      />
                      <span class="absolute right-3 top-1/2 -translate-y-1/2 text-gray-500 text-sm font-medium">
                        {{ translateUOM(item.uom) }}
                      </span>
                    </div>
                  </div>

                  <!-- Rate - 2 cols -->
                  <div class="md:col-span-2">
                    <label class="block text-sm font-medium text-gray-700 mb-1">
                      Đơn giá
                    </label>
                    <input
                      type="number"
                      v-model.number="item.rate"
                      min="0"
                      step="100"
                      class="w-full px-3 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-primary focus:border-primary"
                      placeholder="0"
                    />
                  </div>

                  <!-- Amount - 2 cols -->
                  <div class="md:col-span-2">
                    <label class="block text-sm font-medium text-gray-700 mb-1">
                      Thành tiền
                    </label>
                    <div class="px-3 py-2 bg-gray-100 border border-gray-300 rounded-lg text-gray-700 font-medium">
                      {{ formatNumber(item.qty * item.rate) }}
                    </div>
                  </div>
                </div>
              </div>
            </div>

            <!-- Total -->
            <div class="mt-4 pt-4 border-t border-gray-200 flex justify-end">
              <div class="text-right">
                <span class="text-gray-600">Tổng cộng:</span>
                <span class="ml-2 text-xl font-bold text-primary">{{ formatNumber(totalAmount) }} VND</span>
              </div>
            </div>
          </div>

          <!-- Actions -->
          <div class="flex justify-end gap-3">
            <button
              type="button"
              @click="resetForm"
              class="px-4 py-2 text-gray-700 bg-gray-100 rounded-lg hover:bg-gray-200 transition-colors"
            >
              Làm mới
            </button>
            <button
              type="submit"
              :disabled="loading"
              class="px-6 py-2 text-white bg-primary rounded-lg hover:bg-primary-dark transition-colors disabled:opacity-50 disabled:cursor-not-allowed flex items-center gap-2"
            >
              <svg v-if="loading" class="animate-spin h-4 w-4" xmlns="http://www.w3.org/2000/svg" fill="none" viewBox="0 0 24 24">
                <circle class="opacity-25" cx="12" cy="12" r="10" stroke="currentColor" stroke-width="4"></circle>
                <path class="opacity-75" fill="currentColor" d="M4 12a8 8 0 018-8V0C5.373 0 0 5.373 0 12h4zm2 5.291A7.962 7.962 0 014 12H0c0 3.042 1.135 5.824 3 7.938l3-2.647z"></path>
              </svg>
              {{ loading ? 'Đang xử lý...' : 'Tạo phiếu nhập kho' }}
            </button>
          </div>
        </form>
      </div>
    </div>

    <!-- Toast Notification -->
    <div
      v-if="toast.show"
      :class="[
        'fixed bottom-4 right-4 px-4 py-3 rounded-lg shadow-lg flex items-center gap-2 transition-all transform',
        toast.type === 'success' ? 'bg-green-500 text-white' : 'bg-red-500 text-white'
      ]"
    >
      <svg v-if="toast.type === 'success'" xmlns="http://www.w3.org/2000/svg" class="h-5 w-5" fill="none" viewBox="0 0 24 24" stroke="currentColor">
        <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M5 13l4 4L19 7" />
      </svg>
      <svg v-else xmlns="http://www.w3.org/2000/svg" class="h-5 w-5" fill="none" viewBox="0 0 24 24" stroke="currentColor">
        <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M6 18L18 6M6 6l12 12" />
      </svg>
      {{ toast.message }}
    </div>
  </div>
</template>

<script setup>
import { ref, reactive, computed, onMounted } from 'vue'
import { stockAPI } from '@/api'

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
const warehouses = ref([])
const loading = ref(false)

// Create empty item template
const createEmptyItem = () => ({
  item_code: '',
  item_name: '',
  uom: '',
  qty: 1,
  rate: 0,
  searchQuery: '',
  searchResults: [],
  showDropdown: false,
  isSearching: false,
  hasSearched: false,
  searchTimeout: null
})

// Form state
const form = reactive({
  target_warehouse: '',
  posting_date: new Date().toISOString().split('T')[0],
  remarks: '',
  items: [createEmptyItem()]
})

// Toast
const toast = reactive({
  show: false,
  type: 'success',
  message: ''
})

// Computed
const totalAmount = computed(() => {
  return form.items.reduce((sum, item) => {
    return sum + (item.qty || 0) * (item.rate || 0)
  }, 0)
})

// Methods
const formatNumber = (num) => {
  if (!num) return '0'
  return new Intl.NumberFormat('vi-VN').format(num)
}

const showToast = (type, message) => {
  toast.type = type
  toast.message = message
  toast.show = true
  setTimeout(() => {
    toast.show = false
  }, 3000)
}

// Add new item
const addItem = () => {
  form.items.push(createEmptyItem())
}

// Remove item
const removeItem = (index) => {
  if (form.items.length > 1) {
    form.items.splice(index, 1)
  }
}

// Clear selected item
const clearItem = (index) => {
  const item = form.items[index]
  item.item_code = ''
  item.item_name = ''
  item.uom = ''
  item.qty = 1
  item.rate = 0
  item.searchQuery = ''
  item.searchResults = []
  item.hasSearched = false
}

// Focus on search input
const onFocusSearch = (index) => {
  const item = form.items[index]
  item.showDropdown = true
  // If there's already a search query, search again
  if (item.searchQuery && item.searchQuery.length >= 1) {
    searchItems(index)
  }
}

// Search items with debounce
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
      console.log('Searching for:', item.searchQuery)
      const results = await stockAPI.searchItems(item.searchQuery)
      console.log('Search results:', results)
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

// Hide dropdown with delay
const hideDropdown = (index) => {
  setTimeout(() => {
    form.items[index].showDropdown = false
  }, 200)
}

// Select item from dropdown
const selectItem = (index, selectedItem) => {
  const item = form.items[index]
  item.item_code = selectedItem.item_code
  item.item_name = selectedItem.item_name
  item.uom = selectedItem.stock_uom
  // Sử dụng rate từ API (đã được tính sẵn) hoặc fallback
  item.rate = selectedItem.rate || selectedItem.valuation_rate || selectedItem.standard_rate || 0
  item.showDropdown = false
  item.searchQuery = ''
  item.searchResults = []
}

// Load warehouses
const loadWarehouses = async () => {
  try {
    warehouses.value = await stockAPI.getWarehouses()
  } catch (error) {
    console.error('Error loading warehouses:', error)
    showToast('error', 'Không thể tải danh sách kho')
  }
}

// Reset form
const resetForm = () => {
  form.target_warehouse = ''
  form.posting_date = new Date().toISOString().split('T')[0]
  form.remarks = ''
  form.items = [createEmptyItem()]
}

// Validate form
const validateForm = () => {
  if (!form.target_warehouse) {
    showToast('error', 'Vui lòng chọn kho nhập')
    return false
  }
  
  if (!form.posting_date) {
    showToast('error', 'Vui lòng chọn ngày nhập')
    return false
  }
  
  const validItems = form.items.filter(item => item.item_code && item.qty > 0)
  if (validItems.length === 0) {
    showToast('error', 'Vui lòng thêm ít nhất 1 sản phẩm')
    return false
  }
  
  return true
}

// Submit form
const submitForm = async () => {
  if (!validateForm()) return
  
  loading.value = true
  try {
    // Prepare items for API
    const items = form.items
      .filter(item => item.item_code && item.qty > 0)
      .map(item => ({
        item_code: item.item_code,
        qty: item.qty,
        basic_rate: item.rate,
        t_warehouse: form.target_warehouse
      }))
    
    const result = await stockAPI.createMaterialReceipt({
      items,
      posting_date: form.posting_date,
      remarks: form.remarks
    })
    
    showToast('success', `Đã tạo phiếu nhập kho: ${result.name}`)
    resetForm()
  } catch (error) {
    console.error('Error creating material receipt:', error)
    showToast('error', error.message || 'Không thể tạo phiếu nhập kho')
  } finally {
    loading.value = false
  }
}

// Initialize
onMounted(() => {
  loadWarehouses()
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

.focus\:ring-primary:focus {
  --tw-ring-color: #055568;
}

.focus\:border-primary:focus {
  border-color: #055568;
}

.hover\:bg-primary-dark:hover {
  background-color: #044454;
}
</style>
