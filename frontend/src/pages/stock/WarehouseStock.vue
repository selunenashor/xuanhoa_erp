<template>
  <div class="space-y-6">
    <!-- Header -->
    <div class="flex flex-col sm:flex-row sm:items-center sm:justify-between gap-4">
      <div>
        <h1 class="text-2xl font-bold text-gray-900">Quản lý kho hàng</h1>
        <p class="text-gray-600">Theo dõi hàng hóa và tồn kho tại các kho</p>
      </div>
      <div class="flex gap-2">
        <button
          @click="exportStock"
          class="inline-flex items-center gap-2 px-4 py-2 border border-gray-300 rounded-lg hover:bg-gray-50 transition-colors"
        >
          <svg xmlns="http://www.w3.org/2000/svg" class="h-5 w-5" fill="none" viewBox="0 0 24 24" stroke="currentColor">
            <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M12 10v6m0 0l-3-3m3 3l3-3m2 8H7a2 2 0 01-2-2V5a2 2 0 012-2h5.586a1 1 0 01.707.293l5.414 5.414a1 1 0 01.293.707V19a2 2 0 01-2 2z" />
          </svg>
          Xuất Excel
        </button>
        <button
          @click="loadData"
          class="inline-flex items-center gap-2 px-4 py-2 border border-gray-300 rounded-lg hover:bg-gray-50 transition-colors"
        >
          <svg xmlns="http://www.w3.org/2000/svg" class="h-5 w-5" fill="none" viewBox="0 0 24 24" stroke="currentColor">
            <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M4 4v5h.582m15.356 2A8.001 8.001 0 004.582 9m0 0H9m11 11v-5h-.581m0 0a8.003 8.003 0 01-15.357-2m15.357 2H15" />
          </svg>
          Làm mới
        </button>
      </div>
    </div>

    <!-- Summary Cards -->
    <div class="grid grid-cols-1 md:grid-cols-3 gap-4">
      <div class="bg-white rounded-lg shadow p-4">
        <div class="flex items-center gap-3">
          <div class="w-12 h-12 bg-blue-100 rounded-lg flex items-center justify-center">
            <svg xmlns="http://www.w3.org/2000/svg" class="h-6 w-6 text-blue-600" fill="none" viewBox="0 0 24 24" stroke="currentColor">
              <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M19 21V5a2 2 0 00-2-2H7a2 2 0 00-2 2v16m14 0h2m-2 0h-5m-9 0H3m2 0h5M9 7h1m-1 4h1m4-4h1m-1 4h1m-5 10v-5a1 1 0 011-1h2a1 1 0 011 1v5m-4 0h4" />
            </svg>
          </div>
          <div>
            <div class="text-sm text-gray-500">Tổng số kho</div>
            <div class="text-2xl font-bold text-gray-900">{{ warehouses.length }}</div>
          </div>
        </div>
      </div>

      <div class="bg-white rounded-lg shadow p-4">
        <div class="flex items-center gap-3">
          <div class="w-12 h-12 bg-green-100 rounded-lg flex items-center justify-center">
            <svg xmlns="http://www.w3.org/2000/svg" class="h-6 w-6 text-green-600" fill="none" viewBox="0 0 24 24" stroke="currentColor">
              <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M20 7l-8-4-8 4m16 0l-8 4m8-4v10l-8 4m0-10L4 7m8 4v10M4 7v10l8 4" />
            </svg>
          </div>
          <div>
            <div class="text-sm text-gray-500">Tổng SP tồn kho</div>
            <div class="text-2xl font-bold text-gray-900">{{ formatNumber(summary.totalItems) }}</div>
          </div>
        </div>
      </div>

      <div class="bg-white rounded-lg shadow p-4">
        <div class="flex items-center gap-3">
          <div class="w-12 h-12 bg-purple-100 rounded-lg flex items-center justify-center">
            <svg xmlns="http://www.w3.org/2000/svg" class="h-6 w-6 text-purple-600" fill="none" viewBox="0 0 24 24" stroke="currentColor">
              <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M12 8c-1.657 0-3 .895-3 2s1.343 2 3 2 3 .895 3 2-1.343 2-3 2m0-8c1.11 0 2.08.402 2.599 1M12 8V7m0 1v8m0 0v1m0-1c-1.11 0-2.08-.402-2.599-1M21 12a9 9 0 11-18 0 9 9 0 0118 0z" />
            </svg>
          </div>
          <div>
            <div class="text-sm text-gray-500">Tổng giá trị</div>
            <div class="text-2xl font-bold text-gray-900">{{ formatCurrency(summary.totalValue) }}</div>
          </div>
        </div>
      </div>
    </div>

    <!-- View Mode Tabs -->
    <div class="bg-white rounded-lg shadow">
      <div class="border-b">
        <nav class="flex -mb-px">
          <button
            @click="viewMode = 'warehouse'"
            :class="[
              'px-6 py-3 text-sm font-medium border-b-2 transition-colors',
              viewMode === 'warehouse'
                ? 'border-primary text-primary'
                : 'border-transparent text-gray-500 hover:text-gray-700 hover:border-gray-300'
            ]"
          >
            Theo kho
          </button>
          <button
            @click="viewMode = 'item'"
            :class="[
              'px-6 py-3 text-sm font-medium border-b-2 transition-colors',
              viewMode === 'item'
                ? 'border-primary text-primary'
                : 'border-transparent text-gray-500 hover:text-gray-700 hover:border-gray-300'
            ]"
          >
            Theo sản phẩm
          </button>
          <button
            @click="viewMode = 'ledger'"
            :class="[
              'px-6 py-3 text-sm font-medium border-b-2 transition-colors',
              viewMode === 'ledger'
                ? 'border-primary text-primary'
                : 'border-transparent text-gray-500 hover:text-gray-700 hover:border-gray-300'
            ]"
          >
            Lịch sử xuất nhập
          </button>
        </nav>
      </div>

      <!-- Filters -->
      <div class="p-4 border-b bg-gray-50">
        <div class="grid grid-cols-1 md:grid-cols-4 gap-4">
          <!-- Search -->
          <div>
            <label class="block text-sm font-medium text-gray-700 mb-1">Tìm kiếm</label>
            <div class="relative">
              <input
                type="text"
                v-model="filters.search"
                @input="debouncedSearch"
                placeholder="Tìm sản phẩm..."
                class="w-full pl-10 pr-4 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-primary focus:border-primary"
              />
              <svg xmlns="http://www.w3.org/2000/svg" class="h-5 w-5 text-gray-400 absolute left-3 top-1/2 -translate-y-1/2" fill="none" viewBox="0 0 24 24" stroke="currentColor">
                <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M21 21l-6-6m2-5a7 7 0 11-14 0 7 7 0 0114 0z" />
              </svg>
            </div>
          </div>

          <!-- Warehouse Filter -->
          <div>
            <label class="block text-sm font-medium text-gray-700 mb-1">Kho</label>
            <select
              v-model="filters.warehouse"
              @change="onFilterChange"
              class="w-full px-3 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-primary focus:border-primary"
            >
              <option value="">Tất cả kho</option>
              <option v-for="wh in warehouses" :key="wh.name" :value="wh.name">
                {{ wh.warehouse_name }}
              </option>
            </select>
          </div>

          <!-- Item Group Filter -->
          <div>
            <label class="block text-sm font-medium text-gray-700 mb-1">Nhóm hàng</label>
            <select
              v-model="filters.item_group"
              @change="onFilterChange"
              class="w-full px-3 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-primary focus:border-primary"
            >
              <option value="">Tất cả nhóm</option>
              <option value="Nguyên vật liệu">Nguyên vật liệu</option>
              <option value="Bán thành phẩm">Bán thành phẩm</option>
              <option value="Thành phẩm">Thành phẩm</option>
            </select>
          </div>

          <!-- Date Range (for ledger) -->
          <div v-if="viewMode === 'ledger'">
            <label class="block text-sm font-medium text-gray-700 mb-1">Từ ngày</label>
            <input
              type="date"
              v-model="filters.from_date"
              @change="onFilterChange"
              class="w-full px-3 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-primary focus:border-primary"
            />
          </div>
        </div>
      </div>

      <!-- Loading -->
      <div v-if="loading" class="flex justify-center py-12">
        <svg class="animate-spin h-8 w-8 text-primary" xmlns="http://www.w3.org/2000/svg" fill="none" viewBox="0 0 24 24">
          <circle class="opacity-25" cx="12" cy="12" r="10" stroke="currentColor" stroke-width="4"></circle>
          <path class="opacity-75" fill="currentColor" d="M4 12a8 8 0 018-8V0C5.373 0 0 5.373 0 12h4zm2 5.291A7.962 7.962 0 014 12H0c0 3.042 1.135 5.824 3 7.938l3-2.647z"></path>
        </svg>
      </div>

      <!-- Warehouse View -->
      <div v-else-if="viewMode === 'warehouse'" class="p-4">
        <div v-if="warehouseStocks.length === 0" class="text-center py-12">
          <svg xmlns="http://www.w3.org/2000/svg" class="h-12 w-12 mx-auto text-gray-400 mb-4" fill="none" viewBox="0 0 24 24" stroke="currentColor">
            <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M20 7l-8-4-8 4m16 0l-8 4m8-4v10l-8 4m0-10L4 7m8 4v10M4 7v10l8 4" />
          </svg>
          <h3 class="text-lg font-medium text-gray-900 mb-1">Chưa có dữ liệu tồn kho</h3>
          <p class="text-gray-500">Nhập kho để bắt đầu theo dõi hàng hóa</p>
        </div>
        
        <div v-else class="space-y-4">
          <div 
            v-for="wh in warehouseStocks" 
            :key="wh.warehouse"
            class="border rounded-lg overflow-hidden"
          >
            <!-- Warehouse Header -->
            <div 
              @click="toggleWarehouse(wh.warehouse)"
              class="flex items-center justify-between p-4 bg-gray-50 cursor-pointer hover:bg-gray-100 transition-colors"
            >
              <div class="flex items-center gap-3">
                <svg 
                  xmlns="http://www.w3.org/2000/svg" 
                  class="h-5 w-5 text-gray-400 transition-transform"
                  :class="{ 'rotate-90': expandedWarehouses.includes(wh.warehouse) }"
                  fill="none" viewBox="0 0 24 24" stroke="currentColor"
                >
                  <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M9 5l7 7-7 7" />
                </svg>
                <div class="w-10 h-10 bg-primary/10 rounded-lg flex items-center justify-center">
                  <svg xmlns="http://www.w3.org/2000/svg" class="h-5 w-5 text-primary" fill="none" viewBox="0 0 24 24" stroke="currentColor">
                    <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M19 21V5a2 2 0 00-2-2H7a2 2 0 00-2 2v16m14 0h2m-2 0h-5m-9 0H3m2 0h5M9 7h1m-1 4h1m4-4h1m-1 4h1m-5 10v-5a1 1 0 011-1h2a1 1 0 011 1v5m-4 0h4" />
                  </svg>
                </div>
                <div>
                  <div class="font-medium text-gray-900">{{ wh.warehouse_name || wh.warehouse }}</div>
                  <div class="text-sm text-gray-500">{{ wh.items?.length || 0 }} sản phẩm</div>
                </div>
              </div>
              <div class="text-right">
                <div class="text-sm text-gray-500">{{ wh.items?.length || 0 }} loại SP</div>
                <div class="font-semibold text-gray-900">{{ formatCurrency(wh.total_value) }}</div>
              </div>
            </div>

            <!-- Warehouse Items -->
            <div v-if="expandedWarehouses.includes(wh.warehouse)" class="border-t">
              <table class="min-w-full divide-y divide-gray-200">
                <thead class="bg-gray-50">
                  <tr>
                    <th class="px-4 py-2 text-left text-xs font-medium text-gray-500">Mã SP</th>
                    <th class="px-4 py-2 text-left text-xs font-medium text-gray-500">Tên sản phẩm</th>
                    <th class="px-4 py-2 text-center text-xs font-medium text-gray-500">Nhóm</th>
                    <th class="px-4 py-2 text-right text-xs font-medium text-gray-500">Số lượng</th>
                    <th class="px-4 py-2 text-center text-xs font-medium text-gray-500">ĐVT</th>
                    <th class="px-4 py-2 text-right text-xs font-medium text-gray-500">Đơn giá</th>
                    <th class="px-4 py-2 text-right text-xs font-medium text-gray-500">Giá trị</th>
                  </tr>
                </thead>
                <tbody class="divide-y divide-gray-200">
                  <tr v-for="item in wh.items" :key="item.item_code" class="hover:bg-gray-50">
                    <td class="px-4 py-2 text-sm font-medium text-primary">{{ item.item_code }}</td>
                    <td class="px-4 py-2 text-sm text-gray-900">{{ item.item_name }}</td>
                    <td class="px-4 py-2 text-sm text-center">
                      <span class="px-2 py-0.5 text-xs rounded-full bg-gray-100 text-gray-600">
                        {{ item.item_group || 'N/A' }}
                      </span>
                    </td>
                    <td class="px-4 py-2 text-sm text-right">
                      {{ formatNumber(item.actual_qty) }}
                    </td>
                    <td class="px-4 py-2 text-sm text-center text-gray-500">{{ formatUOM(item.stock_uom) }}</td>
                    <td class="px-4 py-2 text-sm text-right">{{ formatCurrency(item.valuation_rate) }}</td>
                    <td class="px-4 py-2 text-sm text-right font-medium">{{ formatCurrency(item.stock_value) }}</td>
                  </tr>
                </tbody>
              </table>
            </div>
          </div>
        </div>
      </div>

      <!-- Item View -->
      <div v-else-if="viewMode === 'item'" class="overflow-x-auto">
        <div v-if="itemStocks.length === 0" class="text-center py-12">
          <svg xmlns="http://www.w3.org/2000/svg" class="h-12 w-12 mx-auto text-gray-400 mb-4" fill="none" viewBox="0 0 24 24" stroke="currentColor">
            <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M20 7l-8-4-8 4m16 0l-8 4m8-4v10l-8 4m0-10L4 7m8 4v10M4 7v10l8 4" />
          </svg>
          <h3 class="text-lg font-medium text-gray-900 mb-1">Chưa có dữ liệu tồn kho</h3>
          <p class="text-gray-500">Nhập kho để bắt đầu theo dõi hàng hóa</p>
        </div>
        
        <table v-else class="min-w-full divide-y divide-gray-200">
          <thead class="bg-gray-50">
            <tr>
              <th class="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase">Mã SP</th>
              <th class="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase">Tên sản phẩm</th>
              <th class="px-6 py-3 text-center text-xs font-medium text-gray-500 uppercase">Nhóm</th>
              <th class="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase">Kho</th>
              <th class="px-6 py-3 text-right text-xs font-medium text-gray-500 uppercase">Số lượng</th>
              <th class="px-6 py-3 text-center text-xs font-medium text-gray-500 uppercase">ĐVT</th>
              <th class="px-6 py-3 text-right text-xs font-medium text-gray-500 uppercase">Đơn giá</th>
              <th class="px-6 py-3 text-right text-xs font-medium text-gray-500 uppercase">Giá trị</th>
            </tr>
          </thead>
          <tbody class="divide-y divide-gray-200">
            <tr v-for="item in itemStocks" :key="`${item.item_code}-${item.warehouse}`" class="hover:bg-gray-50">
              <td class="px-6 py-3 text-sm font-medium text-primary">{{ item.item_code }}</td>
              <td class="px-6 py-3 text-sm text-gray-900">{{ item.item_name }}</td>
              <td class="px-6 py-3 text-sm text-center">
                <span class="px-2 py-0.5 text-xs rounded-full bg-gray-100 text-gray-600">
                  {{ item.item_group || 'N/A' }}
                </span>
              </td>
              <td class="px-6 py-3 text-sm text-gray-700">{{ formatWarehouse(item.warehouse) }}</td>
              <td class="px-6 py-3 text-sm text-right">
                <span :class="item.actual_qty < 0 ? 'text-red-600' : ''">
                  {{ formatNumber(item.actual_qty) }}
                </span>
              </td>
              <td class="px-6 py-3 text-sm text-center text-gray-500">{{ formatUOM(item.stock_uom) }}</td>
              <td class="px-6 py-3 text-sm text-right">{{ formatCurrency(item.valuation_rate) }}</td>
              <td class="px-6 py-3 text-sm text-right font-medium">{{ formatCurrency(item.stock_value) }}</td>
            </tr>
          </tbody>
        </table>
      </div>

      <!-- Ledger View -->
      <div v-else-if="viewMode === 'ledger'" class="overflow-x-auto">
        <div v-if="stockLedger.length === 0" class="text-center py-12">
          <svg xmlns="http://www.w3.org/2000/svg" class="h-12 w-12 mx-auto text-gray-400 mb-4" fill="none" viewBox="0 0 24 24" stroke="currentColor">
            <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M9 5H7a2 2 0 00-2 2v12a2 2 0 002 2h10a2 2 0 002-2V7a2 2 0 00-2-2h-2M9 5a2 2 0 002 2h2a2 2 0 002-2M9 5a2 2 0 012-2h2a2 2 0 012 2" />
          </svg>
          <h3 class="text-lg font-medium text-gray-900 mb-1">Chưa có lịch sử xuất nhập</h3>
          <p class="text-gray-500">Các giao dịch kho sẽ hiển thị ở đây</p>
        </div>
        
        <table v-else class="min-w-full divide-y divide-gray-200">
          <thead class="bg-gray-50">
            <tr>
              <th class="px-4 py-3 text-left text-xs font-medium text-gray-500 uppercase">Ngày</th>
              <th class="px-4 py-3 text-left text-xs font-medium text-gray-500 uppercase">Chứng từ</th>
              <th class="px-4 py-3 text-left text-xs font-medium text-gray-500 uppercase">Mã SP</th>
              <th class="px-4 py-3 text-left text-xs font-medium text-gray-500 uppercase">Tên SP</th>
              <th class="px-4 py-3 text-left text-xs font-medium text-gray-500 uppercase">Kho</th>
              <th class="px-4 py-3 text-right text-xs font-medium text-gray-500 uppercase">SL thay đổi</th>
              <th class="px-4 py-3 text-right text-xs font-medium text-gray-500 uppercase">SL sau GD</th>
              <th class="px-4 py-3 text-right text-xs font-medium text-gray-500 uppercase">Giá trị</th>
            </tr>
          </thead>
          <tbody class="divide-y divide-gray-200">
            <tr v-for="entry in stockLedger" :key="entry.name" class="hover:bg-gray-50">
              <td class="px-4 py-3 text-sm text-gray-500">{{ formatDateTime(entry.posting_date, entry.posting_time) }}</td>
              <td class="px-4 py-3 text-sm">
                <a :href="`/app/${entry.voucher_type.replace(' ', '-').toLowerCase()}/${entry.voucher_no}`" 
                   class="text-primary hover:underline" target="_blank">
                  {{ entry.voucher_no }}
                </a>
              </td>
              <td class="px-4 py-3 text-sm font-medium text-gray-900">{{ entry.item_code }}</td>
              <td class="px-4 py-3 text-sm text-gray-700">{{ entry.item_name }}</td>
              <td class="px-4 py-3 text-sm text-gray-700">{{ formatWarehouse(entry.warehouse) }}</td>
              <td class="px-4 py-3 text-sm text-right">
                <span :class="entry.actual_qty > 0 ? 'text-green-600' : 'text-red-600'">
                  {{ entry.actual_qty > 0 ? '+' : '' }}{{ formatNumber(entry.actual_qty) }}
                </span>
              </td>
              <td class="px-4 py-3 text-sm text-right">{{ formatNumber(entry.qty_after_transaction) }}</td>
              <td class="px-4 py-3 text-sm text-right font-medium">
                <span :class="entry.stock_value_difference > 0 ? 'text-green-600' : 'text-red-600'">
                  {{ entry.stock_value_difference > 0 ? '+' : '' }}{{ formatCurrency(entry.stock_value_difference) }}
                </span>
              </td>
            </tr>
          </tbody>
        </table>
      </div>

      <!-- Pagination -->
      <div v-if="pagination.totalPages > 1" class="px-6 py-4 border-t border-gray-200">
        <div class="flex items-center justify-between">
          <div class="text-sm text-gray-500">
            Hiển thị {{ (pagination.page - 1) * pagination.pageSize + 1 }} - 
            {{ Math.min(pagination.page * pagination.pageSize, pagination.total) }} / {{ pagination.total }}
          </div>
          <div class="flex items-center gap-2">
            <button
              @click="goToPage(pagination.page - 1)"
              :disabled="pagination.page <= 1"
              class="px-3 py-1 border rounded-lg text-sm disabled:opacity-50 disabled:cursor-not-allowed hover:bg-gray-50"
            >
              Trước
            </button>
            <span class="px-3 py-1 text-sm text-gray-600">
              Trang {{ pagination.page }} / {{ pagination.totalPages }}
            </span>
            <button
              @click="goToPage(pagination.page + 1)"
              :disabled="pagination.page >= pagination.totalPages"
              class="px-3 py-1 border rounded-lg text-sm disabled:opacity-50 disabled:cursor-not-allowed hover:bg-gray-50"
            >
              Sau
            </button>
          </div>
        </div>
      </div>
    </div>

    <!-- Toast -->
    <div
      v-if="toast.show"
      :class="[
        'fixed bottom-4 right-4 px-4 py-3 rounded-lg shadow-lg flex items-center gap-2 z-50 transition-all',
        toast.type === 'success' ? 'bg-green-500 text-white' : 'bg-red-500 text-white'
      ]"
    >
      {{ toast.message }}
    </div>
  </div>
</template>

<script setup>
import { ref, reactive, computed, onMounted, watch } from 'vue'
import { warehouseStockAPI, stockAPI } from '@/api'

// State
const loading = ref(false)
const viewMode = ref('warehouse')
const warehouses = ref([])
const warehouseStocks = ref([])
const itemStocks = ref([])
const stockLedger = ref([])
const expandedWarehouses = ref([])

// Pagination
const pagination = reactive({
  page: 1,
  pageSize: 50,
  total: 0,
  totalPages: 1
})

// Filters
const filters = reactive({
  search: '',
  warehouse: '',
  item_group: '',
  from_date: ''
})

// Summary
const summary = reactive({
  totalItems: 0,
  totalQty: 0,
  totalValue: 0
})

// Toast
const toast = reactive({
  show: false,
  type: 'success',
  message: ''
})

// Debounce
let searchTimeout = null

// Methods
const formatNumber = (num) => {
  if (!num) return '0'
  return new Intl.NumberFormat('vi-VN').format(num)
}

const formatCurrency = (num) => {
  if (!num) return '0 ₫'
  return new Intl.NumberFormat('vi-VN', { style: 'currency', currency: 'VND' }).format(num)
}

const formatWarehouse = (wh) => {
  if (!wh) return 'N/A'
  return wh.split(' - ')[0]
}

const formatUOM = (uom) => {
  if (!uom) return ''
  const uomMap = {
    'Nos': 'Cái',
    'Kg': 'Kg',
    'Meter': 'Mét',
    'Unit': 'Đơn vị',
    'Box': 'Hộp',
    'Pair': 'Cặp',
    'Set': 'Bộ',
    'Litre': 'Lít',
    'Gram': 'Gram'
  }
  return uomMap[uom] || uom
}

const formatDateTime = (date, time) => {
  if (!date) return ''
  const d = new Date(date)
  let result = d.toLocaleDateString('vi-VN')
  if (time) {
    result += ' ' + time.substring(0, 5)
  }
  return result
}

const showToast = (type, message) => {
  toast.type = type
  toast.message = message
  toast.show = true
  setTimeout(() => { toast.show = false }, 3000)
}

const debouncedSearch = () => {
  if (searchTimeout) clearTimeout(searchTimeout)
  searchTimeout = setTimeout(() => {
    pagination.page = 1
    loadData()
  }, 300)
}

const onFilterChange = () => {
  pagination.page = 1
  loadData()
}

const toggleWarehouse = (warehouseName) => {
  const index = expandedWarehouses.value.indexOf(warehouseName)
  if (index > -1) {
    expandedWarehouses.value.splice(index, 1)
  } else {
    expandedWarehouses.value.push(warehouseName)
  }
}

const loadWarehouses = async () => {
  try {
    const result = await stockAPI.getWarehouses(0)
    warehouses.value = result || []
  } catch (error) {
    console.error('Error loading warehouses:', error)
  }
}

const loadData = async () => {
  loading.value = true
  try {
    if (viewMode.value === 'warehouse') {
      await loadWarehouseStocks()
    } else if (viewMode.value === 'item') {
      await loadItemStocks()
    } else if (viewMode.value === 'ledger') {
      await loadStockLedger()
    }
  } catch (error) {
    console.error('Error loading data:', error)
    showToast('error', 'Không thể tải dữ liệu')
  } finally {
    loading.value = false
  }
}

const loadWarehouseStocks = async () => {
  try {
    const params = {}
    if (filters.item_group) params.item_group = filters.item_group
    if (filters.search) params.search = filters.search
    
    const result = await warehouseStockAPI.getByWarehouse(params)
    
    // API returns { data: [...], summary: {...} }
    warehouseStocks.value = result.data || []
    
    // Update summary from API response
    if (result.summary) {
      summary.totalItems = result.summary.totalItems || 0
      summary.totalQty = result.summary.totalQty || 0
      summary.totalValue = result.summary.totalValue || 0
    }
    
    // Auto expand first warehouse
    if (warehouseStocks.value.length > 0 && expandedWarehouses.value.length === 0) {
      expandedWarehouses.value.push(warehouseStocks.value[0].warehouse)
    }
  } catch (error) {
    console.error('Error loading warehouse stocks:', error)
    warehouseStocks.value = []
  }
}

const loadItemStocks = async () => {
  try {
    const params = {
      page: pagination.page,
      page_size: pagination.pageSize
    }
    if (filters.warehouse) params.warehouse = filters.warehouse
    if (filters.item_group) params.item_group = filters.item_group
    if (filters.search) params.search = filters.search
    
    const result = await warehouseStockAPI.getAll(params)
    
    // API returns { data: [...], total, page, page_size, total_pages }
    if (result && result.data) {
      itemStocks.value = result.data
      pagination.total = result.total || 0
      pagination.totalPages = result.total_pages || 1
      
      // Calculate summary from all items
      let totalQty = 0
      let totalValue = 0
      result.data.forEach(item => {
        totalQty += item.actual_qty || 0
        totalValue += item.stock_value || 0
      })
      summary.totalQty = totalQty
      summary.totalValue = totalValue
      summary.totalItems = result.total || result.data.length
    } else if (Array.isArray(result)) {
      // Fallback for array response
      itemStocks.value = result
      pagination.total = result.length
      pagination.totalPages = 1
      
      let totalQty = 0
      let totalValue = 0
      result.forEach(item => {
        totalQty += item.actual_qty || 0
        totalValue += item.stock_value || 0
      })
      summary.totalQty = totalQty
      summary.totalValue = totalValue
      summary.totalItems = result.length
    } else {
      itemStocks.value = []
    }
  } catch (error) {
    console.error('Error loading item stocks:', error)
    itemStocks.value = []
  }
}

const loadStockLedger = async () => {
  try {
    const params = {
      page: pagination.page,
      page_size: pagination.pageSize
    }
    if (filters.warehouse) params.warehouse = filters.warehouse
    if (filters.search) params.item_code = filters.search
    if (filters.from_date) params.from_date = filters.from_date
    
    const result = await warehouseStockAPI.getLedger(params)
    
    if (Array.isArray(result)) {
      stockLedger.value = result
      pagination.total = result.length
      pagination.totalPages = 1
    } else {
      stockLedger.value = result.data || []
      pagination.total = result.total || 0
      pagination.totalPages = result.total_pages || 1
    }
  } catch (error) {
    console.error('Error loading stock ledger:', error)
    stockLedger.value = []
  }
}

const exportStock = () => {
  showToast('success', 'Tính năng xuất Excel đang phát triển')
}

const goToPage = (page) => {
  if (page >= 1 && page <= pagination.totalPages) {
    pagination.page = page
    loadData()
  }
}

// Watch view mode change
watch(viewMode, () => {
  pagination.page = 1
  loadData()
})

// Initialize
onMounted(async () => {
  await loadWarehouses()
  await loadData()
})
</script>

<style scoped>
.bg-primary {
  background-color: #055568;
}
.bg-primary\/10 {
  background-color: rgba(5, 85, 104, 0.1);
}
.text-primary {
  color: #055568;
}
.border-primary {
  border-color: #055568;
}
.focus\:ring-primary:focus {
  --tw-ring-color: #055568;
}
.focus\:border-primary:focus {
  border-color: #055568;
}
</style>
