<template>
  <div class="min-h-screen bg-gray-100">
    <!-- Header -->
    <header class="bg-xh-red text-white shadow-lg">
      <div class="container mx-auto px-4 py-4 flex items-center">
        <router-link to="/" class="mr-4">
          <svg class="w-6 h-6" fill="none" stroke="currentColor" viewBox="0 0 24 24">
            <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M15 19l-7-7 7-7" />
          </svg>
        </router-link>
        <h1 class="text-xl font-bold">Xuất kho</h1>
      </div>
    </header>

    <!-- Main Content -->
    <main class="container mx-auto px-4 py-6">
      <div class="bg-white rounded-lg shadow p-6">
        <form @submit.prevent="handleSubmit" class="space-y-6">
          <!-- Item Search -->
          <div>
            <label class="block text-sm font-medium text-gray-700 mb-2">Mã hàng hóa *</label>
            <input
              v-model="form.item_code"
              type="text"
              required
              @input="searchItems"
              class="w-full px-4 py-3 border border-gray-300 rounded-lg focus:outline-none focus:ring-2 focus:ring-xh-red"
              placeholder="Nhập mã hoặc tên hàng..."
            />
            <!-- Search Results -->
            <div v-if="searchResults.length > 0" class="mt-2 border rounded-lg divide-y">
              <div
                v-for="item in searchResults"
                :key="item.item_code"
                @click="selectItem(item)"
                class="px-4 py-3 hover:bg-gray-50 cursor-pointer"
              >
                <div class="font-medium">{{ item.item_code }}</div>
                <div class="text-sm text-gray-500">{{ item.item_name }}</div>
              </div>
            </div>
          </div>

          <!-- Selected Item Info with Stock -->
          <div v-if="selectedItem" class="bg-gray-50 rounded-lg p-4">
            <div class="text-sm text-gray-500">Đã chọn:</div>
            <div class="font-medium">{{ selectedItem.item_code }} - {{ selectedItem.item_name }}</div>
            <div class="text-sm text-gray-500">Đơn vị: {{ selectedItem.stock_uom }}</div>
            <div v-if="stockInfo" class="mt-2 pt-2 border-t">
              <div class="text-sm font-medium text-green-600">Tồn kho: {{ stockInfo.total_qty }} {{ selectedItem.stock_uom }}</div>
            </div>
          </div>

          <!-- Quantity -->
          <div>
            <label class="block text-sm font-medium text-gray-700 mb-2">Số lượng xuất *</label>
            <input
              v-model.number="form.qty"
              type="number"
              min="0.01"
              step="0.01"
              required
              class="w-full px-4 py-3 border border-gray-300 rounded-lg focus:outline-none focus:ring-2 focus:ring-xh-red"
              placeholder="Nhập số lượng"
            />
          </div>

          <!-- Warehouse -->
          <div>
            <label class="block text-sm font-medium text-gray-700 mb-2">Kho xuất *</label>
            <select
              v-model="form.warehouse"
              required
              class="w-full px-4 py-3 border border-gray-300 rounded-lg focus:outline-none focus:ring-2 focus:ring-xh-red"
            >
              <option value="">-- Chọn kho --</option>
              <option v-for="wh in warehouses" :key="wh.name" :value="wh.name">
                {{ wh.warehouse_name || wh.name }}
              </option>
            </select>
          </div>

          <!-- Error Message -->
          <div v-if="error" class="bg-red-50 border border-red-200 text-red-600 px-4 py-3 rounded-lg">
            {{ error }}
          </div>

          <!-- Success Message -->
          <div v-if="success" class="bg-green-50 border border-green-200 text-green-600 px-4 py-3 rounded-lg">
            {{ success }}
          </div>

          <!-- Submit Button -->
          <button
            type="submit"
            :disabled="loading || !selectedItem"
            class="w-full bg-xh-red text-white py-4 rounded-lg font-medium text-lg hover:bg-red-700 transition disabled:opacity-50"
          >
            <span v-if="loading">Đang xử lý...</span>
            <span v-else>Xuất kho</span>
          </button>
        </form>
      </div>
    </main>
  </div>
</template>

<script setup>
import { ref, reactive, onMounted, watch } from 'vue'
import { xuanhoaAPI } from '@/api/client'

const form = reactive({
  item_code: '',
  qty: null,
  warehouse: ''
})

const loading = ref(false)
const error = ref('')
const success = ref('')
const searchResults = ref([])
const selectedItem = ref(null)
const stockInfo = ref(null)
const warehouses = ref([])

// Load warehouses on mount
onMounted(async () => {
  try {
    warehouses.value = await xuanhoaAPI.getWarehouses(0)
  } catch (e) {
    console.error('Error loading warehouses:', e)
  }
})

// Watch selected item to get stock info
watch(selectedItem, async (item) => {
  if (item) {
    try {
      stockInfo.value = await xuanhoaAPI.getItemStock(item.item_code)
    } catch (e) {
      console.error('Error getting stock:', e)
    }
  } else {
    stockInfo.value = null
  }
})

// Search items
let searchTimeout = null
const searchItems = () => {
  selectedItem.value = null
  clearTimeout(searchTimeout)
  
  if (form.item_code.length < 2) {
    searchResults.value = []
    return
  }
  
  searchTimeout = setTimeout(async () => {
    try {
      searchResults.value = await xuanhoaAPI.searchItems(form.item_code)
    } catch (e) {
      console.error('Search error:', e)
    }
  }, 300)
}

// Select item
const selectItem = (item) => {
  selectedItem.value = item
  form.item_code = item.item_code
  searchResults.value = []
}

// Submit form
const handleSubmit = async () => {
  error.value = ''
  success.value = ''
  loading.value = true
  
  try {
    const result = await xuanhoaAPI.createMaterialIssue(
      form.item_code,
      form.qty,
      form.warehouse
    )
    
    if (result.success) {
      success.value = result.message
      form.item_code = ''
      form.qty = null
      selectedItem.value = null
    } else {
      error.value = result.message
    }
  } catch (e) {
    error.value = e.message || 'Có lỗi xảy ra'
  } finally {
    loading.value = false
  }
}
</script>
