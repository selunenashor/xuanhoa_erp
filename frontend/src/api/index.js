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
   * @param {string} query - Search query
   * @param {string|null} itemGroup - Filter by item group
   * @param {string|null} warehouse - Warehouse to get specific stock
   */
  searchItems: async (query, itemGroup = null, warehouse = null) => {
    const res = await api.post('/method/xuanhoa_app.api.search_items', { 
      query, 
      item_group: itemGroup,
      warehouse: warehouse 
    })
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
   * Create material issue (xuất kho) - Hỗ trợ nhiều sản phẩm
   * @param {Object} data - { items: Array, posting_date: string, remarks: string }
   */
  createMaterialIssue: async (data) => {
    const res = await api.post('/method/xuanhoa_app.api.create_material_issue', {
      items: JSON.stringify(data.items),
      posting_date: data.posting_date,
      remarks: data.remarks
    })
    return res.data.message
  },

  /**
   * Create material issue (legacy - single item)
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
   * @param {Object} params - { status, docstatus, limit, page }
   */
  getList: async (params = {}) => {
    const res = await api.post('/method/xuanhoa_app.api.get_work_orders', params)
    return res.data.message
  },

  /**
   * Get work order detail
   */
  getDetail: async (name) => {
    const res = await api.post('/method/xuanhoa_app.api.get_work_order_detail', { work_order_name: name })
    return res.data.message
  },

  /**
   * Get list of BOMs for selection
   * @param {string|null} itemCode - Filter by item
   * @param {boolean} isActive - Only active BOMs
   * @param {boolean} isDefault - Only default BOMs
   */
  getBOMs: async (itemCode = null, isActive = true, isDefault = false) => {
    const res = await api.post('/method/xuanhoa_app.api.get_boms', { 
      item_code: itemCode,
      is_active: isActive ? 1 : 0,
      is_default: isDefault ? 1 : 0
    })
    return res.data.message
  },

  /**
   * Get BOM detail with items
   */
  getBOMDetail: async (bomNo) => {
    const res = await api.post('/method/xuanhoa_app.api.get_bom_detail', { bom_no: bomNo })
    return res.data.message
  },

  /**
   * Create new work order (Draft)
   * @param {Object} data - { bom_no, qty, planned_start_date, expected_delivery_date, source_warehouse, wip_warehouse, fg_warehouse }
   */
  create: async (data) => {
    const res = await api.post('/method/xuanhoa_app.api.create_work_order', data)
    return res.data.message
  },

  /**
   * Submit/Approve work order (Draft -> Submitted)
   */
  submit: async (name) => {
    const res = await api.post('/method/xuanhoa_app.api.submit_work_order', { work_order_name: name })
    return res.data.message
  },

  /**
   * Start work order (transfer materials to WIP)
   */
  start: async (name) => {
    const res = await api.post('/method/xuanhoa_app.api.start_work_order', { work_order_name: name })
    return res.data.message
  },

  /**
   * Complete work order (manufacture finished goods)
   */
  complete: async (name, qty) => {
    const res = await api.post('/method/xuanhoa_app.api.complete_work_order', { work_order_name: name, qty })
    return res.data.message
  },

  /**
   * Stop work order
   */
  stop: async (name) => {
    const res = await api.post('/method/xuanhoa_app.api.stop_work_order', { work_order_name: name })
    return res.data.message
  },

  /**
   * Cancel work order (only if not started)
   */
  cancel: async (name) => {
    const res = await api.post('/method/xuanhoa_app.api.cancel_work_order', { work_order_name: name })
    return res.data.message
  }
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
