/**
 * API Client - Axios Instance
 * Base configuration for all API calls
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

export default api
