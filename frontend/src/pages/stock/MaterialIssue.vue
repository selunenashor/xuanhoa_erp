<template>
  <div class="h-full">
    <!-- Main Form -->
    <div class="p-6 overflow-auto">
      <div class="max-w-4xl mx-auto">
        <!-- Header -->
        <div class="mb-6">
          <h1 class="text-2xl font-bold text-gray-900">Xuất kho</h1>
          <p class="text-gray-600">Tạo phiếu xuất kho nguyên vật liệu</p>
        </div>

        <!-- Form -->
        <form @submit.prevent="submitForm" class="space-y-6">
          <!-- Basic Info Card -->
          <div class="bg-white rounded-lg shadow p-6">
            <h2 class="text-lg font-semibold text-gray-900 mb-4">Thông tin chung</h2>
            
            <div class="grid grid-cols-1 md:grid-cols-2 gap-4">
              <!-- Source Warehouse -->
              <div>
                <label class="block text-sm font-medium text-gray-700 mb-1">
                  Kho xuất <span class="text-red-500">*</span>
                </label>
                <select
                  v-model="form.source_warehouse"
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
                  Ngày xuất <span class="text-red-500">*</span>
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
                  placeholder="Ghi chú cho phiếu xuất kho..."
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
                  <!-- Item Selection - 6 cols -->
                  <div class="md:col-span-6">
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
                            <!-- Hiển thị tồn kho thông minh -->
                            <template v-if="form.source_warehouse && result.warehouse_qty !== null">
                              <!-- Đã chọn kho: hiển thị cả tồn kho kho hiện tại và tổng -->
                              <span :class="result.warehouse_qty > 0 ? 'text-green-600' : 'text-orange-500'">
                                Tồn: {{ formatNumber(result.warehouse_qty || 0) }}
                              </span>
                              <span v-if="result.actual_qty !== result.warehouse_qty" class="text-gray-400">
                                (Tổng: {{ formatNumber(result.actual_qty || 0) }})
                              </span>
                            </template>
                            <template v-else>
                              <!-- Chưa chọn kho: hiển thị tổng tồn -->
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

                  <!-- Quantity - 3 cols -->
                  <div class="md:col-span-3">
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
                        :disabled="item.available_qty === 0"
                        @change="item.qty = Math.max(1, Math.floor(item.qty))"
                        :class="[
                          'w-full px-3 py-2 pr-16 border rounded-lg focus:ring-2 focus:ring-primary focus:border-primary',
                          item.qty > item.available_qty ? 'border-red-300 bg-red-50' : 'border-gray-300',
                          item.available_qty === 0 ? 'bg-gray-100 cursor-not-allowed' : ''
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
                    <p v-else-if="item.available_qty === 0 && item.item_code" class="text-xs text-red-500 mt-1">
                      Hết hàng trong tất cả kho
                    </p>
                  </div>

                  <!-- Valuation Rate (readonly) - 3 cols -->
                  <div class="md:col-span-3">
                    <label class="block text-sm font-medium text-gray-700 mb-1">
                      Giá trị
                    </label>
                    <div class="px-3 py-2 bg-gray-100 border border-gray-300 rounded-lg text-gray-700 font-medium">
                      {{ formatNumber(item.qty * (item.valuation_rate || 0)) }}
                    </div>
                    <p class="text-xs text-gray-400 mt-1">
                      Đơn giá: {{ formatNumber(item.valuation_rate || 0) }}
                    </p>
                  </div>
                </div>
              </div>
            </div>

            <!-- Total -->
            <div class="mt-4 pt-4 border-t border-gray-200 flex justify-between items-center">
              <div class="text-sm text-gray-600">
                <span class="font-medium">{{ form.items.filter(i => i.item_code).length }}</span> sản phẩm
              </div>
              <div class="text-right">
                <span class="text-gray-600">Tổng giá trị:</span>
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
              :disabled="loading || !canSubmit"
              class="px-6 py-2 text-white bg-primary rounded-lg hover:bg-primary-dark transition-colors disabled:opacity-50 disabled:cursor-not-allowed flex items-center gap-2"
            >
              <svg v-if="loading" class="animate-spin h-4 w-4" xmlns="http://www.w3.org/2000/svg" fill="none" viewBox="0 0 24 24">
                <circle class="opacity-25" cx="12" cy="12" r="10" stroke="currentColor" stroke-width="4"></circle>
                <path class="opacity-75" fill="currentColor" d="M4 12a8 8 0 018-8V0C5.373 0 0 5.373 0 12h4zm2 5.291A7.962 7.962 0 014 12H0c0 3.042 1.135 5.824 3 7.938l3-2.647z"></path>
              </svg>
              {{ loading ? 'Đang xử lý...' : 'Tạo phiếu xuất kho' }}
            </button>
          </div>
        </form>
      </div>
    </div>

    <!-- Toast Notification -->
    <div
      v-if="toast.show"
      :class="[
        'fixed bottom-4 right-4 px-4 py-3 rounded-lg shadow-lg flex items-center gap-2 transition-all transform z-50',
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
import { ref, reactive, computed, onMounted, watch } from 'vue'
import { useRouter } from 'vue-router'
import { stockAPI } from '@/api'

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
const warehouses = ref([])
const loading = ref(false)

// Create empty item template
const createEmptyItem = () => ({
  item_code: '',
  item_name: '',
  uom: '',
  qty: 1,
  available_qty: 0,
  total_qty: 0,  // Total stock across all warehouses
  valuation_rate: 0,
  searchQuery: '',
  searchResults: [],
  showDropdown: false,
  isSearching: false,
  hasSearched: false,
  searchTimeout: null
})

// Form state
const form = reactive({
  source_warehouse: '',
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
    return sum + (item.qty || 0) * (item.valuation_rate || 0)
  }, 0)
})

// Check if form can be submitted
const canSubmit = computed(() => {
  // Must have warehouse selected
  if (!form.source_warehouse) return false
  
  // Must have at least one valid item
  const validItems = form.items.filter(item => item.item_code && item.qty > 0)
  if (validItems.length === 0) return false
  
  // All items must not exceed available qty
  const hasOverQty = form.items.some(item => 
    item.item_code && item.qty > item.available_qty
  )
  if (hasOverQty) return false
  
  return true
})

// Watch warehouse change to update stock for all items
watch(() => form.source_warehouse, async (newWarehouse) => {
  if (newWarehouse) {
    // Update stock info for all selected items
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
  item.available_qty = 0
  item.total_qty = 0
  item.valuation_rate = 0
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
      // Gửi warehouse để API trả về tồn kho của kho đã chọn
      const results = await stockAPI.searchItems(item.searchQuery, null, form.source_warehouse || null)
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

// Update item stock based on selected warehouse
const updateItemStock = async (item) => {
  if (!item.item_code) {
    item.available_qty = 0
    item.total_qty = 0
    item.valuation_rate = 0
    return
  }
  
  try {
    // Get stock info - pass warehouse if selected
    const stockInfo = await stockAPI.getItemStock(item.item_code, form.source_warehouse || null)
    
    if (!stockInfo) {
      item.available_qty = 0
      item.total_qty = 0
      return
    }
    
    // Always store total qty for reference
    item.total_qty = stockInfo.total_qty || 0
    
    // If warehouse is selected, use warehouse-specific qty
    if (form.source_warehouse) {
      // Use warehouse_qty if available (direct from API when warehouse param passed)
      if (stockInfo.warehouse_qty !== undefined) {
        item.available_qty = stockInfo.warehouse_qty || 0
        item.valuation_rate = stockInfo.valuation_rate || 0
      } else {
        // Fallback: find in by_warehouse array
        const warehouseStock = stockInfo.by_warehouse?.find(w => w.warehouse === form.source_warehouse)
        if (warehouseStock) {
          item.available_qty = warehouseStock.actual_qty || 0
          item.valuation_rate = warehouseStock.valuation_rate || 
            (warehouseStock.stock_value && warehouseStock.actual_qty 
              ? warehouseStock.stock_value / warehouseStock.actual_qty 
              : 0)
        } else {
          // Item doesn't exist in this warehouse
          item.available_qty = 0
        }
      }
    } else {
      // No warehouse selected, show total stock
      item.available_qty = stockInfo.total_qty || 0
      item.valuation_rate = stockInfo.valuation_rate || 0
    }
  } catch (error) {
    console.error('Error getting item stock:', error)
    item.available_qty = 0
    item.total_qty = 0
  }
}

// Select item from dropdown
const selectItem = async (index, selectedItem) => {
  const item = form.items[index]
  item.item_code = selectedItem.item_code
  item.item_name = selectedItem.item_name
  item.uom = selectedItem.stock_uom
  item.valuation_rate = selectedItem.valuation_rate || selectedItem.rate || 0
  item.showDropdown = false
  item.searchQuery = ''
  item.searchResults = []
  
  // Always update stock - will use warehouse filter if selected
  await updateItemStock(item)
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
  form.source_warehouse = ''
  form.posting_date = new Date().toISOString().split('T')[0]
  form.remarks = ''
  form.items = [createEmptyItem()]
}

// Validate form
const validateForm = () => {
  if (!form.source_warehouse) {
    showToast('error', 'Vui lòng chọn kho xuất')
    return false
  }
  
  if (!form.posting_date) {
    showToast('error', 'Vui lòng chọn ngày xuất')
    return false
  }
  
  const validItems = form.items.filter(item => item.item_code && item.qty > 0)
  if (validItems.length === 0) {
    showToast('error', 'Vui lòng thêm ít nhất 1 sản phẩm')
    return false
  }
  
  // Check stock availability
  for (const item of validItems) {
    if (item.qty > item.available_qty) {
      showToast('error', `Sản phẩm ${item.item_code} vượt quá số lượng tồn kho`)
      return false
    }
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
        s_warehouse: form.source_warehouse
      }))
    
    const result = await stockAPI.createMaterialIssue({
      items,
      posting_date: form.posting_date,
      remarks: form.remarks
    })
    
    if (result.success) {
      showToast('success', `Đã tạo phiếu xuất kho: ${result.name}`)
      // Navigate to detail page after short delay
      setTimeout(() => {
        router.push(`/stock/entries/${result.name}`)
      }, 1500)
    } else {
      showToast('error', result.message || 'Không thể tạo phiếu xuất kho')
    }
  } catch (error) {
    console.error('Error creating material issue:', error)
    showToast('error', error.response?.data?.message || error.message || 'Không thể tạo phiếu xuất kho')
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
