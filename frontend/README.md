# Xuân Hòa Manufacturing Frontend

> Vue.js 3 frontend cho hệ thống quản lý sản xuất Xuân Hòa

## Tech Stack

- **Vue.js 3** - Composition API với `<script setup>`
- **Tailwind CSS v4** - Utility-first CSS framework
- **Vite** - Next generation frontend build tool
- **Vue Router** - Client-side routing
- **Pinia** - State management
- **Axios** - HTTP client

## Cấu trúc thư mục

```
frontend/
├── src/
│   ├── api/                  # API modules
│   │   ├── client.js         # Axios instance với interceptors
│   │   ├── auth.js           # Authentication APIs
│   │   ├── stock.js          # Stock, Warehouse APIs
│   │   ├── production.js     # Work Orders, BOMs APIs
│   │   ├── invoice.js        # Purchase/Sales Invoice APIs
│   │   ├── master.js         # Items, Suppliers, Customers APIs
│   │   ├── dashboard.js      # Dashboard KPIs APIs
│   │   ├── resource.js       # Generic CRUD APIs
│   │   └── index.js          # Re-exports tất cả modules
│   ├── components/
│   │   └── layouts/
│   │       └── MainLayout.vue
│   ├── pages/
│   │   ├── Dashboard.vue
│   │   ├── Login.vue
│   │   ├── stock/            # Nhập/Xuất kho, Danh sách phiếu
│   │   ├── production/       # Work Orders, BOMs
│   │   ├── purchasing/       # Purchase Invoices
│   │   ├── selling/          # Sales Invoices
│   │   └── master/           # Items, Item Groups
│   ├── router/
│   │   └── index.js          # Route definitions
│   ├── stores/
│   │   └── user.js           # User authentication store
│   ├── App.vue
│   ├── main.js
│   └── style.css             # Tailwind CSS với custom theme
├── index.html
├── package.json
├── vite.config.js
└── README.md
```

## Development

### Cài đặt dependencies

```bash
npm install
```

### Chạy development server

```bash
npm run dev
```

Truy cập: http://localhost:5173

> **Lưu ý**: Cần chạy `bench start` ở terminal khác để có backend API

### Build production

```bash
npm run build
```

Output sẽ được tạo tại `../xuanhoa_app/public/frontend/`

## Authentication

App sử dụng **session-based authentication**:

- Login thành công → set marker vào `sessionStorage`
- Đóng trình duyệt → phải login lại
- Refresh trang / mở tab mới → giữ session

## API Modules

### Cách import

```javascript
// Import từng module
import { authAPI, stockAPI, itemAPI } from '@/api'

// Hoặc import default axios instance
import api from '@/api'
```

### Các modules có sẵn

| Module | Chức năng |
|--------|-----------|
| `authAPI` | Login, logout, get user info |
| `stockAPI` | Material receipt/issue, stock entries |
| `warehouseAPI` | Warehouse list |
| `warehouseStockAPI` | Stock by warehouse, stock ledger |
| `workOrderAPI` | Work order CRUD, actions |
| `bomAPI` | BOM CRUD |
| `purchaseInvoiceAPI` | Purchase invoice CRUD, payment |
| `salesInvoiceAPI` | Sales invoice CRUD, payment |
| `itemAPI` | Item CRUD, search |
| `itemGroupAPI` | Item group CRUD |
| `supplierAPI` | Supplier list |
| `customerAPI` | Customer list |
| `dashboardAPI` | KPIs, recent activities |
| `paymentAPI` | Payment modes |
| `resourceAPI` | Generic Frappe CRUD |
| `customAPI` | Call custom methods |

## Routing

| Path | Page | Mô tả |
|------|------|-------|
| `/` | Dashboard | Tổng quan |
| `/login` | Login | Đăng nhập |
| `/stock/receipt` | MaterialReceipt | Tạo phiếu nhập |
| `/stock/issue` | MaterialIssue | Tạo phiếu xuất |
| `/stock/entries` | StockEntryList | DS phiếu kho |
| `/stock/entries/:name` | StockEntryDetail | Chi tiết phiếu |
| `/stock/warehouses` | WarehouseStock | Quản lý kho |
| `/production/orders` | WorkOrderList | DS lệnh SX |
| `/production/orders/create` | WorkOrderCreate | Tạo lệnh SX |
| `/production/orders/:name` | WorkOrderDetail | Chi tiết lệnh |
| `/production/boms` | BOMList | Định mức NVL |
| `/purchasing/invoices` | PurchaseInvoiceList | DS hóa đơn mua |
| `/purchasing/invoices/create` | PurchaseInvoiceCreate | Tạo HĐ mua |
| `/purchasing/invoices/:name` | PurchaseInvoiceDetail | Chi tiết HĐ mua |
| `/selling/invoices` | SalesInvoiceList | DS hóa đơn bán |
| `/selling/invoices/create` | SalesInvoiceCreate | Tạo HĐ bán |
| `/selling/invoices/:name` | SalesInvoiceDetail | Chi tiết HĐ bán |
| `/master/items` | ItemList | Quản lý sản phẩm |

## Tailwind CSS Theme

Custom theme được định nghĩa trong `src/style.css`:

```css
@theme {
  --color-primary: #055568;
  --color-primary-light: #0d9488;
  --color-primary-dark: #134e4a;
  --color-secondary: #33CAB1;
  --color-accent: #33CAB1;
  /* ... */
}
```

## License

MIT
