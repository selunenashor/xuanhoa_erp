/**
 * Invoice API Module
 * Purchase and Sales Invoice related API calls
 */

import api from './client'

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
