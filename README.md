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
│   Tailwind CSS      │  REST   │   Accounts, Setup...   │
└─────────────────────┘         └────────────────────────┘
```

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

- Hướng dẫn cài đặt: https://github.com/frappe/erpnext/

- Hướng dẫn kiểm tra:

```bash
# Kiểm tra ERPNext đã cài chưa
bench --site [your-site] list-apps
# Phải có: frappe, erpnext
```

## Cài đặt

### Bước 1: Clone repository

```bash
cd $PATH_TO_YOUR_BENCH
bench get-app git@github.com:selunenashor/xuanhoa_erp.git --branch main
```

Hoặc sử dụng HTTPS:
```bash
bench get-app https://github.com/selunenashor/xuanhoa_erp.git --branch main
```

### Bước 2: Cài đặt app vào site

```bash
# Cài vào site có sẵn ERPNext
bench --site [your-site] install-app xuanhoa_app

# Ví dụ:
bench --site erpnext.localhost install-app xuanhoa_app
```

### Bước 3: Build frontend assets

```bash
# Cài đặt dependencies frontend
cd apps/xuanhoa_app/frontend
npm install

# Build production
npm run build

# Quay lại bench root và build assets
cd $PATH_TO_YOUR_BENCH
bench build --app xuanhoa_app
```

### Bước 4: Khởi động lại bench

```bash
bench restart
# Hoặc trong development mode:
bench start
```

## Truy cập ứng dụng

Sau khi cài đặt thành công:

- **Xuân Hòa App (Frontend)**: `http://[your-site]:8000/manage`

## Cấu trúc dự án

```
xuanhoa_app/
├── xuanhoa_app/
│   ├── api.py              # API endpoints cho frontend
│   ├── hooks.py            # Cấu hình Frappe app
│   ├── public/
│   │   └── frontend/       # Vue.js build output
│   └── www/
│       └── manage.html     # SPA entry point
├── frontend/               # Vue.js source code
│   ├── src/
│   │   ├── api/            # API client (axios)
│   │   ├── pages/          # Page components
│   │   ├── router/         # Vue Router
│   │   └── stores/         # Pinia stores
│   ├── package.json
│   └── vite.config.js
├── pyproject.toml
└── README.md
```

## Phát triển

### Chạy development mode

**Terminal 1** - Frappe Backend:
```bash
cd $PATH_TO_YOUR_BENCH
bench start
```

**Terminal 2** - Vue Frontend (Hot Reload):
```bash
cd apps/xuanhoa_app/frontend
npm run dev
```

Truy cập frontend dev server tại: `http://localhost:5173`

### Code formatting

App này sử dụng `pre-commit` để kiểm tra và format code:

```bash
cd apps/xuanhoa_app
pre-commit install
```

Các công cụ được sử dụng:
- **ruff** - Python linter và formatter
- **eslint** - JavaScript/Vue linter
- **prettier** - Code formatter
