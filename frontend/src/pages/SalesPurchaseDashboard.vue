<template>
  <div class="space-y-6">
    <!-- Header -->
    <div class="bg-gradient-to-r from-purple-600 to-purple-400 rounded-xl p-6 text-white">
      <h2 class="text-2xl font-bold mb-2">Tổng quan mua bán</h2>
      <p class="text-white/80">Thống kê và phân tích hoạt động kinh doanh</p>
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
              <p class="text-sm text-gray-500 mb-1">Tổng mua tháng này</p>
              <p class="text-2xl font-bold text-orange-600">{{ formatCurrency(data.purchase_value_month) }}</p>
              <p class="text-xs text-gray-400 mt-1">{{ data.purchase_submitted }} hóa đơn</p>
            </div>
            <div class="w-12 h-12 rounded-lg bg-orange-100 flex items-center justify-center">
              <PurchaseIcon class="w-6 h-6 text-orange-600" />
            </div>
          </div>
        </div>

        <div class="bg-white rounded-xl p-5 shadow-sm border border-gray-100">
          <div class="flex items-start justify-between">
            <div>
              <p class="text-sm text-gray-500 mb-1">Tổng bán tháng này</p>
              <p class="text-2xl font-bold text-green-600">{{ formatCurrency(data.sales_value_month) }}</p>
              <p class="text-xs text-gray-400 mt-1">{{ data.sales_submitted }} hóa đơn</p>
            </div>
            <div class="w-12 h-12 rounded-lg bg-green-100 flex items-center justify-center">
              <SalesIcon class="w-6 h-6 text-green-600" />
            </div>
          </div>
        </div>

        <div class="bg-white rounded-xl p-5 shadow-sm border border-gray-100">
          <div class="flex items-start justify-between">
            <div>
              <p class="text-sm text-gray-500 mb-1">Lợi nhuận gộp</p>
              <p class="text-2xl font-bold text-blue-600">{{ formatCurrency(data.gross_profit) }}</p>
              <p class="text-xs text-gray-400 mt-1">{{ data.profit_margin.toFixed(1) }}% biên lợi nhuận</p>
            </div>
            <div class="w-12 h-12 rounded-lg bg-blue-100 flex items-center justify-center">
              <TrendIcon class="w-6 h-6 text-blue-600" />
            </div>
          </div>
        </div>

        <div class="bg-white rounded-xl p-5 shadow-sm border border-gray-100">
          <div class="flex items-start justify-between">
            <div>
              <p class="text-sm text-gray-500 mb-1">Đơn chờ xử lý</p>
              <p class="text-2xl font-bold text-amber-600">{{ data.purchase_pending + data.sales_pending }}</p>
              <p class="text-xs text-gray-400 mt-1">Cần duyệt</p>
            </div>
            <div class="w-12 h-12 rounded-lg bg-amber-100 flex items-center justify-center">
              <ClockIcon class="w-6 h-6 text-amber-600" />
            </div>
          </div>
        </div>
      </div>

      <!-- Charts Row -->
      <div class="grid grid-cols-1 lg:grid-cols-2 gap-6">
        <!-- Purchase vs Sales Trend -->
        <div class="bg-white rounded-xl p-6 shadow-sm border border-gray-100">
          <h3 class="text-lg font-semibold text-gray-800 mb-4">Xu hướng mua bán (tháng này)</h3>
          <div class="h-80">
            <svg class="w-full h-full" viewBox="0 0 420 260" preserveAspectRatio="xMidYMid meet">
              <!-- Y-axis labels -->
              <text x="10" y="20" class="text-xs fill-gray-400">{{ maxTrend }}</text>
              <text x="10" y="105" class="text-xs fill-gray-400">{{ Math.round(maxTrend/2) }}</text>
              <text x="10" y="185" class="text-xs fill-gray-400">0</text>
              
              <!-- Grid lines -->
              <line x1="45" y1="20" x2="410" y2="20" stroke="#E5E7EB" stroke-width="1" stroke-dasharray="2,2"/>
              <line x1="45" y1="105" x2="410" y2="105" stroke="#E5E7EB" stroke-width="1" stroke-dasharray="2,2"/>
              <line x1="45" y1="185" x2="410" y2="185" stroke="#E5E7EB" stroke-width="1"/>
              
              <!-- Purchase bars -->
              <rect v-for="(point, i) in trendChartData" :key="'purchase-'+i"
                    :x="65 + i * 85" 
                    :y="185 - point.purchaseHeight" 
                    :width="28" 
                    :height="point.purchaseHeight"
                    class="fill-orange-400 hover:fill-orange-500 transition-colors"
                    rx="3">
                <title>Mua: {{ point.purchase_count }} đơn - {{ formatCurrency(point.purchase_value) }}</title>
              </rect>
              
              <!-- Sales bars -->
              <rect v-for="(point, i) in trendChartData" :key="'sales-'+i"
                    :x="95 + i * 85" 
                    :y="185 - point.salesHeight" 
                    :width="28" 
                    :height="point.salesHeight"
                    class="fill-green-400 hover:fill-green-500 transition-colors"
                    rx="3">
                <title>Bán: {{ point.sales_count }} đơn - {{ formatCurrency(point.sales_value) }}</title>
              </rect>
              
              <!-- X-axis labels -->
              <text v-for="(point, i) in trendChartData" :key="'label-'+i"
                    :x="80 + i * 85" 
                    y="205" 
                    text-anchor="middle"
                    class="text-sm fill-gray-600 font-medium">
                {{ point.week }}
              </text>
            </svg>
          </div>
          <div class="flex items-center justify-center gap-6 mt-4 pt-4 border-t border-gray-100">
            <div class="flex items-center gap-2">
              <div class="w-3 h-3 rounded bg-orange-400"></div>
              <span class="text-xs text-gray-600">Hóa đơn mua</span>
            </div>
            <div class="flex items-center gap-2">
              <div class="w-3 h-3 rounded bg-green-400"></div>
              <span class="text-xs text-gray-600">Hóa đơn bán</span>
            </div>
          </div>
        </div>

        <!-- Invoice Status Distribution -->
        <div class="bg-white rounded-xl p-6 shadow-sm border border-gray-100">
          <h3 class="text-lg font-semibold text-gray-800 mb-4">Phân bổ trạng thái hóa đơn</h3>
          <div class="space-y-4 mt-6">
            <!-- Purchase Invoices -->
            <div>
              <div class="flex items-center justify-between mb-2">
                <span class="text-sm font-medium text-gray-700">Hóa đơn mua</span>
                <span class="text-sm font-bold text-gray-800">{{ data.total_purchase }}</span>
              </div>
              <div class="flex gap-1 h-3 rounded-full overflow-hidden bg-gray-100">
                <div v-if="data.purchase_submitted > 0"
                     :style="{ width: (data.purchase_submitted / data.total_purchase * 100) + '%' }"
                     class="bg-green-500 transition-all"
                     :title="`Đã duyệt: ${data.purchase_submitted}`">
                </div>
                <div v-if="data.purchase_pending > 0"
                     :style="{ width: (data.purchase_pending / data.total_purchase * 100) + '%' }"
                     class="bg-amber-500 transition-all"
                     :title="`Chờ duyệt: ${data.purchase_pending}`">
                </div>
                <div v-if="data.purchase_cancelled > 0"
                     :style="{ width: (data.purchase_cancelled / data.total_purchase * 100) + '%' }"
                     class="bg-red-500 transition-all"
                     :title="`Đã hủy: ${data.purchase_cancelled}`">
                </div>
              </div>
              <div class="flex items-center gap-4 mt-2 text-xs">
                <span class="text-green-600">✓ {{ data.purchase_submitted }}</span>
                <span class="text-amber-600">⏳ {{ data.purchase_pending }}</span>
                <span class="text-red-600">✗ {{ data.purchase_cancelled }}</span>
              </div>
            </div>

            <!-- Sales Invoices -->
            <div>
              <div class="flex items-center justify-between mb-2">
                <span class="text-sm font-medium text-gray-700">Hóa đơn bán</span>
                <span class="text-sm font-bold text-gray-800">{{ data.total_sales }}</span>
              </div>
              <div class="flex gap-1 h-3 rounded-full overflow-hidden bg-gray-100">
                <div v-if="data.sales_submitted > 0"
                     :style="{ width: (data.sales_submitted / data.total_sales * 100) + '%' }"
                     class="bg-green-500 transition-all"
                     :title="`Đã duyệt: ${data.sales_submitted}`">
                </div>
                <div v-if="data.sales_pending > 0"
                     :style="{ width: (data.sales_pending / data.total_sales * 100) + '%' }"
                     class="bg-amber-500 transition-all"
                     :title="`Chờ duyệt: ${data.sales_pending}`">
                </div>
                <div v-if="data.sales_cancelled > 0"
                     :style="{ width: (data.sales_cancelled / data.total_sales * 100) + '%' }"
                     class="bg-red-500 transition-all"
                     :title="`Đã hủy: ${data.sales_cancelled}`">
                </div>
              </div>
              <div class="flex items-center gap-4 mt-2 text-xs">
                <span class="text-green-600">✓ {{ data.sales_submitted }}</span>
                <span class="text-amber-600">⏳ {{ data.sales_pending }}</span>
                <span class="text-red-600">✗ {{ data.sales_cancelled }}</span>
              </div>
            </div>
          </div>
        </div>
      </div>

      <!-- Top Lists -->
      <div class="grid grid-cols-1 lg:grid-cols-2 gap-6">
        <!-- Top Suppliers -->
        <div class="bg-white rounded-xl p-6 shadow-sm border border-gray-100">
          <h3 class="text-lg font-semibold text-gray-800 mb-4">Top 5 nhà cung cấp (30 ngày)</h3>
          <div class="space-y-3">
            <div v-for="(supplier, index) in data.top_suppliers" :key="index"
                 class="flex items-center gap-4 p-3 rounded-lg border border-gray-100 hover:bg-gray-50 transition-colors">
              <div class="flex items-center justify-center w-8 h-8 rounded-full bg-orange-100 text-orange-600 font-bold text-sm">
                {{ index + 1 }}
              </div>
              <div class="flex-1 min-w-0">
                <p class="text-sm font-medium text-gray-800 truncate">{{ supplier.supplier }}</p>
                <p class="text-xs text-gray-500">{{ supplier.invoice_count }} hóa đơn</p>
              </div>
              <div class="text-right">
                <p class="text-sm font-semibold text-gray-800">{{ formatCurrency(supplier.total_value) }}</p>
              </div>
            </div>
            <div v-if="!data.top_suppliers || data.top_suppliers.length === 0" class="text-center py-8 text-gray-400">
              Chưa có dữ liệu
            </div>
          </div>
        </div>

        <!-- Top Customers -->
        <div class="bg-white rounded-xl p-6 shadow-sm border border-gray-100">
          <h3 class="text-lg font-semibold text-gray-800 mb-4">Top 5 khách hàng (30 ngày)</h3>
          <div class="space-y-3">
            <div v-for="(customer, index) in data.top_customers" :key="index"
                 class="flex items-center gap-4 p-3 rounded-lg border border-gray-100 hover:bg-gray-50 transition-colors">
              <div class="flex items-center justify-center w-8 h-8 rounded-full bg-green-100 text-green-600 font-bold text-sm">
                {{ index + 1 }}
              </div>
              <div class="flex-1 min-w-0">
                <p class="text-sm font-medium text-gray-800 truncate">{{ customer.customer }}</p>
                <p class="text-xs text-gray-500">{{ customer.invoice_count }} hóa đơn</p>
              </div>
              <div class="text-right">
                <p class="text-sm font-semibold text-gray-800">{{ formatCurrency(customer.total_value) }}</p>
              </div>
            </div>
            <div v-if="!data.top_customers || data.top_customers.length === 0" class="text-center py-8 text-gray-400">
              Chưa có dữ liệu
            </div>
          </div>
        </div>
      </div>

      <!-- Top Items -->
      <div class="grid grid-cols-1 lg:grid-cols-2 gap-6">
        <!-- Top Purchased Items -->
        <div class="bg-white rounded-xl p-6 shadow-sm border border-gray-100">
          <h3 class="text-lg font-semibold text-gray-800 mb-4">Top 5 sản phẩm mua nhiều nhất</h3>
          <div class="space-y-3">
            <div v-for="(item, index) in data.top_purchased_items" :key="index"
                 class="flex items-center gap-4 p-3 rounded-lg border border-gray-100">
              <div class="flex items-center justify-center w-8 h-8 rounded-full bg-purple-100 text-purple-600 font-bold text-sm">
                {{ index + 1 }}
              </div>
              <div class="flex-1 min-w-0">
                <p class="text-sm font-medium text-gray-800 truncate">{{ item.item_name }}</p>
                <p class="text-xs text-gray-500">{{ item.item_code }}</p>
              </div>
              <div class="text-right">
                <p class="text-sm font-semibold text-gray-800">{{ formatNumber(item.total_qty) }} {{ item.uom }}</p>
                <p class="text-xs text-gray-500">{{ formatCurrency(item.total_amount) }}</p>
              </div>
            </div>
            <div v-if="!data.top_purchased_items || data.top_purchased_items.length === 0" class="text-center py-8 text-gray-400">
              Chưa có dữ liệu
            </div>
          </div>
        </div>

        <!-- Top Sold Items -->
        <div class="bg-white rounded-xl p-6 shadow-sm border border-gray-100">
          <h3 class="text-lg font-semibold text-gray-800 mb-4">Top 5 sản phẩm bán nhiều nhất</h3>
          <div class="space-y-3">
            <div v-for="(item, index) in data.top_sold_items" :key="index"
                 class="flex items-center gap-4 p-3 rounded-lg border border-gray-100">
              <div class="flex items-center justify-center w-8 h-8 rounded-full bg-indigo-100 text-indigo-600 font-bold text-sm">
                {{ index + 1 }}
              </div>
              <div class="flex-1 min-w-0">
                <p class="text-sm font-medium text-gray-800 truncate">{{ item.item_name }}</p>
                <p class="text-xs text-gray-500">{{ item.item_code }}</p>
              </div>
              <div class="text-right">
                <p class="text-sm font-semibold text-gray-800">{{ formatNumber(item.total_qty) }} {{ item.uom }}</p>
                <p class="text-xs text-gray-500">{{ formatCurrency(item.total_amount) }}</p>
              </div>
            </div>
            <div v-if="!data.top_sold_items || data.top_sold_items.length === 0" class="text-center py-8 text-gray-400">
              Chưa có dữ liệu
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
  total_purchase: 0,
  purchase_pending: 0,
  purchase_submitted: 0,
  purchase_cancelled: 0,
  purchase_value_month: 0,
  total_sales: 0,
  sales_pending: 0,
  sales_submitted: 0,
  sales_cancelled: 0,
  sales_value_month: 0,
  gross_profit: 0,
  profit_margin: 0,
  purchase_sales_trend: [],
  top_suppliers: [],
  top_customers: [],
  top_purchased_items: [],
  top_sold_items: []
})

// Icons
const PurchaseIcon = {
  render: () => h('svg', { fill: 'none', stroke: 'currentColor', viewBox: '0 0 24 24' }, [
    h('path', { 'stroke-linecap': 'round', 'stroke-linejoin': 'round', 'stroke-width': '2',
      d: 'M3 3h2l.4 2M7 13h10l4-8H5.4M7 13L5.4 5M7 13l-2.293 2.293c-.63.63-.184 1.707.707 1.707H17m0 0a2 2 0 100 4 2 2 0 000-4zm-8 2a2 2 0 11-4 0 2 2 0 014 0z' })
  ])
}

const SalesIcon = {
  render: () => h('svg', { fill: 'none', stroke: 'currentColor', viewBox: '0 0 24 24' }, [
    h('path', { 'stroke-linecap': 'round', 'stroke-linejoin': 'round', 'stroke-width': '2',
      d: 'M17 9V7a2 2 0 00-2-2H5a2 2 0 00-2 2v6a2 2 0 002 2h2m2 4h10a2 2 0 002-2v-6a2 2 0 00-2-2H9a2 2 0 00-2 2v6a2 2 0 002 2zm7-5a2 2 0 11-4 0 2 2 0 014 0z' })
  ])
}

const TrendIcon = {
  render: () => h('svg', { fill: 'none', stroke: 'currentColor', viewBox: '0 0 24 24' }, [
    h('path', { 'stroke-linecap': 'round', 'stroke-linejoin': 'round', 'stroke-width': '2', d: 'M13 7h8m0 0v8m0-8l-8 8-4-4-6 6' })
  ])
}

const ClockIcon = {
  render: () => h('svg', { fill: 'none', stroke: 'currentColor', viewBox: '0 0 24 24' }, [
    h('path', { 'stroke-linecap': 'round', 'stroke-linejoin': 'round', 'stroke-width': '2',
      d: 'M12 8v4l3 3m6-3a9 9 0 11-18 0 9 9 0 0118 0z' })
  ])
}

// Chart data
const trendChartData = computed(() => {
  if (!data.value.purchase_sales_trend || data.value.purchase_sales_trend.length === 0) return []
  
  const trend = data.value.purchase_sales_trend
  const max = Math.max(...trend.map(d => Math.max(d.purchase_count, d.sales_count))) || 1
  
  return trend.map(d => ({
    ...d,
    purchaseHeight: (d.purchase_count / max) * 170,
    salesHeight: (d.sales_count / max) * 170
  }))
})

const maxTrend = computed(() => {
  if (!data.value.purchase_sales_trend || data.value.purchase_sales_trend.length === 0) return 10
  const max = Math.max(...data.value.purchase_sales_trend.map(d => Math.max(d.purchase_count, d.sales_count)))
  return max + 2
})

// Format functions
const formatNumber = (num) => {
  if (!num) return '0'
  return new Intl.NumberFormat('vi-VN').format(num)
}

const formatCurrency = (amount) => {
  if (!amount) return '0 ₫'
  if (amount >= 1000000000) {
    return (amount / 1000000000).toFixed(1) + ' tỷ'
  }
  if (amount >= 1000000) {
    return (amount / 1000000).toFixed(1) + ' tr'
  }
  return new Intl.NumberFormat('vi-VN', { style: 'currency', currency: 'VND' }).format(amount)
}

// Load data
const loadData = async () => {
  loading.value = true
  try {
    const response = await axios.get('/api/method/xuanhoa_app.api.get_sales_purchase_dashboard')
    if (response.data && response.data.message) {
      data.value = { ...data.value, ...response.data.message }
    }
  } catch (error) {
    console.error('Error loading sales purchase dashboard:', error)
  } finally {
    loading.value = false
  }
}

onMounted(() => {
  loadData()
})
</script>
