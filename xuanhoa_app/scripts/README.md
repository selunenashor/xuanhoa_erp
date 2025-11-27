# Hướng dẫn cài đặt dữ liệu mẫu - Xuân Hòa ERP

## ⚡ Quick Start

```bash
# Reset toàn bộ và cài lại từ đầu (RECOMMENDED)
bench --site erpnext.localhost execute xuanhoa_app.scripts.reset_all_data.run
```

## 📁 Cấu trúc thư mục

```
scripts/
├── README.md              # File hướng dẫn này
├── __init__.py
├── reset_all_data.py      # Script reset & import chính (RECOMMENDED)
├── import_data.py         # Script import dữ liệu (legacy)
├── import_bom.py          # Script import BOM riêng
├── create_users.py        # Script tạo users
└── example/               # Thư mục chứa dữ liệu mẫu CSV
    ├── company.csv
    ├── warehouse.csv
    ├── item.csv
    ├── item_group.csv
    ├── supplier.csv
    ├── supplier_group.csv
    ├── customer.csv
    ├── customer_group.csv
    ├── bom.csv
    ├── bom_item.csv
    └── ...
```

---

## 🚀 Cài đặt dữ liệu mẫu

### Cách 1: Reset toàn bộ (KHUYẾN NGHỊ cho môi trường mới)

Script này sẽ:
1. ✅ Thiết lập prerequisites (Currency VND, UOMs, Country Vietnam)
2. ✅ Xóa toàn bộ dữ liệu cũ (transactions, master data, companies, users)
3. ✅ Tạo Company mới: "Xuân Hòa Thái Bình" (XHTB)
4. ✅ **Set default company** cho tất cả users (tránh lỗi warehouse mismatch)
5. ✅ Tạo Users với đầy đủ roles
6. ✅ Import Warehouses, Items, BOMs (đã submit)
7. ✅ Tạo tồn kho ban đầu qua Stock Entry (đã submit)
8. ✅ Tạo Work Orders (Draft)
9. ✅ Verify cấu hình

```bash
bench --site erpnext.localhost execute xuanhoa_app.scripts.reset_all_data.run
```

### Cách 2: Chỉ import (không xóa dữ liệu cũ)

```bash
bench --site erpnext.localhost execute xuanhoa_app.scripts.reset_all_data.run_import_only
```

### Cách 3: Chỉ xóa dữ liệu

```bash
bench --site erpnext.localhost execute xuanhoa_app.scripts.reset_all_data.run_delete_only
```

### Cách 4: Kiểm tra cấu hình hiện tại

```bash
bench --site erpnext.localhost execute xuanhoa_app.scripts.reset_all_data.run_verify
```

---

## 👥 Danh sách Users mẫu

| Email | Password | Role | Mô tả |
|-------|----------|------|-------|
| `admin@xuanhoa.local` | `admin123` | System Manager | Quản trị hệ thống |
| `kho@xuanhoa.local` | `kho123` | Stock Manager | Quản lý kho |
| `sanxuat@xuanhoa.local` | `sanxuat123` | Manufacturing Manager | Quản lý sản xuất |

---

## 📦 Dữ liệu mẫu bao gồm

### Company
- **Xuân Hòa Thái Bình** (abbr: XHTB)

### Warehouses (thuộc đúng company XHTB)
- Kho Chính - XHTB (Nguyên vật liệu)
- Kho Thành Phẩm - XHTB (Thành phẩm)
- Kho WIP - XHTB (Work In Progress)

### Items
- **Nguyên vật liệu**: LED-5W, LED-10W, PCB-DRIVER, CAP-ALUMINUM, HEAT-SINK, WIRE-COPPER, BOX-PAPER
- **Thành phẩm**: LAMP-10W-50LED, LAMP-5W-30LED, SPOTLIGHT-30W

### Tồn kho ban đầu
| Item | Kho | Số lượng | Đơn giá |
|------|-----|----------|---------|
| LED-5W | Kho Chính | 1000 | 5,000 |
| LED-10W | Kho Chính | 800 | 8,000 |
| PCB-DRIVER | Kho Chính | 400 | 12,000 |
| CAP-ALUMINUM | Kho Chính | 1000 | 3,000 |
| HEAT-SINK | Kho Chính | 600 | 8,000 |
| WIRE-COPPER | Kho Chính | 50 | 50,000 |
| LAMP-10W-50LED | Kho Thành Phẩm | 50 | 150,000 |
| SPOTLIGHT-30W | Kho Thành Phẩm | 30 | 250,000 |

### BOMs (đã submit)
- BOM-LAMP-10W-50LED-001
- BOM-LAMP-5W-30LED-001
- BOM-SPOTLIGHT-30W-001

### Work Orders (Draft)
- LAMP-10W-50LED x 100
- SPOTLIGHT-30W x 50

---

## ⚠️ Lỗi thường gặp và cách xử lý

### 1. Lỗi "Warehouse does not belong to company"

**Nguyên nhân**: Warehouse thuộc company khác với company trên phiếu.

**Giải pháp**: Script `reset_all_data.py` đã xử lý bằng cách:
- Tất cả warehouses được tạo với đúng company "Xuân Hòa Thái Bình"
- Default company được set cho tất cả users
- Verify sau khi import để đảm bảo không có warehouse nào thuộc company khác

### 2. Lỗi "Default Company not set"

**Nguyên nhân**: User chưa có default company.

**Giải pháp**: Script đã tự động set default company trong:
- Global Defaults
- System default (__default)
- Từng user cụ thể

### 3. Stock Entry không tạo Stock Ledger Entry

**Nguyên nhân**: Warehouse không khớp company trên Stock Entry.

**Giải pháp**: Script đã đảm bảo:
- Company trên Stock Entry = "Xuân Hòa Thái Bình"
- Tất cả warehouses thuộc company "Xuân Hòa Thái Bình"

### 4. Lỗi "UOM not found"

**Nguyên nhân**: UOM chưa được tạo trong hệ thống.

**Giải pháp**: Script tự động tạo các UOM cần thiết trong `setup_prerequisites()`:
- Nos, Set, Box, Roll, Kg, Meter

---

## 🔧 Tùy chỉnh dữ liệu

### Thay đổi Company

Chỉnh sửa trong file `reset_all_data.py`:

```python
COMPANY_NAME = 'Tên Công Ty Mới'
COMPANY_ABBR = 'TCT'
```

### Thêm Item mới

Chỉnh sửa file `example/item.csv`:
```csv
Item Code,Item Name,Item Group,Default Unit of Measure,Is Stock Item,Standard Selling Rate
NEW-ITEM-001,Tên sản phẩm mới,Nguyên vật liệu,Cái,1,10000
```

### Thêm tồn kho ban đầu

Chỉnh sửa trong `reset_all_data.py`, phần `INITIAL_STOCK`:
```python
INITIAL_STOCK = [
    {'item_code': 'NEW-ITEM-001', 'qty': 100, 'rate': 10000, 'warehouse': 'Kho Chính'},
    ...
]
```

---

## 📞 Debug

Nếu gặp lỗi, kiểm tra:

```bash
# 1. Xem log chi tiết
bench --site erpnext.localhost execute xuanhoa_app.scripts.reset_all_data.run 2>&1 | tee import.log

# 2. Kiểm tra cấu hình
bench --site erpnext.localhost execute xuanhoa_app.scripts.reset_all_data.run_verify

# 3. Kiểm tra trong console
bench --site erpnext.localhost console
>>> frappe.defaults.get_user_default("Company")
>>> frappe.get_all("Warehouse", filters={"company": "Xuân Hòa Thái Bình"}, pluck="name")
>>> frappe.get_all("Bin", fields=["item_code", "warehouse", "actual_qty"])
```

---

## 🔄 Chạy lại từ đầu

```bash
# Backup (optional)
bench --site erpnext.localhost backup

# Reset
bench --site erpnext.localhost execute xuanhoa_app.scripts.reset_all_data.run

# Clear cache
bench --site erpnext.localhost clear-cache

# Đăng nhập lại vào hệ thống
```
