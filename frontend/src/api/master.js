/**
 * Master Data API Module
 * Items, Item Groups, UOMs, Suppliers, Customers related API calls
 */

import api from './client'

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

export const uomAPI = {
  /**
   * Get list of UOMs
   */
  getList: async () => {
    const res = await api.post('/method/xuanhoa_app.api.get_uom_list')
    return res.data.message
  }
}

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
