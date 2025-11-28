/**
 * User Store
 * Manages authentication state and user info
 * 
 * Session-based auth: User must re-login when browser is closed
 * Uses sessionStorage to persist state only within browser session
 */

import { defineStore } from 'pinia'
import { ref, computed, watch } from 'vue'
import { authAPI } from '@/api'

// Session storage key
const SESSION_KEY = 'xuanhoa_session'

export const useUserStore = defineStore('user', () => {
  // ==================== STATE ====================
  
  const user = ref(null)
  const userInfo = ref(null)  // Store full user info
  const roles = ref([])
  const isLoading = ref(false)
  const error = ref(null)
  const initialized = ref(false)  // Track if init has been called
  const sessionValid = ref(false) // Track if session is valid in this browser session
  let initPromise = null  // Promise to handle concurrent init calls

  // ==================== SESSION HELPERS ====================
  
  /**
   * Check if we have a valid session marker in sessionStorage
   * This marker is set on successful login and cleared on logout/browser close
   */
  function hasSessionMarker() {
    try {
      return sessionStorage.getItem(SESSION_KEY) === 'active'
    } catch {
      return false
    }
  }
  
  /**
   * Set session marker on successful login
   */
  function setSessionMarker() {
    try {
      sessionStorage.setItem(SESSION_KEY, 'active')
      sessionValid.value = true
    } catch (e) {
      console.warn('[UserStore] Failed to set session marker:', e)
    }
  }
  
  /**
   * Clear session marker on logout
   */
  function clearSessionMarker() {
    try {
      sessionStorage.removeItem(SESSION_KEY)
      sessionValid.value = false
    } catch (e) {
      console.warn('[UserStore] Failed to clear session marker:', e)
    }
  }

  // ==================== GETTERS ====================
  
  const isLoggedIn = computed(() => !!user.value && user.value !== 'Guest' && sessionValid.value)
  
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
      // Set session marker BEFORE fetching user
      setSessionMarker()
      await fetchUser()
      return { success: true }
    } catch (err) {
      // Clear session marker on failed login
      clearSessionMarker()
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
      // Always clear local state and session marker
      user.value = null
      userInfo.value = null
      roles.value = []
      clearSessionMarker()
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
   * 
   * Session-based logic:
   * - If no session marker exists (browser was closed/new tab), user must login
   * - If session marker exists, verify with server and restore session
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
        // Check if we have a session marker (browser session still active)
        if (hasSessionMarker()) {
          console.log('[UserStore] Session marker found, verifying with server...')
          sessionValid.value = true
          await fetchUser()
          
          // If server says user is logged in, keep session valid
          // If server says Guest, clear session (server session expired)
          if (!user.value || user.value === 'Guest') {
            console.log('[UserStore] Server session expired, clearing local session')
            clearSessionMarker()
          }
        } else {
          console.log('[UserStore] No session marker, user must login')
          // No session marker = new browser session, don't auto-login
          user.value = null
          userInfo.value = null
          roles.value = []
          sessionValid.value = false
        }
        
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
    sessionValid,
    
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
