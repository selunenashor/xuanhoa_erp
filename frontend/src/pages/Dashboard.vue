<template>
  <div class="space-y-6">
    <!-- Welcome Section -->
    <div class="bg-gradient-to-r from-primary to-primary-light rounded-xl p-6 text-white">
      <h2 class="text-2xl font-bold mb-2">Xin chào, {{ userStore.fullName }}!</h2>
      <p class="text-white/80">Chào mừng bạn đến với hệ thống Quản lý Sản xuất</p>
    </div>

    <!-- KPI Cards -->
    <div class="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-4">
      <div v-for="kpi in kpiCards" :key="kpi.id" 
           class="bg-white rounded-xl p-5 shadow-sm border border-gray-100">
        <div class="flex items-start justify-between">
          <div>
            <p class="text-sm text-gray-500 mb-1">{{ kpi.label }}</p>
            <p class="text-2xl font-bold text-gray-800">{{ kpi.value }}</p>
            <p v-if="kpi.trend !== undefined" :class="['text-sm mt-1', kpi.trend >= 0 ? 'text-success' : 'text-error']">
              <span v-if="kpi.trend >= 0">↑</span>
              <span v-else>↓</span>
              {{ Math.abs(kpi.trend) }}% so với tuần trước
            </p>
          </div>
          <div :class="['w-12 h-12 rounded-lg flex items-center justify-center', kpi.bgColor]">
            <component :is="kpi.icon" :class="['w-6 h-6', kpi.iconColor]" />
          </div>
        </div>
      </div>
    </div>

    <!-- Quick Actions -->
    <div class="bg-white rounded-xl p-6 shadow-sm border border-gray-100">
      <h3 class="text-lg font-semibold text-gray-800 mb-4">Thao tác nhanh</h3>
      <div class="grid grid-cols-2 md:grid-cols-4 gap-4">
        <router-link 
          v-for="action in quickActions" 
          :key="action.path"
          :to="action.path"
          class="flex flex-col items-center gap-3 p-4 rounded-xl border-2 border-dashed border-gray-200 
                 hover:border-primary hover:bg-primary/5 transition-colors group"
        >
          <div class="w-12 h-12 rounded-xl bg-gray-100 group-hover:bg-primary/10 
                      flex items-center justify-center transition-colors">
            <component :is="action.icon" class="w-6 h-6 text-gray-500 group-hover:text-primary" />
          </div>
          <span class="text-sm font-medium text-gray-700 text-center">{{ action.label }}</span>
        </router-link>
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
        Chưa có hoạt động nào
      </div>
      
      <!-- Activities list -->
      <div v-else class="space-y-4">
        <div v-for="activity in recentActivities" :key="activity.id"
             class="flex items-start gap-4 p-3 rounded-lg hover:bg-gray-50 transition-colors">
          <div :class="['w-10 h-10 rounded-full flex items-center justify-center flex-shrink-0', getActivityBgColor(activity.type)]">
            <component :is="getActivityIcon(activity.type)" :class="['w-5 h-5', getActivityIconColor(activity.type)]" />
          </div>
          <div class="flex-1 min-w-0">
            <p class="text-sm text-gray-800 font-medium">{{ activity.title }}</p>
            <p class="text-xs text-gray-500 mt-0.5">{{ activity.description }}</p>
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
import { useUserStore } from '@/stores/user'
import { dashboardAPI } from '@/api'

const userStore = useUserStore()

// State
const loadingActivities = ref(false)
const recentActivities = ref([])
const kpiData = ref(null)

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

const ChartIcon = {
  render: () => h('svg', { fill: 'none', stroke: 'currentColor', viewBox: '0 0 24 24' }, [
    h('path', { 
      'stroke-linecap': 'round', 
      'stroke-linejoin': 'round', 
      'stroke-width': '2',
      d: 'M9 19v-6a2 2 0 00-2-2H5a2 2 0 00-2 2v6a2 2 0 002 2h2a2 2 0 002-2zm0 0V9a2 2 0 012-2h2a2 2 0 012 2v10m-6 0a2 2 0 002 2h2a2 2 0 002-2m0 0V5a2 2 0 012-2h2a2 2 0 012 2v14a2 2 0 01-2 2h-2a2 2 0 01-2-2z'
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
  
  // Tính tổng Work Orders đang chạy
  const woInProgress = data?.work_orders?.['In Process'] || 0
  const woNotStarted = data?.work_orders?.['Not Started'] || 0
  
  return [
    {
      id: 1,
      label: 'Lệnh SX đang chạy',
      value: woInProgress + woNotStarted,
      icon: ClipboardIcon,
      bgColor: 'bg-primary/10',
      iconColor: 'text-primary'
    },
    {
      id: 2,
      label: 'Giá trị tồn kho',
      value: formatNumber(Math.round((data?.stock_value || 0) / 1000)) + 'K',
      icon: BoxIcon,
      bgColor: 'bg-warning/10',
      iconColor: 'text-warning'
    },
    {
      id: 3,
      label: 'Nhập kho hôm nay',
      value: data?.receipts_today || 0,
      icon: PlusIcon,
      bgColor: 'bg-success/10',
      iconColor: 'text-success'
    },
    {
      id: 4,
      label: 'Xuất kho hôm nay',
      value: data?.issues_today || 0,
      icon: TruckIcon,
      bgColor: 'bg-info/10',
      iconColor: 'text-info'
    }
  ]
})

// Quick actions
const quickActions = [
  { path: '/stock/receipt', label: 'Nhập kho', icon: PlusIcon },
  { path: '/stock/issue', label: 'Xuất kho', icon: TruckIcon },
  { path: '/production/orders', label: 'Lệnh sản xuất', icon: ClipboardIcon },
  { path: '/', label: 'Báo cáo', icon: ChartIcon }
]

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
  } catch (error) {
    console.error('Error loading KPI data:', error)
  }
}

// Initialize
onMounted(() => {
  loadKPIData()
  loadRecentActivities()
})
</script>
