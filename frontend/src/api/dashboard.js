/**
 * Dashboard API Module
 * Dashboard KPI and activity related API calls
 */

import api from './client'

export const dashboardAPI = {
  /**
   * Get KPI data for dashboard
   */
  getKPI: async () => {
    const res = await api.post('/method/xuanhoa_app.api.get_dashboard_kpi')
    return res.data.message
  },

  /**
   * Get recent activities for dashboard
   */
  getRecentActivities: async (limit = 10) => {
    const res = await api.post('/method/xuanhoa_app.api.get_recent_activities', { limit })
    return res.data.message
  }
}

export const paymentAPI = {
  /**
   * Get list of payment modes
   */
  getModes: async () => {
    const res = await api.post('/method/xuanhoa_app.api.get_mode_of_payments')
    return res.data.message
  }
}
