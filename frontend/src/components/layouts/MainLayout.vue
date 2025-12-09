<template>
  <div class="h-screen flex bg-gray-50 overflow-hidden">
    <!-- Sidebar -->
    <aside 
      :class="[
        'w-64 bg-primary flex flex-col h-screen shrink-0',
        'fixed inset-y-0 left-0 z-30 transform transition-transform duration-300 ease-in-out',
        'lg:static lg:translate-x-0',
        isSidebarOpen ? 'translate-x-0' : '-translate-x-full'
      ]"
    >
      <!-- Logo -->
      <div class="h-16 flex items-center justify-center border-b border-white/10 flex-shrink-0">
        <div class="flex items-center gap-3">
          <div class="w-10 h-10 bg-white/10 rounded-lg flex items-center justify-center">
            <svg class="w-6 h-6 text-secondary" fill="none" stroke="currentColor" viewBox="0 0 24 24">
              <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" 
                    d="M13 10V3L4 14h7v7l9-11h-7z" />
            </svg>
          </div>
          <span class="text-white font-semibold text-lg">Manufacturing</span>
        </div>
      </div>

      <!-- Navigation -->
      <nav class="p-4 flex-1 overflow-y-auto">
        <!-- Menu sections with dividers -->
        <template v-for="(section, sectionIndex) in menuSections" :key="sectionIndex">
          <!-- Section divider (except first) -->
          <div v-if="sectionIndex > 0" class="my-3 border-t border-white/10"></div>
          
          <!-- Section label (optional) -->
          <div v-if="section.label" class="px-4 py-2 text-xs font-semibold text-white/40 uppercase tracking-wider">
            {{ section.label }}
          </div>
          
          <!-- Section items -->
          <div class="space-y-1">
            <router-link
              v-for="item in section.items"
              :key="item.path"
              :to="item.path"
              custom
              v-slot="{ isExactActive, href, navigate }"
            >
              <a
                :href="href"
                @click="navigate"
                :class="[
                  'flex items-center gap-3 px-4 py-2.5 rounded-lg transition-colors',
                  isExactActive 
                    ? 'bg-white/15 text-white' 
                    : 'text-white/70 hover:bg-white/10 hover:text-white'
                ]"
              >
                <component :is="item.icon" class="w-5 h-5" />
                <span class="font-medium text-sm">{{ item.label }}</span>
              </a>
            </router-link>
          </div>
        </template>
      </nav>

      <!-- User Info (Bottom) -->
      <div class="p-4 border-t border-white/10 flex-shrink-0">
        <div class="flex items-center gap-3">
          <div class="w-10 h-10 bg-white/10 rounded-full flex items-center justify-center">
            <span class="text-white font-medium">{{ userInitial }}</span>
          </div>
          <div class="flex-1 min-w-0">
            <p class="text-white text-sm font-medium truncate">{{ userStore.fullName }}</p>
            <p class="text-white/50 text-xs truncate">{{ userRole }}</p>
          </div>
          <button 
            @click="handleLogout"
            class="p-2 text-white/50 hover:text-white hover:bg-white/10 rounded-lg transition-colors"
            title="Đăng xuất"
          >
            <svg class="w-5 h-5" fill="none" stroke="currentColor" viewBox="0 0 24 24">
              <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" 
                    d="M17 16l4-4m0 0l-4-4m4 4H7m6 4v1a3 3 0 01-3 3H6a3 3 0 01-3-3V7a3 3 0 013-3h4a3 3 0 013 3v1" />
            </svg>
          </button>
        </div>
      </div>
    </aside>

    <!-- Overlay (mobile) -->
    <div 
      v-if="isSidebarOpen"
      @click="isSidebarOpen = false"
      class="fixed inset-0 bg-black/50 z-20 lg:hidden"
    ></div>

    <!-- Main Content -->
    <div class="flex-1 flex flex-col h-screen overflow-hidden">
      <!-- Top Header -->
      <header class="h-16 bg-white border-b border-gray-200 flex items-center px-4 lg:px-6 sticky top-0 z-10">
        <!-- Mobile Menu Button -->
        <button 
          @click="isSidebarOpen = !isSidebarOpen"
          class="p-2 text-gray-500 hover:text-gray-700 hover:bg-gray-100 rounded-lg lg:hidden"
        >
          <svg class="w-6 h-6" fill="none" stroke="currentColor" viewBox="0 0 24 24">
            <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M4 6h16M4 12h16M4 18h16" />
          </svg>
        </button>

        <!-- Page Title -->
        <h1 class="text-lg font-semibold text-gray-800 ml-2 lg:ml-0">
          {{ pageTitle }}
        </h1>

        <!-- Spacer -->
        <div class="flex-1"></div>
      </header>

      <!-- Page Content -->
      <main class="flex-1 p-4 lg:p-6 overflow-y-auto">
        <router-view />
      </main>
    </div>
  </div>
</template>

<script setup>
import { ref, computed, h } from 'vue'
import { useRoute, useRouter } from 'vue-router'
import { useUserStore } from '@/stores/user'

const route = useRoute()
const router = useRouter()
const userStore = useUserStore()

// Sidebar state
const isSidebarOpen = ref(false)

// Computed
const pageTitle = computed(() => route.meta?.title || 'Trang chủ')

const userInitial = computed(() => {
  const name = userStore.fullName
  return name ? name.charAt(0).toUpperCase() : 'U'
})

const userRole = computed(() => {
  if (userStore.isAdmin) return 'Quản trị viên'
  return 'Người dùng'
})

// Menu Items with inline SVG icons as render functions
// Icons
const HomeIcon = {
  render: () => h('svg', { fill: 'none', stroke: 'currentColor', viewBox: '0 0 24 24' }, [
    h('path', { 
      'stroke-linecap': 'round', 
      'stroke-linejoin': 'round', 
      'stroke-width': '2',
      d: 'M3 12l2-2m0 0l7-7 7 7M5 10v10a1 1 0 001 1h3m10-11l2 2m-2-2v10a1 1 0 01-1 1h-3m-6 0a1 1 0 001-1v-4a1 1 0 011-1h2a1 1 0 011 1v4a1 1 0 001 1m-6 0h6'
    })
  ])
}

const ListIcon = {
  render: () => h('svg', { fill: 'none', stroke: 'currentColor', viewBox: '0 0 24 24' }, [
    h('path', { 
      'stroke-linecap': 'round', 
      'stroke-linejoin': 'round', 
      'stroke-width': '2',
      d: 'M9 5H7a2 2 0 00-2 2v12a2 2 0 002 2h10a2 2 0 002-2V7a2 2 0 00-2-2h-2M9 5a2 2 0 002 2h2a2 2 0 002-2M9 5a2 2 0 012-2h2a2 2 0 012 2m-3 7h3m-3 4h3m-6-4h.01M9 16h.01'
    })
  ])
}

const ReceiptIcon = {
  render: () => h('svg', { fill: 'none', stroke: 'currentColor', viewBox: '0 0 24 24' }, [
    h('path', { 
      'stroke-linecap': 'round', 
      'stroke-linejoin': 'round', 
      'stroke-width': '2',
      d: 'M20 7l-8-4-8 4m16 0l-8 4m8-4v10l-8 4m0-10L4 7m8 4v10M4 7v10l8 4'
    })
  ])
}

const IssueIcon = {
  render: () => h('svg', { fill: 'none', stroke: 'currentColor', viewBox: '0 0 24 24' }, [
    h('path', { 
      'stroke-linecap': 'round', 
      'stroke-linejoin': 'round', 
      'stroke-width': '2',
      d: 'M5 8h14M5 8a2 2 0 110-4h14a2 2 0 110 4M5 8v10a2 2 0 002 2h10a2 2 0 002-2V8m-9 4h4'
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

const PurchaseIcon = {
  render: () => h('svg', { fill: 'none', stroke: 'currentColor', viewBox: '0 0 24 24' }, [
    h('path', { 
      'stroke-linecap': 'round', 
      'stroke-linejoin': 'round', 
      'stroke-width': '2',
      d: 'M3 3h2l.4 2M7 13h10l4-8H5.4M7 13L5.4 5M7 13l-2.293 2.293c-.63.63-.184 1.707.707 1.707H17m0 0a2 2 0 100 4 2 2 0 000-4zm-8 2a2 2 0 11-4 0 2 2 0 014 0z'
    })
  ])
}

const SellIcon = {
  render: () => h('svg', { fill: 'none', stroke: 'currentColor', viewBox: '0 0 24 24' }, [
    h('path', { 
      'stroke-linecap': 'round', 
      'stroke-linejoin': 'round', 
      'stroke-width': '2',
      d: 'M17 9V7a2 2 0 00-2-2H5a2 2 0 00-2 2v6a2 2 0 002 2h2m2 4h10a2 2 0 002-2v-6a2 2 0 00-2-2H9a2 2 0 00-2 2v6a2 2 0 002 2zm7-5a2 2 0 11-4 0 2 2 0 014 0z'
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

const ProductIcon = {
  render: () => h('svg', { fill: 'none', stroke: 'currentColor', viewBox: '0 0 24 24' }, [
    h('path', { 
      'stroke-linecap': 'round', 
      'stroke-linejoin': 'round', 
      'stroke-width': '2',
      d: 'M20 7l-8-4-8 4m16 0l-8 4m8-4v10l-8 4m0-10L4 7m8 4v10M4 7v10l8 4'
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

// Menu sections for organized navigation
const menuSections = [
  {
    // Tổng quan
    items: [
      { path: '/', label: 'Tổng quan', icon: HomeIcon }
    ]
  },
  {
    // Phiếu kho
    label: 'Kho',
    items: [
      { path: '/stock/dashboard', label: 'Thống kê kho', icon: HomeIcon },
      { path: '/stock/entries', label: 'Danh sách phiếu', icon: ListIcon },
      { path: '/stock/receipt', label: 'Nhập kho', icon: ReceiptIcon },
      { path: '/stock/issue', label: 'Xuất kho', icon: IssueIcon }
    ]
  },
  {
    // Sản xuất
    label: 'Sản xuất',
    items: [
      { path: '/production/dashboard', label: 'Thống kê SX', icon: HomeIcon },
      { path: '/production/orders', label: 'Lệnh sản xuất', icon: ManufactureIcon },
      { path: '/production/boms', label: 'Định mức NVL', icon: BOMIcon }
    ]
  },
  {
    // Mua bán
    label: 'Giao dịch',
    items: [
      { path: '/sales-purchase/dashboard', label: 'Thống kê mua bán', icon: HomeIcon },
      { path: '/purchasing/invoices', label: 'Hóa đơn mua', icon: PurchaseIcon },
      { path: '/selling/invoices', label: 'Hóa đơn bán', icon: SellIcon }
    ]
  },
  {
    // Danh mục
    label: 'Danh mục',
    items: [
      { path: '/stock/warehouses', label: 'Quản lý kho', icon: WarehouseIcon },
      { path: '/master/items', label: 'Sản phẩm', icon: ProductIcon }
    ]
  }
]

// Methods
async function handleLogout() {
  await userStore.logout()
  router.push('/login')
}
</script>
