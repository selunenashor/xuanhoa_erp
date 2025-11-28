# Xuân Hòa Manufacturing App

> Ứng dụng quản lý sản xuất tùy chỉnh cho Công ty Xuân Hòa, xây dựng trên nền tảng Frappe/ERPNext theo kiến trúc Headless ERP.

## Tổng quan

Xuân Hòa Manufacturing App là một custom Frappe app cung cấp:
- **Frontend Vue.js** - Giao diện người dùng hiện đại, tối ưu cho mobile
- **API Wrapper** - Các endpoint đơn giản hóa thao tác với ERPNext
- **Tích hợp ERPNext** - Sử dụng toàn bộ modules Stock, Manufacturing, Accounts từ ERPNext

### Kiến trúc

```
┌─────────────────────┐         ┌────────────────────────┐
│   Vue.js Frontend   │   API   │   ERPNext (Backend)    │
│   (/manage)         │◄───────►│   Stock, Manufacturing │
│   Tailwind CSS v4   │  REST   │   Accounts, Setup...   │
└─────────────────────┘         └────────────────────────┘
```

## Tính năng

### Đã hoàn thành ✅

| Module | Tính năng | Mô tả |
|--------|-----------|-------|
| **Dashboard** | Tổng quan | KPIs, thao tác nhanh, hoạt động gần đây |
| **Kho** | Nhập kho | Tạo phiếu nhập nhiều sản phẩm |
| | Xuất kho | Tạo phiếu xuất nhiều sản phẩm |
| | Danh sách phiếu | Xem, lọc, tìm kiếm phiếu kho |
| | Chi tiết phiếu | Xem chi tiết, submit/cancel phiếu |
| | Quản lý kho | Xem tồn kho theo kho/sản phẩm |
| **Sản xuất** | Lệnh sản xuất | CRUD, submit, start, complete, cancel |
| | Định mức NVL | Quản lý BOM (tạo, sửa, xóa) |
| **Giao dịch** | Hóa đơn mua | CRUD, submit, cancel, thanh toán |
| | Hóa đơn bán | CRUD, submit, cancel, thanh toán |
| **Danh mục** | Sản phẩm | CRUD Items, Item Groups |
| | Kho hàng | Xem danh sách kho |

### Đang phát triển 🚧

- Báo cáo thống kê
- Quản lý Supplier/Customer  
- Notification system

## Yêu cầu hệ thống

### Phiên bản Framework

| Framework | Phiên bản | Ghi chú |
|-----------|-----------|---------|
| Python | 3.10+ | Khuyến nghị 3.12 |
| Node.js | 18+ | Sử dụng cho frontend build |
| MariaDB | 10.6+ | Database backend |
| Redis | 6+ | Cache và queue |
| Frappe | v15.x | Core framework |
| ERPNext | v15.x | **BẮT BUỘC** - Phải cài trước |

### Điều kiện tiên quyết

⚠️ **QUAN TRỌNG**: App này **yêu cầu ERPNext** đã được cài đặt và hoạt động trên site trước khi cài đặt.

```bash
# Kiểm tra ERPNext đã cài chưa
bench --site [your-site] list-apps
# Phải có: frappe, erpnext
```

## Cài đặt

### Bước 1: Clone repository

```bash
cd \$PATH_TO_YOUR_BENCH
bench get-app git@github.com:selunenashor/xuanhoa_erp.git --branch main
```

### Bước 2: Cài đặt app vào site

```bash
bench --site [your-site] install-app xuanhoa_app
```

### Bước 3: Build frontend assets

```bash
cd apps/xuanhoa_app/frontend
npm install
npm run build

cd \$PATH_TO_YOUR_BENCH
bench build --app xuanhoa_app
```

### Bước 4: Khởi động lại bench

```bash
bench restart
```

## Truy cập ứng dụng

- **Frontend**: \`http://[your-site]:8000/manage\`

## Cấu trúc dự án

```
xuanhoa_app/
├── xuanhoa_app/
│   ├── api.py                # API endpoints cho frontend
│   ├── hooks.py              # Cấu hình Frappe app
│   ├── scripts/              # Scripts import data mẫu
│   │   ├── reset_all_data.py
│   │   ├── import_data.py
│   │   └── example/          # CSV data files
│   ├── public/
│   │   └── frontend/         # Vue.js build output
│   └── www/
│       └── manage.html       # SPA entry point
├── frontend/                 # Vue.js source code
│   ├── src/
│   │   ├── api/              # API modules (modular)
│   │   │   ├── client.js     # Axios instance
│   │   │   ├── auth.js       # Authentication
│   │   │   ├── stock.js      # Stock operations
│   │   │   ├── production.js # Work Orders, BOMs
│   │   │   ├── invoice.js    # Purchase/Sales invoices
│   │   │   ├── master.js     # Items, Suppliers, Customers
│   │   │   ├── dashboard.js  # Dashboard KPIs
│   │   │   └── index.js      # Re-exports
│   │   ├── components/       # Reusable components
│   │   │   └── layouts/      # MainLayout
│   │   ├── pages/            # Page components
│   │   ├── router/           # Vue Router
│   │   └── stores/           # Pinia stores
│   ├── package.json
│   └── vite.config.js
├── pyproject.toml
└── README.md
```

## Phát triển

### Chạy development mode

**Terminal 1** - Frappe Backend:
```bash
cd \$PATH_TO_YOUR_BENCH
bench start
```

**Terminal 2** - Vue Frontend (Hot Reload):
```bash
cd apps/xuanhoa_app/frontend
npm run dev
```

### Build production

```bash
cd apps/xuanhoa_app/frontend
npm run build
```

## Dữ liệu mẫu

Xem hướng dẫn chi tiết tại: [scripts/README.md](./xuanhoa_app/scripts/README.md)

### Quick Start

```bash
# Setup toàn bộ dữ liệu mẫu (1 lệnh)
bench --site erpnext.localhost execute xuanhoa_app.scripts.reset_all_data.setup_all
```

### Users mặc định

| Email | Password | Role |
|-------|----------|------|
| admin@xuanhoa.local | admin123 | System Manager |
| admin2@xuanhoa.local | admin123 | System Manager |

## Tech Stack

### Frontend
- **Vue.js 3** - Composition API
- **Tailwind CSS v4** - Utility-first CSS
- **Vite** - Build tool
- **Vue Router** - Client-side routing
- **Pinia** - State management
- **Axios** - HTTP client

### Backend
- **Frappe Framework v15**
- **ERPNext v15**
- **Python 3.12**
- **MariaDB**
- **Redis**

## License

MIT
