/**
 * Vue Router Configuration
 */

import { createRouter, createWebHistory } from 'vue-router'

const routes = [
  {
    path: '/',
    name: 'Dashboard',
    component: () => import('@/pages/Dashboard.vue'),
    meta: { title: 'Tổng quan' }
  },
  {
    path: '/login',
    name: 'Login',
    component: () => import('@/pages/Login.vue'),
    meta: { title: 'Đăng nhập', public: true }
  },
  {
    path: '/stock/receipt',
    name: 'MaterialReceipt',
    component: () => import('@/pages/MaterialReceipt.vue'),
    meta: { title: 'Nhập kho' }
  },
  {
    path: '/stock/issue',
    name: 'MaterialIssue',
    component: () => import('@/pages/MaterialIssue.vue'),
    meta: { title: 'Xuất kho' }
  },
  {
    path: '/production/orders',
    name: 'WorkOrderList',
    component: () => import('@/pages/WorkOrderList.vue'),
    meta: { title: 'Lệnh sản xuất' }
  },
  {
    path: '/production/orders/:name',
    name: 'WorkOrderDetail',
    component: () => import('@/pages/WorkOrderDetail.vue'),
    meta: { title: 'Chi tiết lệnh sản xuất' }
  }
]

const router = createRouter({
  history: createWebHistory('/manage/'),
  routes
})

// Navigation guard for auth
router.beforeEach((to, from, next) => {
  document.title = `${to.meta.title || 'Xuân Hòa'} | Xuân Hòa Manufacturing`
  next()
})

export default router
