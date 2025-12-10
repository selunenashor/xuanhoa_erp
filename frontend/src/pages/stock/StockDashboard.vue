<template>
  <div class="space-y-6">
    <!-- Header -->
    <div class="bg-gradient-to-r from-blue-600 to-blue-400 rounded-xl p-6 text-white">
      <h2 class="text-2xl font-bold mb-2">Tổng quan kho hàng</h2>
      <p class="text-white/80">Thống kê và phân tích tình hình nhập xuất tồn kho</p>
    </div>

    <!-- Loading State -->
    <div v-if="loading" class="flex justify-center py-12">
      <svg class="animate-spin h-12 w-12 text-primary" xmlns="http://www.w3.org/2000/svg" fill="none" viewBox="0 0 24 24">
        <circle class="opacity-25" cx="12" cy="12" r="10" stroke="currentColor" stroke-width="4"></circle>
        <path class="opacity-75" fill="currentColor" d="M4 12a8 8 0 018-8V0C5.373 0 0 5.373 0 12h4zm2 5.291A7.962 7.962 0 014 12H0c0 3.042 1.135 5.824 3 7.938l3-2.647z"></path>
      </svg>
    </div>

    <template v-else>
      <!-- KPI Cards -->
      <div class="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-4">
        <div class="bg-white rounded-xl p-5 shadow-sm border border-gray-100">
          <div class="flex items-start justify-between">
            <div>
              <p class="text-sm text-gray-500 mb-1">Tổng giá trị tồn kho</p>
              <p class="text-2xl font-bold text-gray-800">{{ formatCurrency(data.stock_value) }}</p>
              <p class="text-xs text-gray-400 mt-1">{{ data.total_items }} sản phẩm</p>
            </div>
            <div class="w-12 h-12 rounded-lg bg-teal-100 flex items-center justify-center">
              <BoxIcon class="w-6 h-6 text-teal-600" />
            </div>
          </div>
        </div>

        <div class="bg-white rounded-xl p-5 shadow-sm border border-gray-100">
          <div class="flex items-start justify-between">
            <div>
              <p class="text-sm text-gray-500 mb-1">Cần nhập thêm</p>
              <p class="text-2xl font-bold text-red-600">{{ data.low_stock_items }}</p>
              <p class="text-xs text-gray-400 mt-1">Sản phẩm thiếu hụt</p>
            </div>
            <div class="w-12 h-12 rounded-lg bg-red-100 flex items-center justify-center">
              <AlertIcon class="w-6 h-6 text-red-600" />
            </div>
          </div>
        </div>

        <div class="bg-white rounded-xl p-5 shadow-sm border border-gray-100">
          <div class="flex items-start justify-between">
            <div>
              <p class="text-sm text-gray-500 mb-1">Nhập kho tháng này</p>
              <p class="text-2xl font-bold text-green-600">{{ data.receipts_month }}</p>
              <p class="text-xs text-gray-400 mt-1">Phiếu nhập</p>
            </div>
            <div class="w-12 h-12 rounded-lg bg-green-100 flex items-center justify-center">
              <PlusIcon class="w-6 h-6 text-green-600" />
            </div>
          </div>
        </div>

        <div class="bg-white rounded-xl p-5 shadow-sm border border-gray-100">
          <div class="flex items-start justify-between">
            <div>
              <p class="text-sm text-gray-500 mb-1">Xuất kho tháng này</p>
              <p class="text-2xl font-bold text-blue-600">{{ data.issues_month }}</p>
              <p class="text-xs text-gray-400 mt-1">Phiếu xuất</p>
            </div>
            <div class="w-12 h-12 rounded-lg bg-blue-100 flex items-center justify-center">
              <TruckIcon class="w-6 h-6 text-blue-600" />
            </div>
          </div>
        </div>
      </div>

      <!-- Charts Row -->
      <div class="grid grid-cols-1 lg:grid-cols-2 gap-6">
        <!-- Stock Movement Chart -->
        <div class="bg-white rounded-xl p-6 shadow-sm border border-gray-100">
          <h3 class="text-lg font-semibold text-gray-800 mb-4">Biến động xuất nhập kho (tháng này)</h3>
          <div class="h-80">
            <svg class="w-full h-full" viewBox="0 0 520 260" preserveAspectRatio="xMidYMid meet">
              <!-- Y-axis labels -->
              <text x="10" y="20" class="text-xs fill-gray-400">{{ maxMovement }}</text>
              <text x="10" y="105" class="text-xs fill-gray-400">{{ Math.round(maxMovement/2) }}</text>
              <text x="10" y="185" class="text-xs fill-gray-400">0</text>
              
              <!-- Grid lines -->
              <line x1="45" y1="20" x2="510" y2="20" stroke="#E5E7EB" stroke-width="1" stroke-dasharray="2,2"/>
              <line x1="45" y1="105" x2="510" y2="105" stroke="#E5E7EB" stroke-width="1" stroke-dasharray="2,2"/>
              <line x1="45" y1="185" x2="510" y2="185" stroke="#E5E7EB" stroke-width="1"/>
              
              <!-- Receipt bars -->
              <rect v-for="(point, i) in chartData" :key="'receipt-'+i"
                    :x="65 + i * 70" 
                    :y="185 - point.receiptHeight" 
                    :width="24" 
                    :height="point.receiptHeight"
                    class="fill-green-400 hover:fill-green-500 transition-colors"
                    rx="3">
                <title>Nhập: {{ point.receipts }} phiếu</title>
              </rect>
              
              <!-- Issue bars -->
              <rect v-for="(point, i) in chartData" :key="'issue-'+i"
                    :x="92 + i * 70" 
                    :y="185 - point.issueHeight" 
                    :width="24" 
                    :height="point.issueHeight"
                    class="fill-blue-400 hover:fill-blue-500 transition-colors"
                    rx="3">
                <title>Xuất: {{ point.issues }} phiếu</title>
              </rect>
              
              <!-- X-axis labels -->
              <text v-for="(point, i) in chartData" :key="'label-'+i"
                    :x="80 + i * 70" 
                    y="205" 
                    text-anchor="middle"
                    class="text-sm fill-gray-600 font-medium">
                {{ point.day }}
              </text>
            </svg>
          </div>
          <div class="flex items-center justify-center gap-6 mt-4 pt-4 border-t border-gray-100">
            <div class="flex items-center gap-2">
              <div class="w-3 h-3 rounded bg-green-400"></div>
              <span class="text-xs text-gray-600">Phiếu nhập</span>
            </div>
            <div class="flex items-center gap-2">
              <div class="w-3 h-3 rounded bg-blue-400"></div>
              <span class="text-xs text-gray-600">Phiếu xuất</span>
            </div>
          </div>
        </div>

        <!-- Top Items Table -->
        <div class="bg-white rounded-xl p-6 shadow-sm border border-gray-100">
          <h3 class="text-lg font-semibold text-gray-800 mb-4">Top 5 tồn kho theo giá trị</h3>
          <div class="space-y-3">
            <div v-for="(item, index) in data.top_items" :key="index"
                 class="flex items-center gap-4 p-3 rounded-lg border border-gray-100 hover:bg-gray-50 transition-colors">
              <div class="flex items-center justify-center w-8 h-8 rounded-full bg-primary/10 text-primary font-bold text-sm">
                {{ index + 1 }}
              </div>
              <div class="flex-1 min-w-0">
                <p class="text-sm font-medium text-gray-800 truncate">{{ item.item_name }}</p>
                <p class="text-xs text-gray-500">{{ item.item_code }}</p>
              </div>
              <div class="text-right">
                <p class="text-sm font-semibold text-gray-800">{{ formatNumber(item.total_qty) }} {{ item.uom }}</p>
                <p class="text-xs text-gray-500">{{ formatCurrency(item.total_value) }}</p>
              </div>
            </div>
            <div v-if="!data.top_items || data.top_items.length === 0" class="text-center py-8 text-gray-400">
              Chưa có dữ liệu
            </div>
          </div>
        </div>
      </div>

      <!-- Warehouse Activity -->
      <div class="bg-white rounded-xl p-6 shadow-sm border border-gray-100">
        <h3 class="text-lg font-semibold text-gray-800 mb-4">Kho có nhiều giao dịch nhất (tháng này)</h3>
        <div class="space-y-3">
          <div v-for="(wh, index) in data.top_warehouses" :key="index"
               class="flex items-center gap-4">
            <div class="flex-1">
              <div class="flex items-center justify-between mb-2">
                <span class="text-sm font-medium text-gray-700">{{ wh.warehouse }}</span>
                <span class="text-sm font-bold text-gray-800">{{ wh.transaction_count }} giao dịch</span>
              </div>
              <div class="w-full bg-gray-100 rounded-full h-2">
                <div class="bg-gradient-to-r from-blue-500 to-blue-400 h-2 rounded-full transition-all duration-500"
                     :style="{ width: getWarehousePercentage(wh.transaction_count) + '%' }">
                </div>
              </div>
            </div>
          </div>
          <div v-if="!data.top_warehouses || data.top_warehouses.length === 0" class="text-center py-8 text-gray-400">
            Chưa có dữ liệu
          </div>
        </div>
      </div>
    </template>
  </div>
</template>

<script setup>
import { h, ref, computed, onMounted } from 'vue'
import axios from 'axios'

const loading = ref(true)
const data = ref({
  stock_value: 0,
  total_items: 0,
  low_stock_items: 0,
  receipts_month: 0,
  issues_month: 0,
  top_items: [],
  stock_movement: [],
  top_warehouses: []
})

// Icons
const BoxIcon = {
  render: () => h('svg', { fill: 'none', stroke: 'currentColor', viewBox: '0 0 24 24' }, [
    h('path', { 'stroke-linecap': 'round', 'stroke-linejoin': 'round', 'stroke-width': '2',
      d: 'M20 7l-8-4-8 4m16 0l-8 4m8-4v10l-8 4m0-10L4 7m8 4v10M4 7v10l8 4' })
  ])
}

const AlertIcon = {
  render: () => h('svg', { fill: 'none', stroke: 'currentColor', viewBox: '0 0 24 24' }, [
    h('path', { 'stroke-linecap': 'round', 'stroke-linejoin': 'round', 'stroke-width': '2',
      d: 'M12 9v2m0 4h.01m-6.938 4h13.856c1.54 0 2.502-1.667 1.732-3L13.732 4c-.77-1.333-2.694-1.333-3.464 0L3.34 16c-.77 1.333.192 3 1.732 3z' })
  ])
}

const PlusIcon = {
  render: () => h('svg', { fill: 'none', stroke: 'currentColor', viewBox: '0 0 24 24' }, [
    h('path', { 'stroke-linecap': 'round', 'stroke-linejoin': 'round', 'stroke-width': '2', d: 'M12 4v16m8-8H4' })
  ])
}

const TruckIcon = {
  render: () => h('svg', { fill: 'none', stroke: 'currentColor', viewBox: '0 0 24 24' }, [
    h('path', { 'stroke-linecap': 'round', 'stroke-linejoin': 'round', 'stroke-width': '2',
      d: 'M13 16V6a1 1 0 00-1-1H4a1 1 0 00-1 1v10a1 1 0 001 1h1m8-1a1 1 0 01-1 1H9m4-1V8a1 1 0 011-1h2.586a1 1 0 01.707.293l3.414 3.414a1 1 0 01.293.707V16a1 1 0 01-1 1h-1m-6-1a1 1 0 001 1h1M5 17a2 2 0 104 0m-4 0a2 2 0 114 0m6 0a2 2 0 104 0m-4 0a2 2 0 114 0' })
  ])
}

// Chart data
const chartData = computed(() => {
  if (!data.value.stock_movement || data.value.stock_movement.length === 0) return []
  
  const movement = data.value.stock_movement
  const max = Math.max(...movement.map(d => Math.max(d.receipts, d.issues))) || 1
  
  return movement.map(d => ({
    ...d,
    receiptHeight: (d.receipts / max) * 170,
    issueHeight: (d.issues / max) * 170
  }))
})

const maxMovement = computed(() => {
  if (!data.value.stock_movement || data.value.stock_movement.length === 0) return 10
  const max = Math.max(...data.value.stock_movement.map(d => Math.max(d.receipts, d.issues)))
  return max + 2
})

// Format functions
const formatNumber = (num) => {
  if (!num) return '0'
  return new Intl.NumberFormat('vi-VN').format(num)
}

const formatCurrency = (amount) => {
  if (!amount) return '0 ₫'
  if (amount >= 1000000) {
    return (amount / 1000000).toFixed(1) + ' tr'
  }
  return new Intl.NumberFormat('vi-VN', { style: 'currency', currency: 'VND' }).format(amount)
}

const getWarehousePercentage = (count) => {
  if (!data.value.top_warehouses || data.value.top_warehouses.length === 0) return 0
  const max = Math.max(...data.value.top_warehouses.map(w => w.transaction_count))
  return (count / max) * 100
}

// Load data
const loadData = async () => {
  loading.value = true
  try {
    const response = await axios.get('/api/method/xuanhoa_app.api.get_stock_dashboard')
    if (response.data && response.data.message) {
      data.value = { ...data.value, ...response.data.message }
    }
  } catch (error) {
    console.error('Error loading stock dashboard:', error)
  } finally {
    loading.value = false
  }
}

onMounted(() => {
  loadData()
})
</script>
