<template>
  <div class="space-y-6">
    <!-- Header -->
    <div class="bg-gradient-to-r from-amber-600 to-amber-400 rounded-xl p-6 text-white">
      <h2 class="text-2xl font-bold mb-2">Tổng quan sản xuất</h2>
      <p class="text-white/80">Thống kê và phân tích hiệu suất sản xuất</p>
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
              <p class="text-sm text-gray-500 mb-1">Tổng lệnh SX</p>
              <p class="text-2xl font-bold text-gray-800">{{ data.total_work_orders }}</p>
              <p class="text-xs text-gray-400 mt-1">Tất cả trạng thái</p>
            </div>
            <div class="w-12 h-12 rounded-lg bg-purple-100 flex items-center justify-center">
              <ClipboardIcon class="w-6 h-6 text-purple-600" />
            </div>
          </div>
        </div>

        <div class="bg-white rounded-xl p-5 shadow-sm border border-gray-100">
          <div class="flex items-start justify-between">
            <div>
              <p class="text-sm text-gray-500 mb-1">Đang thực hiện</p>
              <p class="text-2xl font-bold text-amber-600">{{ data.wo_in_progress }}</p>
              <p class="text-xs text-gray-400 mt-1">{{ data.wo_not_started }} chưa bắt đầu</p>
            </div>
            <div class="w-12 h-12 rounded-lg bg-amber-100 flex items-center justify-center">
              <ManufactureIcon class="w-6 h-6 text-amber-600" />
            </div>
          </div>
        </div>

        <div class="bg-white rounded-xl p-5 shadow-sm border border-gray-100">
          <div class="flex items-start justify-between">
            <div>
              <p class="text-sm text-gray-500 mb-1">Hoàn thành</p>
              <p class="text-2xl font-bold text-green-600">{{ data.wo_completed }}</p>
              <p class="text-xs text-gray-400 mt-1">{{ data.wo_completed_week }} trong tuần</p>
            </div>
            <div class="w-12 h-12 rounded-lg bg-green-100 flex items-center justify-center">
              <CheckIcon class="w-6 h-6 text-green-600" />
            </div>
          </div>
        </div>

        <div class="bg-white rounded-xl p-5 shadow-sm border border-gray-100">
          <div class="flex items-start justify-between">
            <div>
              <p class="text-sm text-gray-500 mb-1">SX tháng này</p>
              <p class="text-2xl font-bold text-blue-600">{{ formatNumber(data.qty_produced_month) }}</p>
              <p class="text-xs text-gray-400 mt-1">Sản phẩm đã sản xuất</p>
            </div>
            <div class="w-12 h-12 rounded-lg bg-blue-100 flex items-center justify-center">
              <TrendIcon class="w-6 h-6 text-blue-600" />
            </div>
          </div>
        </div>
      </div>

      <!-- Charts Row -->
      <div class="grid grid-cols-1 lg:grid-cols-2 gap-6">
        <!-- Production Trend Chart -->
        <div class="bg-white rounded-xl p-6 shadow-sm border border-gray-100">
          <h3 class="text-lg font-semibold text-gray-800 mb-4">Xu hướng sản xuất (tháng này)</h3>
          <div class="h-80">
            <svg class="w-full h-full" viewBox="0 0 520 260" preserveAspectRatio="xMidYMid meet">
              <!-- Y-axis labels -->
              <text x="10" y="20" class="text-xs fill-gray-400">{{ maxProduction }}</text>
              <text x="10" y="105" class="text-xs fill-gray-400">{{ Math.round(maxProduction/2) }}</text>
              <text x="10" y="185" class="text-xs fill-gray-400">0</text>
              
              <!-- Grid lines -->
              <line x1="45" y1="20" x2="510" y2="20" stroke="#E5E7EB" stroke-width="1" stroke-dasharray="2,2"/>
              <line x1="45" y1="105" x2="510" y2="105" stroke="#E5E7EB" stroke-width="1" stroke-dasharray="2,2"/>
              <line x1="45" y1="185" x2="510" y2="185" stroke="#E5E7EB" stroke-width="1"/>
              
              <!-- Created bars -->
              <rect v-for="(point, i) in chartData" :key="'created-'+i"
                    :x="65 + i * 70" 
                    :y="185 - point.createdHeight" 
                    :width="24" 
                    :height="point.createdHeight"
                    class="fill-amber-400 hover:fill-amber-500 transition-colors"
                    rx="3">
                <title>Tạo mới: {{ point.created }} lệnh</title>
              </rect>
              
              <!-- Completed bars -->
              <rect v-for="(point, i) in chartData" :key="'completed-'+i"
                    :x="92 + i * 70" 
                    :y="185 - point.completedHeight" 
                    :width="24" 
                    :height="point.completedHeight"
                    class="fill-green-400 hover:fill-green-500 transition-colors"
                    rx="3">
                <title>Hoàn thành: {{ point.completed }} lệnh</title>
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
              <div class="w-3 h-3 rounded bg-amber-400"></div>
              <span class="text-xs text-gray-600">Lệnh tạo mới</span>
            </div>
            <div class="flex items-center gap-2">
              <div class="w-3 h-3 rounded bg-green-400"></div>
              <span class="text-xs text-gray-600">Lệnh hoàn thành</span>
            </div>
          </div>
        </div>

        <!-- Work Order Status Donut -->
        <div class="bg-white rounded-xl p-6 shadow-sm border border-gray-100">
          <h3 class="text-lg font-semibold text-gray-800 mb-4">Trạng thái lệnh sản xuất</h3>
          <div class="h-64 flex items-center justify-center">
            <svg class="w-48 h-48" viewBox="0 0 200 200">
              <!-- Background circle -->
              <circle cx="100" cy="100" r="80" fill="none" stroke="#F3F4F6" stroke-width="20"/>
              
              <!-- Progress arcs -->
              <circle v-if="workOrderTotal > 0"
                      cx="100" cy="100" r="80" 
                      fill="none" 
                      stroke="#10B981" 
                      stroke-width="20"
                      :stroke-dasharray="`${completedPercent * 5.024} 502.4`"
                      transform="rotate(-90 100 100)"
                      class="transition-all duration-500"/>
              
              <circle v-if="workOrderTotal > 0"
                      cx="100" cy="100" r="80" 
                      fill="none" 
                      stroke="#F59E0B" 
                      stroke-width="20"
                      :stroke-dasharray="`${inProgressPercent * 5.024} 502.4`"
                      :stroke-dashoffset="`${-completedPercent * 5.024}`"
                      transform="rotate(-90 100 100)"
                      class="transition-all duration-500"/>
              
              <!-- Center text -->
              <text x="100" y="95" text-anchor="middle" class="text-2xl font-bold fill-gray-800">
                {{ workOrderTotal }}
              </text>
              <text x="100" y="115" text-anchor="middle" class="text-xs fill-gray-500">
                Lệnh SX
              </text>
            </svg>
          </div>
          <div class="space-y-2 mt-4 pt-4 border-t border-gray-100">
            <div class="flex items-center justify-between">
              <div class="flex items-center gap-2">
                <div class="w-3 h-3 rounded-full bg-green-500"></div>
                <span class="text-sm text-gray-600">Hoàn thành</span>
              </div>
              <span class="text-sm font-medium text-gray-800">{{ data.wo_completed }}</span>
            </div>
            <div class="flex items-center justify-between">
              <div class="flex items-center gap-2">
                <div class="w-3 h-3 rounded-full bg-amber-500"></div>
                <span class="text-sm text-gray-600">Đang thực hiện</span>
              </div>
              <span class="text-sm font-medium text-gray-800">{{ data.wo_in_progress }}</span>
            </div>
            <div class="flex items-center justify-between">
              <div class="flex items-center gap-2">
                <div class="w-3 h-3 rounded-full bg-gray-300"></div>
                <span class="text-sm text-gray-600">Chưa bắt đầu</span>
              </div>
              <span class="text-sm font-medium text-gray-800">{{ data.wo_not_started }}</span>
            </div>
            <div v-if="data.wo_stopped > 0" class="flex items-center justify-between">
              <div class="flex items-center gap-2">
                <div class="w-3 h-3 rounded-full bg-red-500"></div>
                <span class="text-sm text-gray-600">Đã dừng</span>
              </div>
              <span class="text-sm font-medium text-gray-800">{{ data.wo_stopped }}</span>
            </div>
          </div>
        </div>
      </div>

      <!-- Top Products Table -->
      <div class="bg-white rounded-xl p-6 shadow-sm border border-gray-100">
        <h3 class="text-lg font-semibold text-gray-800 mb-4">Top 5 sản phẩm sản xuất nhiều nhất</h3>
        <div class="space-y-3">
          <div v-for="(product, index) in data.top_products" :key="index"
               class="flex items-center gap-4 p-3 rounded-lg border border-gray-100 hover:bg-gray-50 transition-colors">
            <div class="flex items-center justify-center w-8 h-8 rounded-full bg-amber-100 text-amber-600 font-bold text-sm">
              {{ index + 1 }}
            </div>
            <div class="flex-1 min-w-0">
              <p class="text-sm font-medium text-gray-800 truncate">{{ product.item_name }}</p>
              <p class="text-xs text-gray-500">{{ product.production_item }}</p>
            </div>
            <div class="text-right">
              <p class="text-sm font-semibold text-gray-800">{{ formatNumber(product.produced_qty) }} {{ product.uom }}</p>
              <p class="text-xs text-gray-500">{{ product.order_count }} lệnh sản xuất</p>
            </div>
            <div class="w-32">
              <div class="w-full bg-gray-100 rounded-full h-2">
                <div class="bg-gradient-to-r from-amber-500 to-amber-400 h-2 rounded-full"
                     :style="{ width: getProductPercentage(product.produced_qty) + '%' }">
                </div>
              </div>
            </div>
          </div>
          <div v-if="!data.top_products || data.top_products.length === 0" class="text-center py-8 text-gray-400">
            Chưa có dữ liệu
          </div>
        </div>
      </div>

      <!-- Urgent Orders -->
      <div v-if="data.urgent_orders && data.urgent_orders.length > 0" 
           class="bg-gradient-to-r from-red-50 to-orange-50 rounded-xl p-6 border border-red-100">
        <div class="flex items-center gap-2 mb-4">
          <AlertIcon class="w-6 h-6 text-red-600" />
          <h3 class="text-lg font-semibold text-gray-800">Lệnh sắp hết hạn (3 ngày tới)</h3>
        </div>
        <div class="space-y-3">
          <div v-for="order in data.urgent_orders" :key="order.name"
               class="flex items-center gap-4 p-4 bg-white rounded-lg border border-red-200">
            <div class="flex-1">
              <p class="text-sm font-medium text-gray-800">{{ order.name }}</p>
              <p class="text-xs text-gray-500 mt-1">{{ order.production_item }}</p>
            </div>
            <div class="text-right">
              <p class="text-sm font-semibold text-gray-700">
                {{ formatNumber(order.produced_qty) }} / {{ formatNumber(order.qty) }}
              </p>
              <p class="text-xs text-red-600">Hạn: {{ formatDate(order.planned_end_date) }}</p>
            </div>
            <div :class="['px-3 py-1 rounded-full text-xs font-medium',
                          order.status === 'In Process' ? 'bg-amber-100 text-amber-700' : 'bg-gray-100 text-gray-700']">
              {{ translateStatus(order.status) }}
            </div>
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
  total_work_orders: 0,
  wo_not_started: 0,
  wo_in_progress: 0,
  wo_completed: 0,
  wo_stopped: 0,
  wo_this_week: 0,
  wo_completed_week: 0,
  qty_produced_month: 0,
  top_products: [],
  production_trend: [],
  urgent_orders: []
})

// Icons
const ClipboardIcon = {
  render: () => h('svg', { fill: 'none', stroke: 'currentColor', viewBox: '0 0 24 24' }, [
    h('path', { 'stroke-linecap': 'round', 'stroke-linejoin': 'round', 'stroke-width': '2',
      d: 'M9 5H7a2 2 0 00-2 2v12a2 2 0 002 2h10a2 2 0 002-2V7a2 2 0 00-2-2h-2M9 5a2 2 0 002 2h2a2 2 0 002-2M9 5a2 2 0 012-2h2a2 2 0 012 2' })
  ])
}

const ManufactureIcon = {
  render: () => h('svg', { fill: 'none', stroke: 'currentColor', viewBox: '0 0 24 24' }, [
    h('path', { 'stroke-linecap': 'round', 'stroke-linejoin': 'round', 'stroke-width': '2',
      d: 'M19.428 15.428a2 2 0 00-1.022-.547l-2.387-.477a6 6 0 00-3.86.517l-.318.158a6 6 0 01-3.86.517L6.05 15.21a2 2 0 00-1.806.547M8 4h8l-1 1v5.172a2 2 0 00.586 1.414l5 5c1.26 1.26.367 3.414-1.415 3.414H4.828c-1.782 0-2.674-2.154-1.414-3.414l5-5A2 2 0 009 10.172V5L8 4z' })
  ])
}

const CheckIcon = {
  render: () => h('svg', { fill: 'none', stroke: 'currentColor', viewBox: '0 0 24 24' }, [
    h('path', { 'stroke-linecap': 'round', 'stroke-linejoin': 'round', 'stroke-width': '2', d: 'M5 13l4 4L19 7' })
  ])
}

const TrendIcon = {
  render: () => h('svg', { fill: 'none', stroke: 'currentColor', viewBox: '0 0 24 24' }, [
    h('path', { 'stroke-linecap': 'round', 'stroke-linejoin': 'round', 'stroke-width': '2', d: 'M13 7h8m0 0v8m0-8l-8 8-4-4-6 6' })
  ])
}

const AlertIcon = {
  render: () => h('svg', { fill: 'none', stroke: 'currentColor', viewBox: '0 0 24 24' }, [
    h('path', { 'stroke-linecap': 'round', 'stroke-linejoin': 'round', 'stroke-width': '2',
      d: 'M12 9v2m0 4h.01m-6.938 4h13.856c1.54 0 2.502-1.667 1.732-3L13.732 4c-.77-1.333-2.694-1.333-3.464 0L3.34 16c-.77 1.333.192 3 1.732 3z' })
  ])
}

// Computed
const workOrderTotal = computed(() => {
  return data.value.wo_completed + data.value.wo_in_progress + data.value.wo_not_started
})

const completedPercent = computed(() => {
  return workOrderTotal.value > 0 ? (data.value.wo_completed / workOrderTotal.value) * 100 : 0
})

const inProgressPercent = computed(() => {
  return workOrderTotal.value > 0 ? (data.value.wo_in_progress / workOrderTotal.value) * 100 : 0
})

const chartData = computed(() => {
  if (!data.value.production_trend || data.value.production_trend.length === 0) return []
  
  const trend = data.value.production_trend
  const max = Math.max(...trend.map(d => Math.max(d.created, d.completed))) || 1
  
  return trend.map(d => ({
    ...d,
    createdHeight: (d.created / max) * 170,
    completedHeight: (d.completed / max) * 170
  }))
})

const maxProduction = computed(() => {
  if (!data.value.production_trend || data.value.production_trend.length === 0) return 10
  const max = Math.max(...data.value.production_trend.map(d => Math.max(d.created, d.completed)))
  return max + 2
})

// Format functions
const formatNumber = (num) => {
  if (!num) return '0'
  return new Intl.NumberFormat('vi-VN').format(num)
}

const formatDate = (dateStr) => {
  if (!dateStr) return ''
  const date = new Date(dateStr)
  return date.toLocaleDateString('vi-VN', { day: '2-digit', month: '2-digit' })
}

const translateStatus = (status) => {
  const statusMap = {
    'Not Started': 'Chưa bắt đầu',
    'In Process': 'Đang thực hiện',
    'Completed': 'Hoàn thành',
    'Stopped': 'Đã dừng'
  }
  return statusMap[status] || status
}

const getProductPercentage = (qty) => {
  if (!data.value.top_products || data.value.top_products.length === 0) return 0
  const max = Math.max(...data.value.top_products.map(p => p.produced_qty))
  return (qty / max) * 100
}

// Load data
const loadData = async () => {
  loading.value = true
  try {
    const response = await axios.get('/api/method/xuanhoa_app.api.get_production_dashboard')
    if (response.data && response.data.message) {
      data.value = { ...data.value, ...response.data.message }
    }
  } catch (error) {
    console.error('Error loading production dashboard:', error)
  } finally {
    loading.value = false
  }
}

onMounted(() => {
  loadData()
})
</script>
