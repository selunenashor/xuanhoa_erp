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

export default api
