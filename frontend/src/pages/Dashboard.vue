<template>
  <div class="space-y-6">
    <!-- Welcome Section -->
    <div class="bg-gradient-to-r from-primary to-primary-light rounded-xl p-6 text-white">
      <h2 class="text-2xl font-bold mb-2">Xin chào, {{ userStore.fullName }}!</h2>
      <p class="text-white/80">Chào mừng bạn đến với hệ thống Quản lý Sản xuất Xuân Hòa</p>
    </div>

    <!-- KPI Cards -->
    <div class="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-4">
      <div v-for="kpi in kpiCards" :key="kpi.id" 
           class="bg-white rounded-xl p-5 shadow-sm border border-gray-100 hover:shadow-md transition-shadow">
        <div class="flex items-start justify-between">
          <div>
            <p class="text-sm text-gray-500 mb-1">{{ kpi.label }}</p>
            <p class="text-2xl font-bold text-gray-800">{{ kpi.value }}</p>
            <p v-if="kpi.subLabel" class="text-xs text-gray-400 mt-1">{{ kpi.subLabel }}</p>
          </div>
          <div :class="['w-12 h-12 rounded-lg flex items-center justify-center', kpi.bgColor]">
            <component :is="kpi.icon" :class="['w-6 h-6', kpi.iconColor]" />
          </div>
        </div>
      </div>
    </div>

    <!-- Smart Insights -->
    <div v-if="insights.length > 0" class="bg-gradient-to-r from-indigo-50 to-blue-50 rounded-xl p-6 border border-indigo-100">
      <div class="flex items-center gap-2 mb-4">
        <LightBulbIcon class="w-6 h-6 text-indigo-600" />
        <h3 class="text-lg font-semibold text-gray-800">Gợi ý thông minh</h3>
      </div>
      <div class="space-y-3">
        <div v-for="insight in insights" :key="insight.id"
             :class="['flex items-start gap-3 p-4 rounded-lg bg-white border transition-all hover:shadow-sm', 
                      insight.priority === 'high' ? 'border-red-200' : 
                      insight.priority === 'medium' ? 'border-amber-200' : 'border-blue-200']">
          <div :class="['w-8 h-8 rounded-full flex items-center justify-center flex-shrink-0',
                        insight.priority === 'high' ? 'bg-red-100' : 
                        insight.priority === 'medium' ? 'bg-amber-100' : 'bg-blue-100']">
            <component :is="insight.icon" :class="['w-4 h-4',
                                                    insight.priority === 'high' ? 'text-red-600' : 
                                                    insight.priority === 'medium' ? 'text-amber-600' : 'text-blue-600']" />
          </div>
          <div class="flex-1">
            <p class="text-sm font-medium text-gray-800">{{ insight.message }}</p>
            <p v-if="insight.detail" class="text-xs text-gray-500 mt-1">{{ insight.detail }}</p>
          </div>
          <button v-if="insight.action"
                  @click="handleInsightAction(insight)"
                  class="text-xs font-medium text-indigo-600 hover:text-indigo-700 whitespace-nowrap">
            {{ insight.actionLabel }}
          </button>
        </div>
      </div>
    </div>

    <!-- Charts Section -->
    <div class="grid grid-cols-1 lg:grid-cols-2 gap-6">
      <!-- Stock Movement Chart -->
      <div class="bg-white rounded-xl p-6 shadow-sm border border-gray-100">
        <h3 class="text-lg font-semibold text-gray-800 mb-4">Biến động kho 7 ngày</h3>
        <div class="h-64">
          <svg class="w-full h-full" viewBox="0 0 400 200">
            <!-- Y-axis labels -->
            <text x="10" y="20" class="text-xs fill-gray-400">{{ maxStockValue }}</text>
            <text x="10" y="110" class="text-xs fill-gray-400">{{ Math.round(maxStockValue/2) }}</text>
            <text x="10" y="195" class="text-xs fill-gray-400">0</text>
            
            <!-- Grid lines -->
            <line x1="40" y1="20" x2="390" y2="20" stroke="#E5E7EB" stroke-width="1" stroke-dasharray="2,2"/>
            <line x1="40" y1="110" x2="390" y2="110" stroke="#E5E7EB" stroke-width="1" stroke-dasharray="2,2"/>
            <line x1="40" y1="190" x2="390" y2="190" stroke="#E5E7EB" stroke-width="1"/>
            
            <!-- Receipt bars -->
            <rect v-for="(point, i) in chartData" :key="'receipt-'+i"
                  :x="60 + i * 50" 
                  :y="190 - point.receiptHeight" 
                  :width="18" 
                  :height="point.receiptHeight"
                  :class="'fill-green-400 hover:fill-green-500 transition-colors'"
                  rx="2">
              <title>Nhập: {{ point.receipts }} phiếu</title>
            </rect>
            
            <!-- Issue bars -->
            <rect v-for="(point, i) in chartData" :key="'issue-'+i"
                  :x="80 + i * 50" 
                  :y="190 - point.issueHeight" 
                  :width="18" 
                  :height="point.issueHeight"
                  :class="'fill-blue-400 hover:fill-blue-500 transition-colors'"
                  rx="2">
              <title>Xuất: {{ point.issues }} phiếu</title>
            </rect>
            
            <!-- X-axis labels -->
            <text v-for="(point, i) in chartData" :key="'label-'+i"
                  :x="70 + i * 50" 
                  y="205" 
                  class="text-xs fill-gray-500 text-anchor-middle">
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

      <!-- Work Order Status Chart -->
      <div class="bg-white rounded-xl p-6 shadow-sm border border-gray-100">
        <h3 class="text-lg font-semibold text-gray-800 mb-4">Tình trạng lệnh sản xuất</h3>
        <div class="h-64 flex items-center justify-center">
          <svg class="w-48 h-48" viewBox="0 0 200 200">
            <!-- Background circle -->
            <circle cx="100" cy="100" r="80" fill="none" stroke="#F3F4F6" stroke-width="20"/>
            
            <!-- Progress arcs -->
            <circle v-if="workOrderStats.total > 0"
                    cx="100" cy="100" r="80" 
                    fill="none" 
                    :stroke="'#10B981'" 
                    stroke-width="20"
                    :stroke-dasharray="`${workOrderStats.completedPercent * 5.024} 502.4`"
                    transform="rotate(-90 100 100)"
                    class="transition-all duration-500"/>
            
            <circle v-if="workOrderStats.total > 0"
                    cx="100" cy="100" r="80" 
                    fill="none" 
                    :stroke="'#F59E0B'" 
                    stroke-width="20"
                    :stroke-dasharray="`${workOrderStats.inProcessPercent * 5.024} 502.4`"
                    :stroke-dashoffset="`${-workOrderStats.completedPercent * 5.024}`"
                    transform="rotate(-90 100 100)"
                    class="transition-all duration-500"/>
            
            <!-- Center text -->
            <text x="100" y="95" text-anchor="middle" class="text-2xl font-bold fill-gray-800">
              {{ workOrderStats.total }}
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
            <span class="text-sm font-medium text-gray-800">{{ workOrderStats.completed }}</span>
          </div>
          <div class="flex items-center justify-between">
            <div class="flex items-center gap-2">
              <div class="w-3 h-3 rounded-full bg-amber-500"></div>
              <span class="text-sm text-gray-600">Đang thực hiện</span>
            </div>
            <span class="text-sm font-medium text-gray-800">{{ workOrderStats.inProcess }}</span>
          </div>
          <div class="flex items-center justify-between">
            <div class="flex items-center gap-2">
              <div class="w-3 h-3 rounded-full bg-gray-300"></div>
              <span class="text-sm text-gray-600">Chưa bắt đầu</span>
            </div>
            <span class="text-sm font-medium text-gray-800">{{ workOrderStats.notStarted }}</span>
          </div>
        </div>
      </div>
    </div>

    <!-- Quick Actions Grid -->
    <div class="grid grid-cols-1 lg:grid-cols-3 gap-6">
      <!-- Kho hàng -->
      <div class="bg-white rounded-xl p-6 shadow-sm border border-gray-100">
        <div class="flex items-center gap-2 mb-4">
          <div class="w-8 h-8 rounded-lg bg-blue-100 flex items-center justify-center">
            <BoxIcon class="w-5 h-5 text-blue-600" />
          </div>
          <h3 class="text-lg font-semibold text-gray-800">Kho hàng</h3>
        </div>
        <div class="space-y-2">
          <router-link 
            to="/master/items"
            class="flex items-center gap-3 p-3 rounded-lg border border-gray-200 hover:border-primary hover:bg-primary/5 transition-colors group"
          >
            <BoxIcon class="w-5 h-5 text-teal-500" />
            <span class="text-sm font-medium text-gray-700 group-hover:text-primary">Quản lý sản phẩm</span>
          </router-link>
          <router-link 
            to="/stock/warehouses"
            class="flex items-center gap-3 p-3 rounded-lg border border-gray-200 hover:border-primary hover:bg-primary/5 transition-colors group"
          >
            <WarehouseIcon class="w-5 h-5 text-gray-500" />
            <span class="text-sm font-medium text-gray-700 group-hover:text-primary">Quản lý kho</span>
          </router-link>
          <router-link 
            to="/stock/receipt"
            class="flex items-center gap-3 p-3 rounded-lg border border-gray-200 hover:border-primary hover:bg-primary/5 transition-colors group"
          >
            <PlusIcon class="w-5 h-5 text-success" />
            <span class="text-sm font-medium text-gray-700 group-hover:text-primary">Tạo phiếu nhập kho</span>
          </router-link>
          <router-link 
            to="/stock/issue"
            class="flex items-center gap-3 p-3 rounded-lg border border-gray-200 hover:border-primary hover:bg-primary/5 transition-colors group"
          >
            <TruckIcon class="w-5 h-5 text-info" />
            <span class="text-sm font-medium text-gray-700 group-hover:text-primary">Tạo phiếu xuất kho</span>
          </router-link>
          <router-link 
            to="/stock/entries"
            class="flex items-center gap-3 p-3 rounded-lg border border-gray-200 hover:border-primary hover:bg-primary/5 transition-colors group"
          >
            <ClipboardIcon class="w-5 h-5 text-gray-500" />
            <span class="text-sm font-medium text-gray-700 group-hover:text-primary">Xem danh sách phiếu</span>
          </router-link>
        </div>
      </div>

      <!-- Sản xuất -->
      <div class="bg-white rounded-xl p-6 shadow-sm border border-gray-100">
        <div class="flex items-center gap-2 mb-4">
          <div class="w-8 h-8 rounded-lg bg-amber-100 flex items-center justify-center">
            <ManufactureIcon class="w-5 h-5 text-amber-600" />
          </div>
          <h3 class="text-lg font-semibold text-gray-800">Sản xuất</h3>
        </div>
        <div class="space-y-2">
          <router-link 
            to="/production/boms"
            class="flex items-center gap-3 p-3 rounded-lg border border-gray-200 hover:border-primary hover:bg-primary/5 transition-colors group"
          >
            <BOMIcon class="w-5 h-5 text-purple-500" />
            <span class="text-sm font-medium text-gray-700 group-hover:text-primary">Định mức nguyên vật liệu</span>
          </router-link>
          <router-link 
            to="/production/orders"
            class="flex items-center gap-3 p-3 rounded-lg border border-gray-200 hover:border-primary hover:bg-primary/5 transition-colors group"
          >
            <ClipboardIcon class="w-5 h-5 text-amber-500" />
            <span class="text-sm font-medium text-gray-700 group-hover:text-primary">Lệnh sản xuất</span>
          </router-link>
        </div>
      </div>
    </div>

    <!-- Recent Activity -->
    <div class="bg-white rounded-xl p-6 shadow-sm border border-gray-100">
      <div class="flex justify-between items-center mb-4">
        <h3 class="text-lg font-semibold text-gray-800">Hoạt động gần đây</h3>
        <button 
          @click="loadRecentActivities"
          class="text-sm text-primary hover:text-primary-dark flex items-center gap-1"
        >
          <RefreshIcon class="w-4 h-4" />
          Làm mới
        </button>
      </div>
      
      <!-- Loading state -->
      <div v-if="loadingActivities" class="flex justify-center py-8">
        <svg class="animate-spin h-8 w-8 text-primary" xmlns="http://www.w3.org/2000/svg" fill="none" viewBox="0 0 24 24">
          <circle class="opacity-25" cx="12" cy="12" r="10" stroke="currentColor" stroke-width="4"></circle>
          <path class="opacity-75" fill="currentColor" d="M4 12a8 8 0 018-8V0C5.373 0 0 5.373 0 12h4zm2 5.291A7.962 7.962 0 014 12H0c0 3.042 1.135 5.824 3 7.938l3-2.647z"></path>
        </svg>
      </div>
      
      <!-- Empty state -->
      <div v-else-if="recentActivities.length === 0" class="text-center py-8 text-gray-500">
        <ClipboardIcon class="w-12 h-12 mx-auto text-gray-300 mb-2" />
        <p>Chưa có hoạt động nào</p>
      </div>
      
      <!-- Activities list -->
      <div v-else class="space-y-3">
        <div v-for="activity in recentActivities" :key="activity.id"
             @click="goToActivityDetail(activity)"
             :class="[
               'flex items-start gap-4 p-3 rounded-lg transition-colors',
               activity.doctype === 'Stock Entry' ? 'cursor-pointer hover:bg-gray-100' : 'hover:bg-gray-50'
             ]">
          <div :class="['w-10 h-10 rounded-full flex items-center justify-center flex-shrink-0', getActivityBgColor(activity.type)]">
            <component :is="getActivityIcon(activity.type)" :class="['w-5 h-5', getActivityIconColor(activity.type)]" />
          </div>
          <div class="flex-1 min-w-0">
            <p class="text-sm text-gray-800 font-medium">{{ activity.title }}</p>
            <p class="text-xs text-gray-500 mt-0.5">{{ translateUOMInText(activity.description) }}</p>
            <div class="flex items-center gap-2 mt-1">
              <div class="w-5 h-5 rounded-full bg-gray-200 flex items-center justify-center">
                <span class="text-[10px] font-medium text-gray-600">{{ activity.userInitial }}</span>
              </div>
              <span class="text-xs text-primary font-medium">{{ activity.user }}</span>
              <span v-if="activity.approver" class="text-xs text-gray-400">• Duyệt: {{ activity.approver }}</span>
            </div>
          </div>
          <span class="text-xs text-gray-400 flex-shrink-0">{{ activity.time }}</span>
        </div>
      </div>
    </div>
  </div>
</template>

<script setup>
import { h, ref, computed, onMounted } from 'vue'
import { useRouter } from 'vue-router'
import { useUserStore } from '@/stores/user'
import { dashboardAPI } from '@/api'

const router = useRouter()
const userStore = useUserStore()

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
}

// Translate UOM in text
const translateUOMInText = (text) => {
  if (!text) return text
  let result = text
  for (const [eng, viet] of Object.entries(UOM_TRANSLATIONS)) {
    const regex = new RegExp(`(\\d+\\.?\\d*)\\s*${eng}\\b`, 'g')
    result = result.replace(regex, `$1 ${viet}`)
  }
  return result
}

// Navigate to activity detail
const goToActivityDetail = (activity) => {
  if (activity.doctype === 'Stock Entry' && activity.docname) {
    router.push(`/stock/entries/${activity.docname}`)
  }
}

// State
const loadingActivities = ref(false)
const recentActivities = ref([])
const kpiData = ref(null)
const insights = ref([])
const chartData = ref([])
const maxStockValue = ref(100)

// Work Order Statistics
const workOrderStats = computed(() => {
  const data = kpiData.value
  const completed = data?.work_orders?.['Completed'] || 0
  const inProcess = data?.work_orders?.['In Process'] || 0
  const notStarted = data?.work_orders?.['Not Started'] || 0
  const total = completed + inProcess + notStarted
  
  return {
    completed,
    inProcess,
    notStarted,
    total,
    completedPercent: total > 0 ? (completed / total) * 100 : 0,
    inProcessPercent: total > 0 ? (inProcess / total) * 100 : 0,
    notStartedPercent: total > 0 ? (notStarted / total) * 100 : 0
  }
})

// Icon components
const BoxIcon = {
  render: () => h('svg', { fill: 'none', stroke: 'currentColor', viewBox: '0 0 24 24' }, [
    h('path', { 
      'stroke-linecap': 'round', 
      'stroke-linejoin': 'round', 
      'stroke-width': '2',
      d: 'M20 7l-8-4-8 4m16 0l-8 4m8-4v10l-8 4m0-10L4 7m8 4v10M4 7v10l8 4'
    })
  ])
}

const ClipboardIcon = {
  render: () => h('svg', { fill: 'none', stroke: 'currentColor', viewBox: '0 0 24 24' }, [
    h('path', { 
      'stroke-linecap': 'round', 
      'stroke-linejoin': 'round', 
      'stroke-width': '2',
      d: 'M9 5H7a2 2 0 00-2 2v12a2 2 0 002 2h10a2 2 0 002-2V7a2 2 0 00-2-2h-2M9 5a2 2 0 002 2h2a2 2 0 002-2M9 5a2 2 0 012-2h2a2 2 0 012 2m-6 9l2 2 4-4'
    })
  ])
}

const TruckIcon = {
  render: () => h('svg', { fill: 'none', stroke: 'currentColor', viewBox: '0 0 24 24' }, [
    h('path', { 
      'stroke-linecap': 'round', 
      'stroke-linejoin': 'round', 
      'stroke-width': '2',
      d: 'M13 16V6a1 1 0 00-1-1H4a1 1 0 00-1 1v10a1 1 0 001 1h1m8-1a1 1 0 01-1 1H9m4-1V8a1 1 0 011-1h2.586a1 1 0 01.707.293l3.414 3.414a1 1 0 01.293.707V16a1 1 0 01-1 1h-1m-6-1a1 1 0 001 1h1M5 17a2 2 0 104 0m-4 0a2 2 0 114 0m6 0a2 2 0 104 0m-4 0a2 2 0 114 0'
    })
  ])
}

const ManufactureIcon = {
  render: () => h('svg', { fill: 'none', stroke: 'currentColor', viewBox: '0 0 24 24' }, [
    h('path', { 
      'stroke-linecap': 'round', 
      'stroke-linejoin': 'round', 
      'stroke-width': '2',
      d: 'M19.428 15.428a2 2 0 00-1.022-.547l-2.387-.477a6 6 0 00-3.86.517l-.318.158a6 6 0 01-3.86.517L6.05 15.21a2 2 0 00-1.806.547M8 4h8l-1 1v5.172a2 2 0 00.586 1.414l5 5c1.26 1.26.367 3.414-1.415 3.414H4.828c-1.782 0-2.674-2.154-1.414-3.414l5-5A2 2 0 009 10.172V5L8 4z'
    })
  ])
}

const PlusIcon = {
  render: () => h('svg', { fill: 'none', stroke: 'currentColor', viewBox: '0 0 24 24' }, [
    h('path', { 
      'stroke-linecap': 'round', 
      'stroke-linejoin': 'round', 
      'stroke-width': '2',
      d: 'M12 4v16m8-8H4'
    })
  ])
}

const CheckIcon = {
  render: () => h('svg', { fill: 'none', stroke: 'currentColor', viewBox: '0 0 24 24' }, [
    h('path', { 
      'stroke-linecap': 'round', 
      'stroke-linejoin': 'round', 
      'stroke-width': '2',
      d: 'M5 13l4 4L19 7'
    })
  ])
}

const RefreshIcon = {
  render: () => h('svg', { fill: 'none', stroke: 'currentColor', viewBox: '0 0 24 24' }, [
    h('path', { 
      'stroke-linecap': 'round', 
      'stroke-linejoin': 'round', 
      'stroke-width': '2',
      d: 'M4 4v5h.582m15.356 2A8.001 8.001 0 004.582 9m0 0H9m11 11v-5h-.581m0 0a8.003 8.003 0 01-15.357-2m15.357 2H15'
    })
  ])
}

const WarehouseIcon = {
  render: () => h('svg', { fill: 'none', stroke: 'currentColor', viewBox: '0 0 24 24' }, [
    h('path', { 
      'stroke-linecap': 'round', 
      'stroke-linejoin': 'round', 
      'stroke-width': '2',
      d: 'M19 21V5a2 2 0 00-2-2H7a2 2 0 00-2 2v16m14 0h2m-2 0h-5m-9 0H3m2 0h5M9 7h1m-1 4h1m4-4h1m-1 4h1m-5 10v-5a1 1 0 011-1h2a1 1 0 011 1v5m-4 0h4'
    })
  ])
}

const BOMIcon = {
  render: () => h('svg', { fill: 'none', stroke: 'currentColor', viewBox: '0 0 24 24' }, [
    h('path', { 
      'stroke-linecap': 'round', 
      'stroke-linejoin': 'round', 
      'stroke-width': '2',
      d: 'M9 5H7a2 2 0 00-2 2v12a2 2 0 002 2h10a2 2 0 002-2V7a2 2 0 00-2-2h-2M9 5a2 2 0 002 2h2a2 2 0 002-2M9 5a2 2 0 012-2h2a2 2 0 012 2m-6 9l2 2 4-4'
    })
  ])
}

const LightBulbIcon = {
  render: () => h('svg', { fill: 'none', stroke: 'currentColor', viewBox: '0 0 24 24' }, [
    h('path', { 
      'stroke-linecap': 'round', 
      'stroke-linejoin': 'round', 
      'stroke-width': '2',
      d: 'M9.663 17h4.673M12 3v1m6.364 1.636l-.707.707M21 12h-1M4 12H3m3.343-5.657l-.707-.707m2.828 9.9a5 5 0 117.072 0l-.548.547A3.374 3.374 0 0014 18.469V19a2 2 0 11-4 0v-.531c0-.895-.356-1.754-.988-2.386l-.548-.547z'
    })
  ])
}

const AlertIcon = {
  render: () => h('svg', { fill: 'none', stroke: 'currentColor', viewBox: '0 0 24 24' }, [
    h('path', { 
      'stroke-linecap': 'round', 
      'stroke-linejoin': 'round', 
      'stroke-width': '2',
      d: 'M12 9v2m0 4h.01m-6.938 4h13.856c1.54 0 2.502-1.667 1.732-3L13.732 4c-.77-1.333-2.694-1.333-3.464 0L3.34 16c-.77 1.333.192 3 1.732 3z'
    })
  ])
}

const TrendIcon = {
  render: () => h('svg', { fill: 'none', stroke: 'currentColor', viewBox: '0 0 24 24' }, [
    h('path', { 
      'stroke-linecap': 'round', 
      'stroke-linejoin': 'round', 
      'stroke-width': '2',
      d: 'M13 7h8m0 0v8m0-8l-8 8-4-4-6 6'
    })
  ])
}

// Helper functions for activity styling
const getActivityIcon = (type) => {
  const icons = {
    receipt: BoxIcon,
    issue: TruckIcon,
    manufacture: CheckIcon,
    transfer: ClipboardIcon
  }
  return icons[type] || BoxIcon
}

const getActivityBgColor = (type) => {
  const colors = {
    receipt: 'bg-success/10',
    issue: 'bg-info/10',
    manufacture: 'bg-primary/10',
    transfer: 'bg-warning/10'
  }
  return colors[type] || 'bg-gray-100'
}

const getActivityIconColor = (type) => {
  const colors = {
    receipt: 'text-success',
    issue: 'text-info',
    manufacture: 'text-primary',
    transfer: 'text-warning'
  }
  return colors[type] || 'text-gray-500'
}

// Format number with Vietnamese locale
const formatNumber = (num) => {
  if (!num) return '0'
  return new Intl.NumberFormat('vi-VN').format(num)
}

// KPI Cards data
const kpiCards = computed(() => {
  const data = kpiData.value
  
  const woInProgress = data?.work_orders?.['In Process'] || 0
  const woNotStarted = data?.work_orders?.['Not Started'] || 0
  const woCompleted = data?.work_orders?.['Completed'] || 0
  
  return [
    {
      id: 1,
      label: 'Lệnh SX chưa hoàn thành',
      value: woInProgress + woNotStarted,
      subLabel: woCompleted > 0 ? `${woCompleted} đã hoàn thành` : null,
      icon: ManufactureIcon,
      bgColor: 'bg-amber-100',
      iconColor: 'text-amber-600'
    },
    {
      id: 2,
      label: 'Giá trị tồn kho',
      value: formatNumber(Math.round((data?.stock_value || 0) / 1000000)) + ' tr',
      subLabel: 'Tổng giá trị hàng tồn',
      icon: BoxIcon,
      bgColor: 'bg-teal-100',
      iconColor: 'text-teal-600'
    },
    {
      id: 3,
      label: 'Nhập kho hôm nay',
      value: data?.receipts_today || 0,
      subLabel: 'Phiếu nhập',
      icon: PlusIcon,
      bgColor: 'bg-green-100',
      iconColor: 'text-green-600'
    },
    {
      id: 4,
      label: 'Xuất kho hôm nay',
      value: data?.issues_today || 0,
      subLabel: 'Phiếu xuất',
      icon: TruckIcon,
      bgColor: 'bg-blue-100',
      iconColor: 'text-blue-600'
    }
  ]
})

// Load recent activities
const loadRecentActivities = async () => {
  loadingActivities.value = true
  try {
    const activities = await dashboardAPI.getRecentActivities(10)
    recentActivities.value = activities || []
  } catch (error) {
    console.error('Error loading recent activities:', error)
    recentActivities.value = []
  } finally {
    loadingActivities.value = false
  }
}

// Load KPI data
const loadKPIData = async () => {
  try {
    kpiData.value = await dashboardAPI.getKPI()
    generateInsights()
    generateChartData()
  } catch (error) {
    console.error('Error loading KPI data:', error)
  }
}

// Generate smart insights
const generateInsights = () => {
  const data = kpiData.value
  if (!data) return
  
  const newInsights = []
  
  // Low stock alert
  if (data.low_stock_items && data.low_stock_items > 0) {
    newInsights.push({
      id: 'low-stock',
      icon: AlertIcon,
      priority: 'high',
      message: `Có ${data.low_stock_items} sản phẩm sắp hết hàng`,
      detail: 'Cần nhập kho để đảm bảo sản xuất liên tục',
      action: 'view-items',
      actionLabel: 'Xem chi tiết'
    })
  }
  
  // Work order trend
  const woInProgress = data?.work_orders?.['In Process'] || 0
  const woNotStarted = data?.work_orders?.['Not Started'] || 0
  if (woInProgress + woNotStarted > 5) {
    newInsights.push({
      id: 'wo-backlog',
      icon: TrendIcon,
      priority: 'medium',
      message: `${woInProgress + woNotStarted} lệnh sản xuất đang chờ xử lý`,
      detail: 'Cân nhắc tăng năng lực sản xuất hoặc ưu tiên các lệnh quan trọng',
      action: 'view-orders',
      actionLabel: 'Quản lý lệnh'
    })
  }
  
  // Stock movement trend
  const receiptsToday = data?.receipts_today || 0
  const issuesYesterday = data?.issues_yesterday || 0
  if (receiptsToday > issuesYesterday * 1.5) {
    newInsights.push({
      id: 'stock-increase',
      icon: TrendIcon,
      priority: 'low',
      message: 'Lượng hàng nhập kho tăng đột biến',
      detail: `${receiptsToday} phiếu nhập hôm nay, tăng so với ngày hôm qua`,
      action: null,
      actionLabel: null
    })
  }
  
  // Completed work orders
  const woCompleted = data?.work_orders?.['Completed'] || 0
  if (woCompleted > 0) {
    newInsights.push({
      id: 'wo-completed',
      icon: CheckIcon,
      priority: 'low',
      message: `${woCompleted} lệnh sản xuất đã hoàn thành`,
      detail: 'Kiểm tra và xác nhận chất lượng sản phẩm',
      action: 'view-completed',
      actionLabel: 'Xem lệnh'
    })
  }
  
  insights.value = newInsights
}

// Generate chart data (last 7 days)
const generateChartData = () => {
  const data = kpiData.value
  if (!data?.stock_movement) {
    // Generate mock data for demo
    const days = ['CN', 'T2', 'T3', 'T4', 'T5', 'T6', 'T7']
    const mockData = days.map((day, i) => ({
      day,
      receipts: Math.floor(Math.random() * 10) + 2,
      issues: Math.floor(Math.random() * 8) + 1
    }))
    
    const max = Math.max(...mockData.map(d => Math.max(d.receipts, d.issues)))
    maxStockValue.value = max + 2
    
    chartData.value = mockData.map(d => ({
      ...d,
      receiptHeight: (d.receipts / maxStockValue.value) * 170,
      issueHeight: (d.issues / maxStockValue.value) * 170
    }))
  } else {
    // Use real data from API
    const movement = data.stock_movement
    const max = Math.max(...movement.map(d => Math.max(d.receipts, d.issues)))
    maxStockValue.value = max + 2
    
    chartData.value = movement.map(d => ({
      ...d,
      receiptHeight: (d.receipts / maxStockValue.value) * 170,
      issueHeight: (d.issues / maxStockValue.value) * 170
    }))
  }
}

// Handle insight actions
const handleInsightAction = (insight) => {
  switch (insight.action) {
    case 'view-items':
      router.push('/master/items')
      break
    case 'view-orders':
      router.push('/production/orders')
      break
    case 'view-completed':
      router.push('/production/orders?status=Completed')
      break
  }
}

// Initialize
onMounted(() => {
  loadKPIData()
  loadRecentActivities()
})
</script>
