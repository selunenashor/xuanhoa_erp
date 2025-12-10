# Xuân Hòa Manufacturing App

Dự án này chỉ mô phỏng quá trình số hóa cho một quy trình sản xuất cơ bản, bao gồm **mua hàng**, **sản xuất** và **bán hàng**. 

---
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

## Tính năng Frontend

### Các giao diện đã hoàn thành ✅

| Module | Trang | Route | Mô tả |
|--------|-------|-------|-------|
| **Tổng quan** | Dashboard | `/` | KPIs, thao tác nhanh, hoạt động gần đây |
| | Dashboard Mua/Bán | `/sales-purchase/dashboard` | Thống kê mua bán |
| **Kho hàng** | Dashboard Kho | `/stock/dashboard` | Thống kê tồn kho |
| | Nhập kho | `/stock/receipt` | Tạo phiếu nhập nhiều sản phẩm |
| | Xuất kho | `/stock/issue` | Tạo phiếu xuất nhiều sản phẩm |
| | Danh sách phiếu | `/stock/entries` | Xem, lọc, tìm kiếm phiếu kho |
| | Chi tiết phiếu | `/stock/entries/:name` | Xem chi tiết, submit/cancel phiếu |
| | Quản lý kho | `/stock/warehouses` | Xem tồn kho theo kho/sản phẩm |
| **Sản xuất** | Dashboard SX | `/production/dashboard` | Thống kê sản xuất |
| | Danh sách lệnh SX | `/production/orders` | Danh sách Work Orders |
| | Tạo lệnh SX | `/production/orders/create` | Tạo mới Work Order |
| | Chi tiết lệnh SX | `/production/orders/:name` | Chi tiết, start, complete, cancel |
| | Định mức NVL | `/production/boms` | Quản lý BOM (tạo, sửa, xóa) |
| **Mua hàng** | Danh sách HĐ mua | `/purchasing/invoices` | Danh sách Purchase Invoice |
| | Tạo HĐ mua | `/purchasing/invoices/create` | Tạo hóa đơn mua hàng |
| | Chi tiết HĐ mua | `/purchasing/invoices/:name` | Chi tiết, submit, cancel, thanh toán |
| **Bán hàng** | Danh sách HĐ bán | `/selling/invoices` | Danh sách Sales Invoice |
| | Tạo HĐ bán | `/selling/invoices/create` | Tạo hóa đơn bán hàng |
| | Chi tiết HĐ bán | `/selling/invoices/:name` | Chi tiết, submit, cancel, thanh toán |
| **Danh mục** | Quản lý sản phẩm | `/master/items` | CRUD Items |
| **Hệ thống** | Đăng nhập | `/login` | Xác thực người dùng |

### Đang phát triển 🚧

- Bulk import data từ file Excel
- Xuất phiếu/hóa đơn ra file PDF/Word
- Báo cáo thống kê chi tiết
- Notification system

## Doctypes sử dụng

Dự án sử dụng các Doctypes có sẵn từ ERPNext, được phân theo module:

### 📦 Module Stock (Kho hàng)

| Doctype | Mô tả | Sử dụng trong |
|---------|-------|---------------|
| `Item` | Sản phẩm/Nguyên vật liệu | Danh mục sản phẩm, BOM, phiếu kho |
| `Item Group` | Nhóm sản phẩm | Phân loại sản phẩm |
| `Warehouse` | Kho hàng | Quản lý vị trí lưu trữ |
| `Stock Entry` | Phiếu kho (Nhập/Xuất/Chuyển) | Nhập kho, Xuất kho, Sản xuất |
| `Stock Entry Detail` | Chi tiết phiếu kho | Dòng sản phẩm trong phiếu |
| `UOM` | Đơn vị tính | Định nghĩa đơn vị (cái, kg, m...) |
| `Bin` | Tồn kho theo kho | Tra cứu tồn kho realtime |

### 🏭 Module Manufacturing (Sản xuất)

| Doctype | Mô tả | Sử dụng trong |
|---------|-------|---------------|
| `BOM` (Bill of Materials) | Định mức nguyên vật liệu | Công thức sản xuất sản phẩm |
| `BOM Item` | Chi tiết BOM | Danh sách NVL trong BOM |
| `Work Order` | Lệnh sản xuất | Quản lý quá trình sản xuất |

### 💰 Module Accounts (Kế toán)

| Doctype | Mô tả | Sử dụng trong |
|---------|-------|---------------|
| `Purchase Invoice` | Hóa đơn mua hàng | Ghi nhận mua NVL từ NCC |
| `Purchase Invoice Item` | Chi tiết HĐ mua | Dòng sản phẩm trong HĐ mua |
| `Sales Invoice` | Hóa đơn bán hàng | Ghi nhận bán hàng cho KH |
| `Sales Invoice Item` | Chi tiết HĐ bán | Dòng sản phẩm trong HĐ bán |
| `Payment Entry` | Phiếu thanh toán | Thanh toán cho HĐ mua/bán |

### 👥 Module Buying & Selling (Đối tác)

| Doctype | Mô tả | Sử dụng trong |
|---------|-------|---------------|
| `Supplier` | Nhà cung cấp | Hóa đơn mua hàng |
| `Customer` | Khách hàng | Hóa đơn bán hàng |

### ⚙️ Module Setup (Cấu hình)

| Doctype | Mô tả | Sử dụng trong |
|---------|-------|---------------|
| `Company` | Công ty | Thông tin công ty chủ quản |
| `User` | Người dùng | Đăng nhập, phân quyền |

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

⚠️ **QUAN TRỌNG**: App này **yêu cầu ERPNext** đã được cài đặt và được thiết lập cơ bản trên site.

```bash
# Kiểm tra ERPNext đã cài chưa
bench --site [your-site] list-apps
# Phải có: frappe, erpnext
```

## Cài đặt

### Bước 1: Clone repository

```bash
cd \$PATH_TO_YOUR_BENCH
bench get-app https://github.com/selunenashor/xuanhoa_erp.git --branch main
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
