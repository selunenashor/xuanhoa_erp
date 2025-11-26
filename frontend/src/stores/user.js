/**
 * User Store
 * Manages authentication state and user info
 */

import { defineStore } from 'pinia'
import { ref, computed } from 'vue'
import { authAPI } from '@/api'

export const useUserStore = defineStore('user', () => {
  // ==================== STATE ====================
  
  const user = ref(null)
  const userInfo = ref(null)  // Store full user info
  const roles = ref([])
  const isLoading = ref(false)
  const error = ref(null)
  const initialized = ref(false)  // Track if init has been called
  let initPromise = null  // Promise to handle concurrent init calls

  // ==================== GETTERS ====================
  
  const isLoggedIn = computed(() => !!user.value && user.value !== 'Guest')
  
  const isAdmin = computed(() => 
    roles.value.includes('Administrator') || roles.value.includes('System Manager')
  )
  
  const fullName = computed(() => {
    if (userInfo.value?.full_name) return userInfo.value.full_name
    if (user.value && user.value !== 'Guest') return user.value
    return 'Guest'
  })

  // ==================== ACTIONS ====================

  /**
   * Login with credentials
   */
  async function login(username, password) {
    isLoading.value = true
    error.value = null
    
    try {
      await authAPI.login(username, password)
      await fetchUser()
      return { success: true }
    } catch (err) {
      const message = err.response?.data?.message || 'Đăng nhập thất bại'
      error.value = message
      return { success: false, message }
    } finally {
      isLoading.value = false
    }
  }

  /**
   * Logout current user
   */
  async function logout() {
    isLoading.value = true
    
    try {
      await authAPI.logout()
    } catch (err) {
      console.error('Logout error:', err)
    } finally {
      user.value = null
      userInfo.value = null
      roles.value = []
      isLoading.value = false
    }
  }

  /**
   * Fetch current user info
   */
  async function fetchUser() {
    try {
      const response = await authAPI.getLoggedUser()
      const loggedUser = response.data.message
      
      console.log('[UserStore] fetchUser result:', loggedUser)
      
      if (loggedUser && loggedUser !== 'Guest') {
        user.value = loggedUser
        // Fetch full user info and roles
        await Promise.all([fetchUserInfo(loggedUser), fetchRoles()])
      } else {
        user.value = null
        userInfo.value = null
        roles.value = []
      }
    } catch (err) {
      console.error('[UserStore] fetchUser error:', err)
      user.value = null
      userInfo.value = null
      roles.value = []
    }
  }

  /**
   * Fetch full user info (name, full_name, etc.)
   */
  async function fetchUserInfo(email) {
    try {
      const response = await authAPI.getUserInfo(email)
      userInfo.value = response.data.data
      console.log('[UserStore] userInfo:', userInfo.value)
    } catch (err) {
      console.error('[UserStore] fetchUserInfo error:', err)
    }
  }

  /**
   * Fetch user roles
   */
  async function fetchRoles() {
    try {
      const response = await authAPI.getUserRoles()
      roles.value = response.data.message || []
    } catch (err) {
      roles.value = []
    }
  }

  /**
   * Check if user has specific role
   */
  function hasRole(role) {
    return roles.value.includes(role)
  }

  /**
   * Initialize store - call on app mount
   * Returns same promise if called multiple times concurrently
   */
  async function init() {
    // Already initialized
    if (initialized.value) {
      console.log('[UserStore] already initialized')
      return
    }
    
    // If init is in progress, return the existing promise
    if (initPromise) {
      console.log('[UserStore] init in progress, waiting...')
      return initPromise
    }
    
    console.log('[UserStore] init started')
    isLoading.value = true
    
    // Create and store the promise
    initPromise = (async () => {
      try {
        await fetchUser()
        console.log('[UserStore] init complete - user:', user.value, 'isLoggedIn:', isLoggedIn.value)
      } finally {
        isLoading.value = false
        initialized.value = true
        initPromise = null
      }
    })()
    
    return initPromise
  }

  return {
    // State
    user,
    userInfo,
    roles,
    isLoading,
    error,
    initialized,
    
    // Getters
    isLoggedIn,
    isAdmin,
    fullName,
    
    // Actions
    login,
    logout,
    fetchUser,
    hasRole,
    init
  }
})
