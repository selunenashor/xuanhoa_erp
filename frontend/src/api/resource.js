/**
 * Resource API Module
 * Generic CRUD operations for Frappe doctypes
 */

import api from './client'

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

export const customAPI = {
  /**
   * Call custom whitelisted method
   */
  call: (method, params = {}) => 
    api.post(`/method/${method}`, params)
}
