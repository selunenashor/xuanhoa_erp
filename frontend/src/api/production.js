/**
 * Production API Module
 * Work Orders and BOM related API calls
 */

import api from './client'

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
    if (isDefault) params.is_default = 1
    
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
