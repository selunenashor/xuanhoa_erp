/**
 * Stock API Module
 * Stock management related API calls
 */

import api from './client'

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
