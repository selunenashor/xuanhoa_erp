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
              <p class="text-gray-600">Tạo lệnh sản xuất mới từ BOM</p>
            </div>
          </div>
        </div>

        <!-- Form -->
        <form @submit.prevent="submitForm" class="space-y-6">
          <!-- BOM Selection -->
          <div class="bg-white rounded-lg shadow p-6">
            <h2 class="text-lg font-semibold text-gray-900 mb-4">Chọn sản phẩm</h2>
            
            <!-- BOM Selector -->
            <div class="mb-4">
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
                <option v-for="bom in boms" :key="bom.name" :value="bom.name">
                  {{ bom.item }} - {{ bom.item_name }} ({{ bom.name }})
                  <template v-if="bom.is_default"> ⭐</template>
                </option>
              </select>
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
                  <div class="text-sm text-gray-500">Chi phí/đơn vị</div>
                  <div class="font-semibold text-gray-900">{{ formatNumber(selectedBOM.total_cost) }} VND</div>
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
const boms = ref([])
const bomItems = ref([])
const warehouses = ref([])
const selectedBOM = ref(null)

const form = reactive({
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
  return form.bom_no && form.qty > 0 && form.source_warehouse && form.wip_warehouse && form.fg_warehouse
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

const loadBOMs = async () => {
  try {
    boms.value = await workOrderAPI.getBOMs()
  } catch (error) {
    console.error('Error loading BOMs:', error)
    showToast('error', 'Không thể tải danh sách BOM')
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
  loadBOMs()
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
