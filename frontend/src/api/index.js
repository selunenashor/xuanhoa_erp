/**
 * API Service Module
 * Centralized API calls using Axios
 */

import axios from 'axios'

// Create axios instance with default config
const api = axios.create({
  baseURL: '/api',
  withCredentials: true,
  headers: {
    'Content-Type': 'application/json',
    'Accept': 'application/json'
  }
})

// Request interceptor
api.interceptors.request.use(
  (config) => {
    // Add X-Frappe-CSRF-Token if available
    const csrfToken = document.cookie
      .split('; ')
      .find(row => row.startsWith('csrf_token='))
      ?.split('=')[1]
    
    if (csrfToken) {
      config.headers['X-Frappe-CSRF-Token'] = csrfToken
    }
    return config
  },
  (error) => Promise.reject(error)
)

// Response interceptor
api.interceptors.response.use(
  (response) => response,
  (error) => {
    // Just reject the error, let the app handle auth redirects
    // Do NOT redirect here - it causes infinite loops with the router guard
    console.warn('API Error:', error.response?.status, error.config?.url)
    return Promise.reject(error)
  }
)

// ==================== AUTH APIs ====================

export const authAPI = {
  /**
   * Login with username and password
   */
  login: (usr, pwd) => api.post('/method/login', { usr, pwd }),

  /**
   * Logout current user
   */
  logout: () => api.get('/method/logout'),

  /**
   * Get current logged in user info
   */
  getLoggedUser: () => api.get('/method/frappe.auth.get_logged_user'),

  /**
   * Get full user info (name, full_name, etc.)
   */
  getUserInfo: (email) => api.get(`/resource/User/${encodeURIComponent(email)}`, {
    params: {
      fields: JSON.stringify(['name', 'email', 'full_name', 'first_name', 'last_name', 'user_image'])
    }
  }),

  /**
   * Check if user has specific role
   */
  getUserRoles: () => api.get('/method/frappe.core.doctype.user.user.get_roles')
}

// ==================== RESOURCE APIs ====================

export const resourceAPI = {
  /**
   * Get list of documents
   */
  getList: (doctype, params = {}) => 
    api.get(`/resource/${doctype}`, { params }),

  /**
   * Get single document
   */
  get: (doctype, name) => 
    api.get(`/resource/${doctype}/${name}`),

  /**
   * Create new document
   */
  create: (doctype, data) => 
    api.post(`/resource/${doctype}`, data),

  /**
   * Update document
   */
  update: (doctype, name, data) => 
    api.put(`/resource/${doctype}/${name}`, data),

  /**
   * Delete document
   */
  delete: (doctype, name) => 
    api.delete(`/resource/${doctype}/${name}`)
}

// ==================== CUSTOM APIs ====================

export const customAPI = {
  /**
   * Call custom whitelisted method
   */
  call: (method, params = {}) => 
    api.post(`/method/${method}`, params)
}

// ==================== STOCK APIs ====================

export const stockAPI = {
  /**
   * Get list of items for selection
   */
  getItems: async () => {
    const res = await api.post('/method/xuanhoa_app.api.get_items')
    return res.data.message
  },

  /**
   * Search items with query
   */
  searchItems: async (query, itemGroup = null) => {
    const res = await api.post('/method/xuanhoa_app.api.search_items', { query, item_group: itemGroup })
    return res.data.message
  },

  /**
   * Get list of warehouses
   */
  getWarehouses: async (isGroup = 0) => {
    const res = await api.post('/method/xuanhoa_app.api.get_warehouses', { is_group: isGroup })
    return res.data.message
  },

  /**
   * Get item stock info
   */
  getItemStock: async (itemCode, warehouse = null) => {
    const res = await api.post('/method/xuanhoa_app.api.get_item_stock', { item_code: itemCode, warehouse })
    return res.data.message
  },

  /**
   * Create material receipt (nhập kho) - Hỗ trợ nhiều sản phẩm
   * @param {Object} data - { items: Array, posting_date: string, remarks: string }
   */
  createMaterialReceipt: async (data) => {
    const res = await api.post('/method/xuanhoa_app.api.create_material_receipt', {
      items: JSON.stringify(data.items),
      posting_date: data.posting_date,
      remarks: data.remarks
    })
    return res.data.message
  },

  /**
   * Create material receipt (legacy - single item)
   */
  createReceipt: async (itemCode, qty, warehouse, rate = null) => {
    const res = await api.post('/method/xuanhoa_app.api.create_material_receipt', {
      item_code: itemCode,
      qty,
      warehouse,
      rate
    })
    return res.data.message
  },

  /**
   * Create material issue (xuất kho)
   */
  createIssue: async (itemCode, qty, warehouse) => {
    const res = await api.post('/method/xuanhoa_app.api.create_material_issue', {
      item_code: itemCode,
      qty,
      warehouse
    })
    return res.data.message
  },

  /**
   * Get recent stock entries
   */
  getStockEntries: async (params = {}) => {
    const res = await api.post('/method/xuanhoa_app.api.get_stock_entries', params)
    return res.data.message
  },

  /**
   * Get stock entry detail
   */
  getStockEntryDetail: async (name) => {
    const res = await api.post('/method/xuanhoa_app.api.get_stock_entry_detail', { name })
    return res.data.message
  },

  /**
   * Get recent stock entries (legacy alias)
   */
  getRecentEntries: async (purpose = null, limit = 20) => {
    const res = await api.post('/method/xuanhoa_app.api.get_stock_entries', { purpose, limit })
    return res.data.message
  }
}

// ==================== WORK ORDER APIs ====================

export const workOrderAPI = {
  /**
   * Get list of work orders
   */
  getList: (status = null, limit = 20) => 
    api.post('/method/xuanhoa_app.api.get_work_orders', { status, limit }),

  /**
   * Get work order detail
   */
  getDetail: (name) => 
    api.post('/method/xuanhoa_app.api.get_work_order_detail', { work_order_name: name }),

  /**
   * Start work order (transfer materials)
   */
  start: (name) => 
    api.post('/method/xuanhoa_app.api.start_work_order', { work_order_name: name }),

  /**
   * Complete work order (manufacture)
   */
  complete: (name, qty) => 
    api.post('/method/xuanhoa_app.api.complete_work_order', { work_order_name: name, qty })
}

// ==================== DASHBOARD APIs ====================

export const dashboardAPI = {
  /**
   * Get KPI data for dashboard
   */
  getKPI: async () => {
    const res = await api.post('/method/xuanhoa_app.api.get_dashboard_kpi')
    return res.data.message
  },

  /**
   * Get recent activities for dashboard
   */
  getRecentActivities: async (limit = 10) => {
    const res = await api.post('/method/xuanhoa_app.api.get_recent_activities', { limit })
    return res.data.message
  }
}

export default api
