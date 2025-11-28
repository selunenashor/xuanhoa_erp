/**
 * API Service Module
 * Re-exports all API modules for centralized access
 * 
 * Structure:
 * - client.js: Axios instance with interceptors
 * - auth.js: Authentication APIs
 * - stock.js: Stock, Warehouse APIs  
 * - production.js: Work Orders, BOMs APIs
 * - invoice.js: Purchase/Sales Invoice APIs
 * - master.js: Items, Item Groups, UOMs, Suppliers, Customers APIs
 * - dashboard.js: Dashboard KPIs, Activities APIs
 * - resource.js: Generic CRUD operations
 */

// Default API client
export { default } from './client'
export { default as api } from './client'

// Auth
export { authAPI } from './auth'

// Stock & Warehouse
export { stockAPI, warehouseAPI, warehouseStockAPI } from './stock'

// Production
export { workOrderAPI, bomAPI } from './production'

// Invoices
export { purchaseInvoiceAPI, salesInvoiceAPI } from './invoice'

// Master Data
export { itemAPI, itemGroupAPI, uomAPI, supplierAPI, customerAPI } from './master'

// Dashboard
export { dashboardAPI, paymentAPI } from './dashboard'

// Generic Resource
export { resourceAPI, customAPI } from './resource'
