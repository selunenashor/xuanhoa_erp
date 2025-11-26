/**
 * User Store - Pinia
 */

import { defineStore } from 'pinia'
import { xuanhoaAPI } from '@/api/client'

export const useUserStore = defineStore('user', {
  state: () => ({
    user: null,
    isLoggedIn: false,
    loading: false
  }),

  actions: {
    async checkAuth() {
      try {
        this.loading = true
        const user = await xuanhoaAPI.getLoggedUser()
        if (user && user !== 'Guest') {
          this.user = user
          this.isLoggedIn = true
        } else {
          this.user = null
          this.isLoggedIn = false
        }
      } catch (error) {
        this.user = null
        this.isLoggedIn = false
      } finally {
        this.loading = false
      }
    },

    async login(username, password) {
      try {
        this.loading = true
        await xuanhoaAPI.login(username, password)
        await this.checkAuth()
        return { success: true }
      } catch (error) {
        return { success: false, message: error.message }
      } finally {
        this.loading = false
      }
    },

    async logout() {
      try {
        await xuanhoaAPI.logout()
        this.user = null
        this.isLoggedIn = false
      } catch (error) {
        console.error('Logout error:', error)
      }
    }
  }
})
