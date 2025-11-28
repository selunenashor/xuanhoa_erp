/**
 * Vue Router Configuration
 * With authentication guards
 */

import { createRouter, createWebHistory } from 'vue-router'
import { useUserStore } from '@/stores/user'

// Layouts
import MainLayout from '@/components/layouts/MainLayout.vue'

// Routes configuration
const routes = [
  // Public routes (no auth required)
  {
    path: '/login',
    name: 'Login',
    component: () => import('@/pages/Login.vue'),
    meta: { 
      title: 'Đăng nhập',
      public: true 
    }
  },

  // Protected routes (require auth)
  {
    path: '/',
    component: MainLayout,
    meta: { requiresAuth: true },
    children: [
      {
        path: '',
        name: 'Dashboard',
        component: () => import('@/pages/Dashboard.vue'),
        meta: { title: 'Tổng quan' }
      },
      {
        path: 'stock/receipt',
        name: 'MaterialReceipt',
        component: () => import('@/pages/stock/MaterialReceipt.vue'),
        meta: { title: 'Nhập kho' }
      },
      {
        path: 'stock/receipts',
        name: 'StockReceiptList',
        redirect: '/stock/entries?type=Material%20Receipt'
      },
      {
        path: 'stock/entries',
        name: 'StockEntryList',
        component: () => import('@/pages/stock/StockEntryList.vue'),
        meta: { title: 'Danh sách phiếu kho' }
      },
      {
        path: 'stock/receipts/:name',
        redirect: to => ({ path: `/stock/entries/${to.params.name}` })
      },
      {
        path: 'stock/entries/:name',
        name: 'StockEntryDetail',
        component: () => import('@/pages/stock/StockEntryDetail.vue'),
        meta: { title: 'Chi tiết phiếu kho' }
      },
      {
        path: 'stock/issue',
        name: 'MaterialIssue',
        component: () => import('@/pages/stock/MaterialIssue.vue'),
        meta: { title: 'Xuất kho' }
      },
      {
        path: 'stock/warehouses',
        name: 'WarehouseStock',
        component: () => import('@/pages/stock/WarehouseStock.vue'),
        meta: { title: 'Quản lý kho hàng' }
      },
      {
        path: 'production/boms',
        name: 'BOMList',
        component: () => import('@/pages/production/BOMList.vue'),
        meta: { title: 'Định mức NVL (BOM)' }
      },
      {
        path: 'production/orders',
        name: 'WorkOrderList',
        component: () => import('@/pages/production/WorkOrderList.vue'),
        meta: { title: 'Lệnh sản xuất' }
      },
      {
        path: 'production/orders/create',
        name: 'WorkOrderCreate',
        component: () => import('@/pages/production/WorkOrderCreate.vue'),
        meta: { title: 'Tạo lệnh sản xuất' }
      },
      {
        path: 'production/orders/:name',
        name: 'WorkOrderDetail',
        component: () => import('@/pages/production/WorkOrderDetail.vue'),
        meta: { title: 'Chi tiết lệnh sản xuất' }
      },
      // Purchase Invoice routes
      {
        path: 'purchasing/invoices',
        name: 'PurchaseInvoiceList',
        component: () => import('@/pages/purchasing/PurchaseInvoiceList.vue'),
        meta: { title: 'Hóa đơn mua hàng' }
      },
      {
        path: 'purchasing/invoices/create',
        name: 'PurchaseInvoiceCreate',
        component: () => import('@/pages/purchasing/PurchaseInvoiceCreate.vue'),
        meta: { title: 'Tạo hóa đơn mua hàng' }
      },
      {
        path: 'purchasing/invoices/:name',
        name: 'PurchaseInvoiceDetail',
        component: () => import('@/pages/purchasing/PurchaseInvoiceDetail.vue'),
        meta: { title: 'Chi tiết hóa đơn mua hàng' }
      },
      // Sales Invoice routes
      {
        path: 'selling/invoices',
        name: 'SalesInvoiceList',
        component: () => import('@/pages/selling/SalesInvoiceList.vue'),
        meta: { title: 'Hóa đơn bán hàng' }
      },
      {
        path: 'selling/invoices/create',
        name: 'SalesInvoiceCreate',
        component: () => import('@/pages/selling/SalesInvoiceCreate.vue'),
        meta: { title: 'Tạo hóa đơn bán hàng' }
      },
      {
        path: 'selling/invoices/:name',
        name: 'SalesInvoiceDetail',
        component: () => import('@/pages/selling/SalesInvoiceDetail.vue'),
        meta: { title: 'Chi tiết hóa đơn bán hàng' }
      },
      // Master Data routes
      {
        path: 'master/items',
        name: 'ItemList',
        component: () => import('@/pages/master/ItemList.vue'),
        meta: { title: 'Quản lý sản phẩm' }
      }
    ]
  },

  // 404 - Catch all
  {
    path: '/:pathMatch(.*)*',
    name: 'NotFound',
    component: () => import('@/pages/NotFound.vue'),
    meta: { title: 'Không tìm thấy trang' }
  }
]

// Create router instance
const router = createRouter({
  history: createWebHistory('/manage/'),
  routes,
  scrollBehavior(to, from, savedPosition) {
    if (savedPosition) {
      return savedPosition
    } else {
      return { top: 0 }
    }
  }
})

// Navigation guards
router.beforeEach(async (to, from, next) => {
  console.log('[Router] beforeEach:', from.path, '->', to.path)
  
  // Update document title
  document.title = `${to.meta.title || 'Trang'} | Quản lý Sản xuất`

  const userStore = useUserStore()

  // MUST wait for initialization to complete before checking auth
  if (!userStore.initialized) {
    console.log('[Router] waiting for init...')
    await userStore.init()
    console.log('[Router] init done, isLoggedIn:', userStore.isLoggedIn)
  }

  // Check if route requires authentication
  const requiresAuth = to.matched.some(record => record.meta.requiresAuth)
  const isPublicRoute = to.meta.public
  
  console.log('[Router] requiresAuth:', requiresAuth, 'isPublic:', isPublicRoute, 'isLoggedIn:', userStore.isLoggedIn)

  if (requiresAuth && !userStore.isLoggedIn) {
    // Not logged in, redirect to login
    console.log('[Router] -> redirect to /login')
    next({
      path: '/login',
      query: { redirect: to.fullPath }
    })
  } else if (isPublicRoute && userStore.isLoggedIn && to.path === '/login') {
    // Already logged in, redirect to dashboard
    console.log('[Router] -> redirect to /')
    next('/')
  } else {
    console.log('[Router] -> proceed')
    next()
  }
})

export default router
