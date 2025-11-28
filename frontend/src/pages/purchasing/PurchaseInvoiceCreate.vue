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
        <h1 class="text-2xl font-bold text-gray-900">Tạo hóa đơn mua hàng</h1>
        <p class="text-gray-600">Nhập thông tin hóa đơn từ nhà cung cấp</p>
      </div>
    </div>

    <!-- Form -->
    <form @submit.prevent="handleSubmit" class="space-y-6">
      <!-- Basic Info -->
      <div class="bg-white rounded-lg shadow p-6">
        <h2 class="text-lg font-semibold text-gray-900 mb-4">Thông tin cơ bản</h2>
        
        <div class="grid grid-cols-1 md:grid-cols-2 gap-6">
          <!-- Supplier -->
          <div>
            <label class="block text-sm font-medium text-gray-700 mb-1">
              Nhà cung cấp <span class="text-error">*</span>
            </label>
            <div class="relative">
              <input
                type="text"
                v-model="supplierSearch"
                @input="searchSuppliers"
                @focus="showSupplierDropdown = true"
                :placeholder="form.supplier ? form.supplier_name : 'Tìm nhà cung cấp...'"
                class="w-full px-4 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-primary focus:border-primary"
              />
              <!-- Dropdown -->
              <div
                v-if="showSupplierDropdown && suppliers.length > 0"
                class="absolute z-10 w-full mt-1 bg-white border border-gray-200 rounded-lg shadow-lg max-h-60 overflow-auto"
              >
                <button
                  v-for="supplier in suppliers"
                  :key="supplier.name"
                  type="button"
                  @click="selectSupplier(supplier)"
                  class="w-full px-4 py-2 text-left hover:bg-gray-50 border-b border-gray-100 last:border-b-0"
                >
                  <div class="font-medium text-gray-900">{{ supplier.supplier_name }}</div>
                  <div class="text-xs text-gray-500">{{ supplier.name }}</div>
                </button>
              </div>
            </div>
            <p v-if="form.supplier" class="mt-1 text-sm text-gray-500">
              Đã chọn: {{ form.supplier_name }} ({{ form.supplier }})
            </p>
          </div>

          <!-- Warehouse -->
          <div>
            <label class="block text-sm font-medium text-gray-700 mb-1">
              Kho nhập mặc định
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

        <!-- Items Table -->
        <div class="overflow-x-auto">
          <table class="min-w-full divide-y divide-gray-200">
            <thead class="bg-gray-50">
              <tr>
                <th class="px-4 py-3 text-left text-xs font-medium text-gray-500 uppercase w-16">#</th>
                <th class="px-4 py-3 text-left text-xs font-medium text-gray-500 uppercase">Sản phẩm</th>
                <th class="px-4 py-3 text-left text-xs font-medium text-gray-500 uppercase w-32">Số lượng</th>
                <th class="px-4 py-3 text-left text-xs font-medium text-gray-500 uppercase w-40">Đơn giá</th>
                <th class="px-4 py-3 text-left text-xs font-medium text-gray-500 uppercase w-40">Thành tiền</th>
                <th class="px-4 py-3 text-left text-xs font-medium text-gray-500 uppercase w-48">Kho</th>
                <th class="px-4 py-3 w-16"></th>
              </tr>
            </thead>
            <tbody class="bg-white divide-y divide-gray-200">
              <tr v-for="(item, index) in form.items" :key="index">
                <td class="px-4 py-3 text-sm text-gray-500">{{ index + 1 }}</td>
                <td class="px-4 py-3">
                  <div class="relative">
                    <input
                      type="text"
                      v-model="item.search"
                      @input="searchItems(index)"
                      @focus="item.showDropdown = true"
                      :placeholder="item.item_code ? item.item_name : 'Tìm sản phẩm...'"
                      class="w-full px-3 py-1.5 text-sm border border-gray-300 rounded-lg focus:ring-2 focus:ring-primary focus:border-primary"
                    />
                    <!-- Item Dropdown -->
                    <div
                      v-if="item.showDropdown && item.suggestions?.length > 0"
                      class="absolute z-10 w-full mt-1 bg-white border border-gray-200 rounded-lg shadow-lg max-h-48 overflow-auto"
                    >
                      <button
                        v-for="suggestion in item.suggestions"
                        :key="suggestion.item_code"
                        type="button"
                        @click="selectItem(index, suggestion)"
                        class="w-full px-3 py-2 text-left hover:bg-gray-50 border-b border-gray-100 last:border-b-0"
                      >
                        <div class="font-medium text-gray-900 text-sm">{{ suggestion.item_name }}</div>
                        <div class="text-xs text-gray-500">{{ suggestion.item_code }} | Tồn: {{ suggestion.actual_qty }} {{ suggestion.stock_uom }}</div>
                      </button>
                    </div>
                  </div>
                  <p v-if="item.item_code" class="mt-1 text-xs text-gray-500">{{ item.item_code }}</p>
                </td>
                <td class="px-4 py-3">
                  <input
                    type="number"
                    v-model.number="item.qty"
                    min="0"
                    step="0.01"
                    class="w-full px-3 py-1.5 text-sm border border-gray-300 rounded-lg focus:ring-2 focus:ring-primary focus:border-primary"
                  />
                </td>
                <td class="px-4 py-3">
                  <input
                    type="number"
                    v-model.number="item.rate"
                    min="0"
                    step="0.01"
                    class="w-full px-3 py-1.5 text-sm border border-gray-300 rounded-lg focus:ring-2 focus:ring-primary focus:border-primary"
                  />
                </td>
                <td class="px-4 py-3 text-sm font-medium text-gray-900">
                  {{ formatCurrency(item.qty * item.rate) }}
                </td>
                <td class="px-4 py-3">
                  <select
                    v-model="item.warehouse"
                    class="w-full px-3 py-1.5 text-sm border border-gray-300 rounded-lg focus:ring-2 focus:ring-primary focus:border-primary"
                  >
                    <option value="">-- Mặc định --</option>
                    <option v-for="wh in warehouses" :key="wh.name" :value="wh.name">
                      {{ wh.warehouse_name }}
                    </option>
                  </select>
                </td>
                <td class="px-4 py-3">
                  <button
                    type="button"
                    @click="removeItem(index)"
                    class="p-1.5 text-gray-400 hover:text-error hover:bg-red-50 rounded-lg transition-colors"
                  >
                    <svg xmlns="http://www.w3.org/2000/svg" class="h-5 w-5" fill="none" viewBox="0 0 24 24" stroke="currentColor">
                      <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M19 7l-.867 12.142A2 2 0 0116.138 21H7.862a2 2 0 01-1.995-1.858L5 7m5 4v6m4-6v6m1-10V4a1 1 0 00-1-1h-4a1 1 0 00-1 1v3M4 7h16" />
                    </svg>
                  </button>
                </td>
              </tr>
              <tr v-if="form.items.length === 0">
                <td colspan="7" class="px-4 py-8 text-center text-gray-500">
                  Chưa có sản phẩm nào. Nhấn "Thêm sản phẩm" để bắt đầu.
                </td>
              </tr>
            </tbody>
            <tfoot class="bg-gray-50">
              <tr>
                <td colspan="4" class="px-4 py-3 text-right font-medium text-gray-700">Tổng cộng:</td>
                <td class="px-4 py-3 font-bold text-gray-900">{{ formatCurrency(totalAmount) }}</td>
                <td colspan="2"></td>
              </tr>
            </tfoot>
          </table>
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

    <!-- Error Alert -->
    <div v-if="error" class="fixed bottom-4 right-4 max-w-md bg-red-50 border border-red-200 rounded-lg p-4 shadow-lg">
      <div class="flex items-start gap-3">
        <svg xmlns="http://www.w3.org/2000/svg" class="h-5 w-5 text-error flex-shrink-0 mt-0.5" fill="none" viewBox="0 0 24 24" stroke="currentColor">
          <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M12 8v4m0 4h.01M21 12a9 9 0 11-18 0 9 9 0 0118 0z" />
        </svg>
        <div class="flex-1">
          <p class="text-sm text-error">{{ error }}</p>
        </div>
        <button @click="error = ''" class="text-gray-400 hover:text-gray-600">
          <svg xmlns="http://www.w3.org/2000/svg" class="h-5 w-5" fill="none" viewBox="0 0 24 24" stroke="currentColor">
            <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M6 18L18 6M6 6l12 12" />
          </svg>
        </button>
      </div>
    </div>
  </div>
</template>

<script setup>
import { ref, reactive, computed, onMounted, watch } from 'vue'
import { useRouter } from 'vue-router'
import { purchaseInvoiceAPI, supplierAPI, stockAPI } from '@/api'

const router = useRouter()

// State
const submitting = ref(false)
const error = ref('')
const suppliers = ref([])
const warehouses = ref([])
const supplierSearch = ref('')
const showSupplierDropdown = ref(false)

// Form
const form = reactive({
  supplier: '',
  supplier_name: '',
  posting_date: new Date().toISOString().split('T')[0],
  due_date: '',
  set_warehouse: '',
  remarks: '',
  items: []
})

// Computed
const totalAmount = computed(() => {
  return form.items.reduce((sum, item) => sum + (item.qty || 0) * (item.rate || 0), 0)
})

const isValid = computed(() => {
  return form.supplier && 
         form.posting_date && 
         form.items.length > 0 && 
         form.items.every(item => item.item_code && item.qty > 0 && item.rate >= 0)
})

// Methods
const formatCurrency = (amount) => {
  if (!amount) return '0 ₫'
  return new Intl.NumberFormat('vi-VN', { style: 'currency', currency: 'VND' }).format(amount)
}

let supplierTimeout = null
const searchSuppliers = () => {
  if (supplierTimeout) clearTimeout(supplierTimeout)
  supplierTimeout = setTimeout(async () => {
    try {
      suppliers.value = await supplierAPI.getList(supplierSearch.value, 10)
      showSupplierDropdown.value = true
    } catch (e) {
      console.error('Error searching suppliers:', e)
    }
  }, 300)
}

const selectSupplier = (supplier) => {
  form.supplier = supplier.name
  form.supplier_name = supplier.supplier_name
  supplierSearch.value = ''
  showSupplierDropdown.value = false
}

let itemTimeout = null
const searchItems = (index) => {
  const item = form.items[index]
  if (itemTimeout) clearTimeout(itemTimeout)
  itemTimeout = setTimeout(async () => {
    try {
      // Sử dụng kho của item nếu có, nếu không thì dùng kho mặc định của form
      const warehouse = item.warehouse || form.set_warehouse || null
      const results = await stockAPI.searchItems(item.search, null, warehouse)
      item.suggestions = results
      item.showDropdown = true
    } catch (e) {
      console.error('Error searching items:', e)
    }
  }, 300)
}

const selectItem = (index, suggestion) => {
  const item = form.items[index]
  item.item_code = suggestion.item_code
  item.item_name = suggestion.item_name
  item.uom = suggestion.stock_uom
  item.rate = suggestion.rate || suggestion.valuation_rate || suggestion.standard_rate || 0
  item.search = ''
  item.showDropdown = false
  item.suggestions = []
}

const addItem = () => {
  form.items.push({
    item_code: '',
    item_name: '',
    qty: 1,
    rate: 0,
    uom: '',
    warehouse: '',
    search: '',
    showDropdown: false,
    suggestions: []
  })
}

const removeItem = (index) => {
  form.items.splice(index, 1)
}

const loadWarehouses = async () => {
  try {
    warehouses.value = await stockAPI.getWarehouses()
  } catch (e) {
    console.error('Error loading warehouses:', e)
  }
}

const handleSubmit = async () => {
  if (!isValid.value) return
  
  submitting.value = true
  error.value = ''
  
  try {
    const items = form.items.map(item => ({
      item_code: item.item_code,
      qty: item.qty,
      rate: item.rate,
      warehouse: item.warehouse || form.set_warehouse
    }))
    
    const result = await purchaseInvoiceAPI.create({
      supplier: form.supplier,
      items,
      posting_date: form.posting_date,
      due_date: form.due_date,
      set_warehouse: form.set_warehouse,
      remarks: form.remarks
    })
    
    if (result.success) {
      router.push(`/purchasing/invoices/${result.name}`)
    } else {
      error.value = result.message || 'Có lỗi xảy ra'
    }
  } catch (e) {
    console.error('Error creating invoice:', e)
    error.value = e.response?.data?.message || 'Có lỗi xảy ra khi tạo hóa đơn'
  } finally {
    submitting.value = false
  }
}

// Click outside to close dropdowns
const handleClickOutside = (e) => {
  if (!e.target.closest('.relative')) {
    showSupplierDropdown.value = false
    form.items.forEach(item => {
      item.showDropdown = false
    })
  }
}

// Watch for warehouse change to update items
watch(() => form.set_warehouse, (newWarehouse) => {
  // Cập nhật kho cho các items chưa có kho riêng
  form.items.forEach(item => {
    if (!item.warehouse) {
      // Item sẽ sử dụng kho mặc định mới
    }
  })
})

// Initialize
onMounted(() => {
  loadWarehouses()
  document.addEventListener('click', handleClickOutside)
})
</script>
