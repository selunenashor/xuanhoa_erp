<template>
  <div class="h-full">
    <div class="p-6 overflow-auto">
      <div class="max-w-3xl mx-auto">
        <!-- Header -->
        <div class="mb-6">
          <div class="flex items-center gap-4 mb-2">
            <router-link 
              to="/production/orders"
              class="p-2 text-gray-500 hover:text-gray-700 hover:bg-gray-100 rounded-lg transition-colors"
            >
              <svg class="w-5 h-5" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M15 19l-7-7 7-7" />
              </svg>
            </router-link>
            <div>
              <h1 class="text-2xl font-bold text-gray-900">Tạo lệnh sản xuất</h1>
              <p class="text-gray-600">Chọn sản phẩm và BOM để tạo lệnh sản xuất</p>
            </div>
          </div>
        </div>

        <!-- Form -->
        <form @submit.prevent="submitForm" class="space-y-6">
          <!-- Product & BOM Selection -->
          <div class="bg-white rounded-lg shadow p-6">
            <h2 class="text-lg font-semibold text-gray-900 mb-4">Chọn sản phẩm & BOM</h2>
            
            <!-- Product Selector with Autocomplete -->
            <div class="mb-4 relative">
              <label class="block text-sm font-medium text-gray-700 mb-1">
                Sản phẩm <span class="text-red-500">*</span>
              </label>
              <div class="relative">
                <input
                  type="text"
                  v-model="productSearch"
                  @input="onProductSearch"
                  @focus="showProductDropdown = true"
                  @blur="hideProductDropdown"
                  placeholder="Nhập mã hoặc tên sản phẩm..."
                  class="w-full px-3 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-primary focus:border-primary"
                />
                <!-- Clear button -->
                <button 
                  v-if="form.item" 
                  type="button"
                  @mousedown.prevent="clearProduct"
                  class="absolute right-2 top-1/2 -translate-y-1/2 p-1 text-gray-400 hover:text-gray-600"
                >
                  <svg xmlns="http://www.w3.org/2000/svg" class="h-5 w-5" fill="none" viewBox="0 0 24 24" stroke="currentColor">
                    <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M6 18L18 6M6 6l12 12" />
                  </svg>
                </button>
              </div>
              
              <!-- Product Dropdown -->
              <div 
                v-if="showProductDropdown && filteredProducts.length > 0"
                class="absolute z-20 w-full mt-1 bg-white border border-gray-200 rounded-lg shadow-lg max-h-60 overflow-y-auto"
              >
                <div
                  v-for="product in filteredProducts"
                  :key="product.item_code"
                  @mousedown.prevent="selectProduct(product)"
                  class="px-3 py-2 hover:bg-gray-100 cursor-pointer"
                >
                  <div class="font-medium text-gray-900">{{ product.item_code }}</div>
                  <div class="text-sm text-gray-500">{{ product.item_name }}</div>
                </div>
              </div>
              
              <!-- No results -->
              <div 
                v-if="showProductDropdown && productSearch && filteredProducts.length === 0"
                class="absolute z-20 w-full mt-1 bg-white border border-gray-200 rounded-lg shadow-lg p-3 text-center text-gray-500"
              >
                Không tìm thấy sản phẩm
              </div>
              
              <!-- Selected product display -->
              <div v-if="form.item && selectedProduct" class="mt-2 p-2 bg-primary/5 border border-primary/20 rounded-lg">
                <div class="flex items-center gap-2">
                  <svg xmlns="http://www.w3.org/2000/svg" class="h-5 w-5 text-primary" fill="none" viewBox="0 0 24 24" stroke="currentColor">
                    <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M5 13l4 4L19 7" />
                  </svg>
                  <span class="font-medium text-gray-900">{{ selectedProduct.item_code }}</span>
                  <span class="text-gray-500">-</span>
                  <span class="text-gray-700">{{ selectedProduct.item_name }}</span>
                </div>
              </div>
            </div>

            <!-- No BOM Warning -->
            <div v-if="form.item && !loadingBOMs && productBOMs.length === 0" class="mb-4 p-4 bg-red-50 border border-red-200 rounded-lg">
              <div class="flex items-start gap-3">
                <svg xmlns="http://www.w3.org/2000/svg" class="h-6 w-6 text-red-500 flex-shrink-0" fill="none" viewBox="0 0 24 24" stroke="currentColor">
                  <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M12 9v2m0 4h.01m-6.938 4h13.856c1.54 0 2.502-1.667 1.732-3L13.732 4c-.77-1.333-2.694-1.333-3.464 0L3.34 16c-.77 1.333.192 3 1.732 3z" />
                </svg>
                <div>
                  <h4 class="font-medium text-red-800">Sản phẩm chưa có BOM</h4>
                  <p class="text-sm text-red-600 mt-1">
                    Sản phẩm này chưa được tạo định mức sản xuất (BOM). 
                    Vui lòng <router-link to="/production/boms" class="underline font-medium hover:text-red-800">tạo BOM</router-link> trước khi tạo lệnh sản xuất.
                  </p>
                </div>
              </div>
            </div>

            <!-- Loading BOMs -->
            <div v-if="loadingBOMs" class="mb-4 flex items-center gap-2 text-gray-500">
              <svg class="animate-spin h-5 w-5" xmlns="http://www.w3.org/2000/svg" fill="none" viewBox="0 0 24 24">
                <circle class="opacity-25" cx="12" cy="12" r="10" stroke="currentColor" stroke-width="4"></circle>
                <path class="opacity-75" fill="currentColor" d="M4 12a8 8 0 018-8V0C5.373 0 0 5.373 0 12h4zm2 5.291A7.962 7.962 0 014 12H0c0 3.042 1.135 5.824 3 7.938l3-2.647z"></path>
              </svg>
              <span>Đang tải danh sách BOM...</span>
            </div>

            <!-- BOM Selector (Select dropdown) -->
            <div v-if="form.item && productBOMs.length > 0" class="mb-4">
              <label class="block text-sm font-medium text-gray-700 mb-1">
                Định mức sản xuất (BOM) <span class="text-red-500">*</span>
              </label>
              <select
                v-model="form.bom_no"
                @change="onBOMChange"
                required
                class="w-full px-3 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-primary focus:border-primary"
              >
                <option value="">-- Chọn BOM --</option>
                <option v-for="bom in productBOMs" :key="bom.name" :value="bom.name">
                  {{ bom.name }} {{ bom.is_default ? '⭐' : '' }} - {{ bom.item_count }} NVL - {{ formatNumber(bom.raw_material_cost || bom.total_cost) }} VND/{{ translateUOM(bom.uom) }}
                </option>
              </select>
              <p v-if="productBOMs.length > 1" class="text-xs text-gray-500 mt-1">
                Có {{ productBOMs.length }} BOM cho sản phẩm này. ⭐ = BOM mặc định
              </p>
            </div>

            <!-- Selected BOM Info -->
            <div v-if="selectedBOM" class="bg-gray-50 rounded-lg p-4">
              <div class="flex items-start gap-4">
                <div class="flex-1">
                  <div class="font-medium text-gray-900">{{ selectedBOM.item }}</div>
                  <div class="text-sm text-gray-600">{{ selectedBOM.item_name }}</div>
                  <div class="mt-2 flex flex-wrap gap-2">
                    <span class="px-2 py-1 bg-primary/10 text-primary text-xs rounded-full">
                      {{ selectedBOM.item_count }} nguyên liệu
                    </span>
                    <span class="px-2 py-1 bg-gray-200 text-gray-600 text-xs rounded-full">
                      {{ translateUOM(selectedBOM.uom) }}
                    </span>
                    <span v-if="selectedBOM.is_default" class="px-2 py-1 bg-warning/10 text-warning text-xs rounded-full">
                      ⭐ BOM mặc định
                    </span>
                  </div>
                </div>
                <div class="text-right">
                  <div class="text-sm text-gray-500">Chi phí NVL/đơn vị</div>
                  <div class="font-semibold text-gray-900">{{ formatNumber(selectedBOM.raw_material_cost || selectedBOM.total_cost) }} VND</div>
                </div>
              </div>

              <!-- BOM Items Preview -->
              <div v-if="bomItems.length > 0" class="mt-4 pt-4 border-t border-gray-200">
                <div class="text-sm font-medium text-gray-700 mb-2">Nguyên liệu cần:</div>
                <div class="grid grid-cols-1 md:grid-cols-2 gap-2">
                  <div 
                    v-for="item in bomItems" 
                    :key="item.item_code"
                    class="flex justify-between items-center text-sm bg-white p-2 rounded border"
                  >
                    <span class="text-gray-700">{{ item.item_name }}</span>
                    <span class="font-medium text-gray-900">
                      {{ item.qty }} x {{ form.qty || 1 }} = {{ formatNumber(item.qty * (form.qty || 1)) }} {{ translateUOM(item.uom) }}
                    </span>
                  </div>
                </div>
              </div>
            </div>
          </div>

          <!-- Quantity & Dates -->
          <div class="bg-white rounded-lg shadow p-6">
            <h2 class="text-lg font-semibold text-gray-900 mb-4">Số lượng & Thời gian</h2>
            
            <div class="grid grid-cols-1 md:grid-cols-3 gap-4">
              <!-- Quantity -->
              <div>
                <label class="block text-sm font-medium text-gray-700 mb-1">
                  Số lượng sản xuất <span class="text-red-500">*</span>
                </label>
                <input
                  type="number"
                  v-model.number="form.qty"
                  min="1"
                  step="1"
                  required
                  @change="form.qty = Math.max(1, Math.floor(form.qty))"
                  class="w-full px-3 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-primary focus:border-primary"
                  placeholder="100"
                />
              </div>

              <!-- Planned Start Date -->
              <div>
                <label class="block text-sm font-medium text-gray-700 mb-1">
                  Ngày bắt đầu dự kiến
                </label>
                <input
                  type="date"
                  v-model="form.planned_start_date"
                  class="w-full px-3 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-primary focus:border-primary"
                />
              </div>

              <!-- Expected Delivery Date -->
              <div>
                <label class="block text-sm font-medium text-gray-700 mb-1">
                  Ngày hoàn thành dự kiến
                </label>
                <input
                  type="date"
                  v-model="form.expected_delivery_date"
                  class="w-full px-3 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-primary focus:border-primary"
                />
              </div>
            </div>

            <!-- Estimated Cost -->
            <div v-if="selectedBOM && form.qty" class="mt-4 pt-4 border-t border-gray-200">
              <div class="flex justify-between items-center">
                <span class="text-gray-600">Chi phí nguyên liệu ước tính:</span>
                <span class="text-xl font-bold text-primary">
                  {{ formatNumber(selectedBOM.total_cost * form.qty) }} VND
                </span>
              </div>
            </div>
          </div>

          <!-- Warehouse Settings -->
          <div class="bg-white rounded-lg shadow p-6">
            <h2 class="text-lg font-semibold text-gray-900 mb-4">Thiết lập kho <span class="text-red-500">*</span></h2>
            
            <div class="grid grid-cols-1 md:grid-cols-3 gap-4">
              <!-- Source Warehouse -->
              <div>
                <label class="block text-sm font-medium text-gray-700 mb-1">
                  Kho nguyên liệu <span class="text-red-500">*</span>
                </label>
                <select
                  v-model="form.source_warehouse"
                  required
                  class="w-full px-3 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-primary focus:border-primary"
                >
                  <option v-for="wh in warehouses" :key="wh.name" :value="wh.name">
                    {{ wh.warehouse_name }}
                  </option>
                </select>
                <p class="text-xs text-gray-500 mt-1">Nơi lấy nguyên vật liệu</p>
              </div>

              <!-- WIP Warehouse -->
              <div>
                <label class="block text-sm font-medium text-gray-700 mb-1">
                  Kho sản xuất (WIP) <span class="text-red-500">*</span>
                </label>
                <select
                  v-model="form.wip_warehouse"
                  required
                  class="w-full px-3 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-primary focus:border-primary"
                >
                  <option v-for="wh in warehouses" :key="wh.name" :value="wh.name">
                    {{ wh.warehouse_name }}
                  </option>
                </select>
                <p class="text-xs text-gray-500 mt-1">Kho dở dang khi đang SX</p>
              </div>

              <!-- FG Warehouse -->
              <div>
                <label class="block text-sm font-medium text-gray-700 mb-1">
                  Kho thành phẩm <span class="text-red-500">*</span>
                </label>
                <select
                  v-model="form.fg_warehouse"
                  required
                  class="w-full px-3 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-primary focus:border-primary"
                >
                  <option v-for="wh in warehouses" :key="wh.name" :value="wh.name">
                    {{ wh.warehouse_name }}
                  </option>
                </select>
                <p class="text-xs text-gray-500 mt-1">Nơi nhập thành phẩm</p>
              </div>
            </div>
          </div>

          <!-- Actions -->
          <div class="flex justify-end gap-3">
            <router-link
              to="/production/orders"
              class="px-4 py-2 text-gray-700 bg-gray-100 rounded-lg hover:bg-gray-200 transition-colors"
            >
              Hủy
            </router-link>
            <button
              type="submit"
              :disabled="loading || !canSubmit"
              class="px-6 py-2 text-white bg-primary rounded-lg hover:bg-primary-dark transition-colors disabled:opacity-50 disabled:cursor-not-allowed flex items-center gap-2"
            >
              <svg v-if="loading" class="animate-spin h-4 w-4" xmlns="http://www.w3.org/2000/svg" fill="none" viewBox="0 0 24 24">
                <circle class="opacity-25" cx="12" cy="12" r="10" stroke="currentColor" stroke-width="4"></circle>
                <path class="opacity-75" fill="currentColor" d="M4 12a8 8 0 018-8V0C5.373 0 0 5.373 0 12h4zm2 5.291A7.962 7.962 0 014 12H0c0 3.042 1.135 5.824 3 7.938l3-2.647z"></path>
              </svg>
              {{ loading ? 'Đang tạo...' : 'Tạo lệnh sản xuất' }}
            </button>
          </div>
        </form>
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
import { ref, reactive, computed, onMounted } from 'vue'
import { useRouter } from 'vue-router'
import { workOrderAPI, stockAPI } from '@/api'

const router = useRouter()

// UOM Translation
const UOM_TRANSLATIONS = {
  'Nos': 'Cái', 'nos': 'Cái', 'Unit': 'Cái',
  'Kg': 'Kg', 'kg': 'Kg',
  'Meter': 'Mét', 'm': 'Mét',
  'Set': 'Bộ', 'Box': 'Hộp', 'Roll': 'Cuộn',
  'Liter': 'Lít', 'L': 'Lít'
}
const translateUOM = (uom) => UOM_TRANSLATIONS[uom] || uom || ''

// State
const loading = ref(false)
const loadingBOMs = ref(false)
const products = ref([])
const productBOMs = ref([])
const bomItems = ref([])
const warehouses = ref([])
const selectedBOM = ref(null)
const selectedProduct = ref(null)

// Product search autocomplete
const productSearch = ref('')
const showProductDropdown = ref(false)

const form = reactive({
  item: '',
  bom_no: '',
  qty: 1,
  planned_start_date: new Date().toISOString().split('T')[0],
  expected_delivery_date: '',
  source_warehouse: '',
  wip_warehouse: '',
  fg_warehouse: ''
})

// Toast
const toast = reactive({ show: false, type: 'success', message: '' })

// Computed
const canSubmit = computed(() => {
  return form.item && form.bom_no && form.qty > 0 && form.source_warehouse && form.wip_warehouse && form.fg_warehouse
})

// Filtered products for autocomplete
const filteredProducts = computed(() => {
  if (!productSearch.value) return products.value.slice(0, 20) // Show first 20 when empty
  
  const search = productSearch.value.toLowerCase()
  return products.value.filter(p => 
    p.item_code.toLowerCase().includes(search) || 
    (p.item_name && p.item_name.toLowerCase().includes(search))
  ).slice(0, 20) // Limit to 20 results
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
  setTimeout(() => { toast.show = false }, 3000)
}

const loadProducts = async () => {
  try {
    // Lấy danh sách sản phẩm (thành phẩm có thể sản xuất)
    const res = await stockAPI.getItems()
    // Lọc sản phẩm có thể sản xuất (có BOM hoặc là thành phẩm)
    products.value = res || []
  } catch (error) {
    console.error('Error loading products:', error)
    showToast('error', 'Không thể tải danh sách sản phẩm')
  }
}

// Product autocomplete handlers
const onProductSearch = () => {
  showProductDropdown.value = true
}

const hideProductDropdown = () => {
  // Delay để cho phép click vào item
  setTimeout(() => {
    showProductDropdown.value = false
  }, 200)
}

const selectProduct = async (product) => {
  form.item = product.item_code
  selectedProduct.value = product
  productSearch.value = `${product.item_code} - ${product.item_name}`
  showProductDropdown.value = false
  
  // Load BOMs for selected product
  await onProductChange()
}

const clearProduct = () => {
  form.item = ''
  selectedProduct.value = null
  productSearch.value = ''
  form.bom_no = ''
  selectedBOM.value = null
  bomItems.value = []
  productBOMs.value = []
}

const onProductChange = async () => {
  // Reset BOM selection
  form.bom_no = ''
  selectedBOM.value = null
  bomItems.value = []
  productBOMs.value = []
  
  if (!form.item) return
  
  loadingBOMs.value = true
  try {
    // Lấy danh sách BOM cho sản phẩm đã chọn
    const boms = await workOrderAPI.getBOMs(form.item)
    productBOMs.value = boms || []
    
    // Tự động chọn BOM mặc định nếu có
    const defaultBOM = productBOMs.value.find(b => b.is_default)
    if (defaultBOM) {
      form.bom_no = defaultBOM.name
      await onBOMChange()
    }
  } catch (error) {
    console.error('Error loading BOMs:', error)
    productBOMs.value = []
  } finally {
    loadingBOMs.value = false
  }
}

const loadWarehouses = async () => {
  try {
    warehouses.value = await stockAPI.getWarehouses()
    
    // Set default values based on warehouse names
    if (warehouses.value.length > 0) {
      // Find warehouses by name pattern
      const sourceWh = warehouses.value.find(wh => 
        wh.warehouse_name.toLowerCase().includes('chính') || 
        wh.warehouse_name.toLowerCase().includes('nguồn') ||
        wh.warehouse_name.toLowerCase().includes('nguyên liệu')
      )
      const wipWh = warehouses.value.find(wh => 
        wh.warehouse_name.toLowerCase().includes('wip') || 
        wh.warehouse_name.toLowerCase().includes('sản xuất') ||
        wh.warehouse_name.toLowerCase().includes('dở dang')
      )
      const fgWh = warehouses.value.find(wh => 
        wh.warehouse_name.toLowerCase().includes('thành phẩm') || 
        wh.warehouse_name.toLowerCase().includes('finished')
      )
      
      // Set defaults
      form.source_warehouse = sourceWh?.name || warehouses.value[0]?.name || ''
      form.wip_warehouse = wipWh?.name || warehouses.value[0]?.name || ''
      form.fg_warehouse = fgWh?.name || warehouses.value[0]?.name || ''
    }
  } catch (error) {
    console.error('Error loading warehouses:', error)
  }
}

const onBOMChange = async () => {
  if (!form.bom_no) {
    selectedBOM.value = null
    bomItems.value = []
    return
  }
  
  try {
    const detail = await workOrderAPI.getBOMDetail(form.bom_no)
    if (detail.success !== false) {
      selectedBOM.value = {
        ...detail,
        item_count: detail.items?.length || 0
      }
      bomItems.value = detail.items || []
    }
  } catch (error) {
    console.error('Error loading BOM detail:', error)
  }
}

const submitForm = async () => {
  if (!canSubmit.value) return
  
  loading.value = true
  try {
    const result = await workOrderAPI.create({
      bom_no: form.bom_no,
      qty: form.qty,
      planned_start_date: form.planned_start_date || null,
      expected_delivery_date: form.expected_delivery_date || null,
      source_warehouse: form.source_warehouse || null,
      wip_warehouse: form.wip_warehouse || null,
      fg_warehouse: form.fg_warehouse || null
    })
    
    if (result.success) {
      showToast('success', result.message)
      setTimeout(() => {
        router.push(`/production/orders/${result.name}`)
      }, 1000)
    } else {
      showToast('error', result.message || 'Không thể tạo lệnh sản xuất')
    }
  } catch (error) {
    console.error('Error creating work order:', error)
    showToast('error', error.response?.data?.message || 'Không thể tạo lệnh sản xuất')
  } finally {
    loading.value = false
  }
}

// Initialize
onMounted(() => {
  loadProducts()
  loadWarehouses()
})
</script>

<style scoped>
.bg-primary { background-color: #055568; }
.bg-primary-dark { background-color: #044454; }
.text-primary { color: #055568; }
.bg-primary\/10 { background-color: rgba(5, 85, 104, 0.1); }
.bg-warning\/10 { background-color: rgba(255, 152, 0, 0.1); }
.text-warning { color: #FF9800; }
.hover\:bg-primary-dark:hover { background-color: #044454; }
.focus\:ring-primary:focus { --tw-ring-color: #055568; }
.focus\:border-primary:focus { border-color: #055568; }
</style>
