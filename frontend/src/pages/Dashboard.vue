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
            <p :class="['text-sm mt-1', kpi.trend > 0 ? 'text-success' : 'text-error']">
              <span v-if="kpi.trend > 0">↑</span>
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
      <h3 class="text-lg font-semibold text-gray-800 mb-4">Hoạt động gần đây</h3>
      <div class="space-y-4">
        <div v-for="activity in recentActivities" :key="activity.id"
             class="flex items-start gap-4 p-3 rounded-lg hover:bg-gray-50 transition-colors">
          <div :class="['w-10 h-10 rounded-full flex items-center justify-center flex-shrink-0', activity.bgColor]">
            <component :is="activity.icon" :class="['w-5 h-5', activity.iconColor]" />
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
import { h, computed } from 'vue'
import { useUserStore } from '@/stores/user'

const userStore = useUserStore()

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

// KPI Cards data
const kpiCards = computed(() => [
  {
    id: 1,
    label: 'Lệnh SX đang chạy',
    value: '12',
    trend: 8,
    icon: ClipboardIcon,
    bgColor: 'bg-primary/10',
    iconColor: 'text-primary'
  },
  {
    id: 2,
    label: 'Tồn kho NVL',
    value: '2,450',
    trend: -3,
    icon: BoxIcon,
    bgColor: 'bg-warning/10',
    iconColor: 'text-warning'
  },
  {
    id: 3,
    label: 'Xuất kho hôm nay',
    value: '156',
    trend: 12,
    icon: TruckIcon,
    bgColor: 'bg-success/10',
    iconColor: 'text-success'
  },
  {
    id: 4,
    label: 'Hiệu suất',
    value: '94%',
    trend: 5,
    icon: ChartIcon,
    bgColor: 'bg-info/10',
    iconColor: 'text-info'
  }
])

// Quick actions
const quickActions = [
  { path: '/stock/receipt', label: 'Nhập kho', icon: PlusIcon },
  { path: '/stock/issue', label: 'Xuất kho', icon: TruckIcon },
  { path: '/production/orders', label: 'Lệnh sản xuất', icon: ClipboardIcon },
  { path: '/', label: 'Báo cáo', icon: ChartIcon }
]

// Recent activities
const recentActivities = [
  {
    id: 1,
    title: 'Nhập kho IC Driver 500 cái',
    description: 'Từ NCC Điện tử ABC',
    time: '5 phút trước',
    user: 'Quản Lý Kho',
    userInitial: 'K',
    approver: 'Admin Hệ Thống',
    icon: BoxIcon,
    bgColor: 'bg-success/10',
    iconColor: 'text-success'
  },
  {
    id: 2,
    title: 'Hoàn thành LSX #WO-2024-0045',
    description: 'Đèn LED Bulb 9W - 1,000 cái',
    time: '15 phút trước',
    user: 'Quản Lý Sản Xuất',
    userInitial: 'S',
    approver: null,
    icon: CheckIcon,
    bgColor: 'bg-primary/10',
    iconColor: 'text-primary'
  },
  {
    id: 3,
    title: 'Xuất kho thành phẩm',
    description: 'Đơn hàng #SO-2024-0123',
    time: '1 giờ trước',
    user: 'Quản Lý Kho',
    userInitial: 'K',
    approver: 'Quản Lý Bán Hàng',
    icon: TruckIcon,
    bgColor: 'bg-info/10',
    iconColor: 'text-info'
  }
]
</script>
