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
   * @param {boolean} isDefault - Only default BOMs (true = only default, false/null = all)
   */
  getBOMs: async (itemCode = null, isActive = true, isDefault = null) => {
    const params = {}
    if (itemCode) params.item_code = itemCode
    if (isActive) params.is_active = 1
    if (isDefault) params.is_default = 1  // Chỉ gửi khi muốn filter mặc định
    
    const res = await api.post('/method/xuanhoa_app.api.get_boms', params)
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

// ==================== WAREHOUSE APIs ====================

export const warehouseAPI = {
  /**
   * Get list of warehouses
   * @param {Object} params - { is_group }
   */
  getList: async (params = {}) => {
    const res = await api.post('/method/xuanhoa_app.api.get_warehouses', { 
      is_group: params.is_group || 0 
    })
    return { success: true, data: res.data.message || [] }
  }
}

// ==================== SUPPLIER APIs ====================

export const supplierAPI = {
  /**
   * Get list of suppliers
   * @param {string|null} query - Search query
   * @param {number} limit - Max results
   */
  getList: async (query = null, limit = 20) => {
    const res = await api.post('/method/xuanhoa_app.api.get_suppliers', { query, limit })
    return res.data.message
  }
}

// ==================== CUSTOMER APIs ====================

export const customerAPI = {
  /**
   * Get list of customers
   * @param {string|null} query - Search query
   * @param {number} limit - Max results
   */
  getList: async (query = null, limit = 20) => {
    const res = await api.post('/method/xuanhoa_app.api.get_customers', { query, limit })
    return res.data.message
  }
}

// ==================== PURCHASE INVOICE APIs ====================

export const purchaseInvoiceAPI = {
  /**
   * Get list of purchase invoices
   * @param {Object} params - { status, supplier, from_date, to_date, search, limit, page }
   */
  getList: async (params = {}) => {
    const res = await api.post('/method/xuanhoa_app.api.get_purchase_invoices', params)
    return res.data.message
  },

  /**
   * Get purchase invoice detail
   * @param {string} name - Invoice ID
   */
  getDetail: async (name) => {
    const res = await api.post('/method/xuanhoa_app.api.get_purchase_invoice_detail', { name })
    return res.data.message
  },

  /**
   * Create new purchase invoice (Draft)
   * @param {Object} data - { supplier, items, posting_date, due_date, set_warehouse, remarks, update_stock }
   */
  create: async (data) => {
    const res = await api.post('/method/xuanhoa_app.api.create_purchase_invoice', {
      supplier: data.supplier,
      items: JSON.stringify(data.items),
      posting_date: data.posting_date,
      due_date: data.due_date,
      set_warehouse: data.set_warehouse,
      remarks: data.remarks,
      update_stock: data.update_stock || 0
    })
    return res.data.message
  },

  /**
   * Submit/Approve purchase invoice
   * @param {string} name - Invoice ID
   */
  submit: async (name) => {
    const res = await api.post('/method/xuanhoa_app.api.submit_purchase_invoice', { name })
    return res.data.message
  },

  /**
   * Cancel purchase invoice
   * @param {string} name - Invoice ID
   */
  cancel: async (name) => {
    const res = await api.post('/method/xuanhoa_app.api.cancel_purchase_invoice', { name })
    return res.data.message
  },

  /**
   * Create stock entry (Material Receipt) from purchase invoice
   * @param {string} purchaseInvoice - Invoice ID
   * @param {string|null} warehouse - Target warehouse (optional)
   */
  createStockEntry: async (purchaseInvoice, warehouse = null) => {
    const res = await api.post('/method/xuanhoa_app.api.create_stock_entry_from_purchase_invoice', {
      purchase_invoice: purchaseInvoice,
      warehouse
    })
    return res.data.message
  },

  /**
   * Create payment for purchase invoice
   * @param {string} purchaseInvoice - Invoice ID
   * @param {number|null} amount - Payment amount (optional, defaults to full outstanding)
   * @param {string|null} modeOfPayment - Mode of payment (Cash, Bank, etc.)
   * @param {string|null} referenceNo - Reference number
   * @param {string|null} referenceDate - Reference date
   */
  createPayment: async (purchaseInvoice, amount = null, modeOfPayment = null, referenceNo = null, referenceDate = null) => {
    const res = await api.post('/method/xuanhoa_app.api.create_payment_for_purchase_invoice', {
      purchase_invoice: purchaseInvoice,
      amount,
      mode_of_payment: modeOfPayment,
      reference_no: referenceNo,
      reference_date: referenceDate
    })
    return res.data.message
  }
}

// ==================== SALES INVOICE APIs ====================

export const salesInvoiceAPI = {
  /**
   * Get list of sales invoices
   * @param {Object} params - { status, customer, from_date, to_date, search, limit, page }
   */
  getList: async (params = {}) => {
    const res = await api.post('/method/xuanhoa_app.api.get_sales_invoices', params)
    return res.data.message
  },

  /**
   * Get sales invoice detail
   * @param {string} name - Invoice ID
   */
  getDetail: async (name) => {
    const res = await api.post('/method/xuanhoa_app.api.get_sales_invoice_detail', { name })
    return res.data.message
  },

  /**
   * Create new sales invoice (Draft)
   * @param {Object} data - { customer, items, posting_date, due_date, set_warehouse, remarks, update_stock }
   */
  create: async (data) => {
    const res = await api.post('/method/xuanhoa_app.api.create_sales_invoice', {
      customer: data.customer,
      items: JSON.stringify(data.items),
      posting_date: data.posting_date,
      due_date: data.due_date,
      set_warehouse: data.set_warehouse,
      remarks: data.remarks,
      update_stock: data.update_stock || 0
    })
    return res.data.message
  },

  /**
   * Submit/Approve sales invoice
   * @param {string} name - Invoice ID
   */
  submit: async (name) => {
    const res = await api.post('/method/xuanhoa_app.api.submit_sales_invoice', { name })
    return res.data.message
  },

  /**
   * Cancel sales invoice
   * @param {string} name - Invoice ID
   */
  cancel: async (name) => {
    const res = await api.post('/method/xuanhoa_app.api.cancel_sales_invoice', { name })
    return res.data.message
  },

  /**
   * Create stock entry (Material Issue) from sales invoice
   * @param {string} salesInvoice - Invoice ID
   * @param {string|null} warehouse - Source warehouse (optional)
   */
  createStockEntry: async (salesInvoice, warehouse = null) => {
    const res = await api.post('/method/xuanhoa_app.api.create_stock_entry_from_sales_invoice', {
      sales_invoice: salesInvoice,
      warehouse
    })
    return res.data.message
  },

  /**
   * Create payment (receive) for sales invoice
   * @param {string} salesInvoice - Invoice ID
   * @param {number|null} amount - Payment amount (optional, defaults to full outstanding)
   * @param {string|null} modeOfPayment - Mode of payment (Cash, Bank, etc.)
   * @param {string|null} referenceNo - Reference number
   * @param {string|null} referenceDate - Reference date
   */
  createPayment: async (salesInvoice, amount = null, modeOfPayment = null, referenceNo = null, referenceDate = null) => {
    const res = await api.post('/method/xuanhoa_app.api.create_payment_for_sales_invoice', {
      sales_invoice: salesInvoice,
      amount,
      mode_of_payment: modeOfPayment,
      reference_no: referenceNo,
      reference_date: referenceDate
    })
    return res.data.message
  }
}

// ==================== PAYMENT APIs ====================

export const paymentAPI = {
  /**
   * Get list of payment modes
   */
  getModes: async () => {
    const res = await api.post('/method/xuanhoa_app.api.get_mode_of_payments')
    return res.data.message
  }
}

// ==================== BOM APIs ====================

export const bomAPI = {
  /**
   * Get list of BOMs
   * @param {Object} params - { item, is_active, is_default, search, page, page_size }
   */
  getList: async (params = {}) => {
    const res = await api.post('/method/xuanhoa_app.api.get_all_boms', params)
    return res.data.message
  },

  /**
   * Get BOM detail with items
   * @param {string} name - BOM ID
   */
  getDetail: async (name) => {
    const res = await api.post('/method/xuanhoa_app.api.get_bom_detail', { bom_no: name })
    return res.data.message
  },

  /**
   * Create new BOM
   * @param {Object} data - { item, quantity, uom, is_active, is_default, items }
   */
  create: async (data) => {
    const res = await api.post('/method/xuanhoa_app.api.create_bom', {
      item: data.item,
      quantity: data.quantity,
      uom: data.uom,
      is_active: data.is_active,
      is_default: data.is_default,
      items: JSON.stringify(data.items)
    })
    return res.data.message
  },

  /**
   * Update existing BOM
   * @param {string} name - BOM ID
   * @param {Object} data - { is_active, is_default, quantity, items }
   */
  update: async (name, data) => {
    const params = {
      bom_name: name,
      is_active: data.is_active,
      is_default: data.is_default
    }
    // Nếu có items thì gửi kèm để update
    if (data.items && data.items.length > 0) {
      params.quantity = data.quantity
      params.items = JSON.stringify(data.items)
    }
    const res = await api.post('/method/xuanhoa_app.api.update_bom', params)
    return res.data.message
  },

  /**
   * Delete BOM
   * @param {string} name - BOM ID
   */
  delete: async (name) => {
    const res = await api.post('/method/xuanhoa_app.api.delete_bom', { bom_name: name })
    return res.data.message
  }
}

// ==================== WAREHOUSE STOCK APIs ====================

export const warehouseStockAPI = {
  /**
   * Get stock grouped by warehouse (for "Theo kho" view)
   * @param {Object} params - { search, item_group }
   */
  getByWarehouse: async (params = {}) => {
    const res = await api.post('/method/xuanhoa_app.api.get_stock_by_warehouse', params)
    return res.data.message
  },

  /**
   * Get stock for a specific warehouse
   * @param {string} warehouse - Warehouse name
   * @param {Object} params - { search, page, page_size }
   */
  getWarehouseStock: async (warehouse, params = {}) => {
    const res = await api.post('/method/xuanhoa_app.api.get_warehouse_stock', { warehouse, ...params })
    return res.data.message
  },

  /**
   * Get all stock (flat list)
   * @param {Object} params - { warehouse, item_code, item_group, search, page, page_size }
   */
  getAll: async (params = {}) => {
    const res = await api.post('/method/xuanhoa_app.api.get_all_stock', params)
    return res.data.message
  },

  /**
   * Get warehouse details with stock summary
   * @param {string} warehouse - Warehouse name
   */
  getWarehouseDetails: async (warehouse) => {
    const res = await api.post('/method/xuanhoa_app.api.get_warehouse_details', { warehouse })
    return res.data.message
  },

  /**
   * Get stock ledger (transaction history)
   * @param {Object} params - { warehouse, item_code, from_date, to_date, page, page_size }
   */
  getLedger: async (params = {}) => {
    const res = await api.post('/method/xuanhoa_app.api.get_stock_ledger', params)
    return res.data.message
  }
}


// ==================== ITEM MANAGEMENT APIs ====================

export const itemAPI = {
  /**
   * Search items for autocomplete (simple search)
   * @param {Object} params - { search, item_group, warehouse }
   */
  search: async (params = {}) => {
    const res = await api.post('/method/xuanhoa_app.api.search_items', { 
      query: params.search || '',
      item_group: params.item_group || null,
      warehouse: params.warehouse || null
    })
    return { success: true, data: res.data.message || [] }
  },

  /**
   * Get list of items with pagination and filters
   * @param {Object} params - { search, item_group, is_stock_item, disabled, page, page_size }
   */
  getList: async (params = {}) => {
    const res = await api.post('/method/xuanhoa_app.api.get_item_list', params)
    return res.data.message
  },

  /**
   * Get item detail
   * @param {string} itemCode - Item code
   */
  getDetail: async (itemCode) => {
    const res = await api.post('/method/xuanhoa_app.api.get_item_detail', { item_code: itemCode })
    return res.data.message
  },

  /**
   * Create new item
   * @param {Object} data - Item data
   */
  create: async (data) => {
    const res = await api.post('/method/xuanhoa_app.api.create_item', data)
    return res.data.message
  },

  /**
   * Update existing item
   * @param {string} itemCode - Item code
   * @param {Object} data - Update data
   */
  update: async (itemCode, data) => {
    const res = await api.post('/method/xuanhoa_app.api.update_item', { item_code: itemCode, ...data })
    return res.data.message
  },

  /**
   * Toggle item status (active/disabled)
   * @param {string} itemCode - Item code
   */
  toggleStatus: async (itemCode) => {
    const res = await api.post('/method/xuanhoa_app.api.toggle_item_status', { item_code: itemCode })
    return res.data.message
  }
}


// ==================== ITEM GROUP MANAGEMENT APIs ====================

export const itemGroupAPI = {
  /**
   * Get list of item groups
   * @param {Object} params - { search, parent }
   */
  getList: async (params = {}) => {
    const res = await api.post('/method/xuanhoa_app.api.get_item_group_list', params)
    return res.data.message
  },

  /**
   * Get item group tree (hierarchical)
   */
  getTree: async () => {
    const res = await api.post('/method/xuanhoa_app.api.get_item_group_tree')
    return res.data.message
  },

  /**
   * Create new item group
   * @param {Object} data - { item_group_name, parent_item_group, is_group }
   */
  create: async (data) => {
    const res = await api.post('/method/xuanhoa_app.api.create_item_group', data)
    return res.data.message
  },

  /**
   * Update item group
   * @param {string} name - Group name
   * @param {Object} data - Update data
   */
  update: async (name, data) => {
    const res = await api.post('/method/xuanhoa_app.api.update_item_group', { name, ...data })
    return res.data.message
  },

  /**
   * Delete item group
   * @param {string} name - Group name
   */
  delete: async (name) => {
    const res = await api.post('/method/xuanhoa_app.api.delete_item_group', { name })
    return res.data.message
  }
}


// ==================== UOM APIs ====================

export const uomAPI = {
  /**
   * Get list of UOMs
   */
  getList: async () => {
    const res = await api.post('/method/xuanhoa_app.api.get_uom_list')
    return res.data.message
  }
}

export default api
