/**
 * API Client - Xuân Hòa Manufacturing
 * 
 * Axios instance configured for Frappe/ERPNext API
 */

import axios from 'axios'

// Create axios instance
const api = axios.create({
  baseURL: '/api/method',
  withCredentials: true,  // Important: send cookies for session auth
  headers: {
    'Content-Type': 'application/json',
    'Accept': 'application/json'
  }
})

// Response interceptor - extract message from Frappe response
api.interceptors.response.use(
  response => {
    // Frappe wraps response in { message: ... }
    return response.data.message !== undefined ? response.data.message : response.data
  },
  error => {
    console.error('API Error:', error.response?.data || error.message)
    const message = error.response?.data?.exc_type || error.response?.data?._server_messages || error.message
    return Promise.reject(new Error(message))
  }
)

export default api

/**
 * Xuân Hòa API Functions
 */
export const xuanhoaAPI = {
  // ==================
  // Dashboard
  // ==================
  getDashboardKPI: () => 
    api.post('xuanhoa_app.api.get_dashboard_kpi'),
  
  // ==================
  // Work Orders
  // ==================
  getWorkOrders: (status = null, limit = 20) => 
    api.post('xuanhoa_app.api.get_work_orders', { status, limit }),
  
  getWorkOrder: (name) =>
    api.post('xuanhoa_app.api.get_work_order_detail', { work_order_name: name }),
  
  getWorkOrderDetail: (name) =>
    api.post('xuanhoa_app.api.get_work_order_detail', { work_order_name: name }),
  
  startWorkOrder: (name) => 
    api.post('xuanhoa_app.api.start_work_order', { work_order_name: name }),
  
  completeWorkOrder: (name, qty) => 
    api.post('xuanhoa_app.api.complete_work_order', { work_order_name: name, qty }),
  
  // ==================
  // Stock Entry
  // ==================
  createMaterialReceipt: (item_code, qty, warehouse, rate = null) =>
    api.post('xuanhoa_app.api.create_material_receipt', { item_code, qty, warehouse, rate }),
  
  createMaterialIssue: (item_code, qty, warehouse, cost_center = null) =>
    api.post('xuanhoa_app.api.create_material_issue', { item_code, qty, warehouse, cost_center }),
  
  // ==================
  // Items
  // ==================
  getItems: () =>
    api.post('xuanhoa_app.api.get_items'),
  
  searchItems: (query, item_group = null, limit = 10) =>
    api.post('xuanhoa_app.api.search_items', { query, item_group, limit }),
  
  getItemStock: (item_code, warehouse = null) =>
    api.post('xuanhoa_app.api.get_item_stock', { item_code, warehouse }),
  
  // ==================
  // Warehouses
  // ==================
  getWarehouses: (is_group = null) =>
    api.post('xuanhoa_app.api.get_warehouses', { is_group }),
  
  // ==================
  // BOM
  // ==================
  getBOMItems: (bom_no) =>
    api.post('xuanhoa_app.api.get_bom_items', { bom_no }),
  
  // ==================
  // Auth (Frappe built-in)
  // ==================
  login: (usr, pwd) =>
    api.post('login', { usr, pwd }),
  
  logout: () =>
    api.post('logout'),
  
  getLoggedUser: () =>
    api.post('frappe.auth.get_logged_user')
}
