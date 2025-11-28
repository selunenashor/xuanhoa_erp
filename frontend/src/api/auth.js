/**
 * Auth API Module
 * Authentication related API calls
 */

import api from './client'

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
