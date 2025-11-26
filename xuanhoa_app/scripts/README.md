# Hướng dẫn cài đặt dữ liệu mẫu - Xuân Hòa ERP

## 📁 Cấu trúc thư mục

```
scripts/
├── README.md              # File hướng dẫn này
├── __init__.py
├── import_data.py         # Script import dữ liệu chính
├── import_bom.py          # Script import BOM riêng
├── create_users.py        # Script tạo users
└── example/               # Thư mục chứa dữ liệu mẫu CSV
    ├── item.csv
    ├── item_group.csv
    ├── warehouse.csv
    ├── supplier.csv
    ├── customer.csv
    ├── bom.csv
    ├── bom_item.csv
    ├── work_order.csv
    ├── purchase_receipt.csv
    ├── purchase_receipt_item.csv
    ├── stock_entry.csv
    ├── stock_entry_item.csv
    ├── role_permission.csv
    └── ...
```

---

## 🚀 Cài đặt dữ liệu mẫu

### Cách 1: Import đầy đủ (Khuyến nghị)

Chạy lệnh sau để import toàn bộ dữ liệu mẫu:

```bash
cd /path/to/bench
bench --site erpnext.localhost execute xuanhoa_app.scripts.import_data.run
```

Script này sẽ thực hiện:
1. ✅ Thiết lập Role Permissions
2. ✅ Tạo Users với đầy đủ roles
3. ✅ Xóa dữ liệu cũ (nếu có)
4. ✅ Import Item Groups, Supplier Groups, Customer Groups
5. ✅ Import Warehouses, Suppliers, Customers
6. ✅ Import Items (Nguyên vật liệu + Thành phẩm)
7. ✅ Import BOMs (đã submit)
8. ✅ Import Work Orders (draft)
9. ✅ Import Purchase Receipts (đã submit - cập nhật tồn kho)

### Cách 2: Chỉ setup Permissions và Users

```bash
bench --site erpnext.localhost execute xuanhoa_app.scripts.import_data.run_permissions_only
```

### Cách 3: Chỉ tạo Users

```bash
bench --site erpnext.localhost execute xuanhoa_app.scripts.import_data.run_users_only
```

Hoặc sử dụng script riêng:

```bash
bench --site erpnext.localhost execute xuanhoa_app.scripts.create_users.run
```

---

## 👥 Danh sách Users mẫu

Sau khi chạy script, các users sau sẽ được tạo:

| Email | Password | Role | Mô tả |
|-------|----------|------|-------|
| `admin@xuanhoa.local` | `admin123` | System Manager | Quản trị hệ thống |
| `kho@xuanhoa.local` | `kho123` | Stock Manager | Quản lý kho |
| `sanxuat@xuanhoa.local` | `sanxuat123` | Manufacturing Manager | Quản lý sản xuất |
| `muahang@xuanhoa.local` | `muahang123` | Purchase Manager | Quản lý mua hàng |
| `banhang@xuanhoa.local` | `banhang123` | Sales Manager | Quản lý bán hàng |
| `ketoan@xuanhoa.local` | `ketoan123` | Accounts Manager | Quản lý kế toán |

---

## 📦 Dữ liệu mẫu bao gồm

### Item Groups (Nhóm sản phẩm)
- Nguyên vật liệu
- Linh kiện điện tử
- Thành phẩm
- Bán thành phẩm

### Items (Sản phẩm)
- **Nguyên vật liệu**: LED, IC Driver, PCB, Tụ điện, Điện trở, Nhựa ABS, Dây điện...
- **Thành phẩm**: Đèn LED 10W, Đèn Chiếu Sáng 30W...

### Warehouses (Kho)
- Kho Nguyên Vật Liệu - XHTB
- Kho Thành Phẩm - XHTB
- Kho WIP (Work In Progress) - XHTB

### Suppliers (Nhà cung cấp)
- NCC Linh kiện điện tử
- NCC Nhựa & Kim loại
- NCC Đèn LED

### Customers (Khách hàng)
- Đại lý miền Bắc
- Đại lý miền Trung
- Đại lý miền Nam
- Khách lẻ

### BOM (Bill of Materials)
- BOM cho Đèn LED 10W (50 LED)
- BOM cho Đèn Chiếu Sáng 30W

### Purchase Receipts (Phiếu nhập kho)
- Nhập NVL từ nhà cung cấp (đã submit - có tồn kho)

### Work Orders (Lệnh sản xuất)
- Lệnh SX Đèn LED 10W (draft - sẵn sàng submit)

---

## 🔐 Phân quyền (Role Permissions)

Permissions được thiết lập qua file `example/role_permission.csv`:

| DocType | System Manager | Stock Manager | Manufacturing Manager |
|---------|----------------|---------------|----------------------|
| Item | Full | Read/Write | Read |
| Stock Entry | Full | Full | Full |
| BOM | Full | Read | Full |
| Work Order | Full | Read | Full |
| Purchase Receipt | Full | Full | Read |
| Warehouse | Full | Read | Read |

---

## ⚠️ Lưu ý quan trọng

1. **Backup trước khi chạy**: Script sẽ xóa dữ liệu cũ của company
   ```bash
   bench --site erpnext.localhost backup
   ```

2. **Company mặc định**: Script sử dụng company `Xuân Hòa Thái Bình`. Đảm bảo company này đã tồn tại.

3. **Suffix Warehouse**: Kho sẽ được tạo với suffix ` - XHTB` (abbreviation của company)

4. **BOM đã submit**: BOMs được submit ngay sau khi tạo để có thể sử dụng trong Work Orders

5. **Tồn kho ban đầu**: Purchase Receipts được submit để tạo tồn kho NVL ban đầu

---

## 🔄 Chạy lại từ đầu

Nếu muốn reset và import lại từ đầu:

```bash
# 1. Backup (optional)
bench --site erpnext.localhost backup

# 2. Chạy lại script (sẽ tự động xóa dữ liệu cũ)
bench --site erpnext.localhost execute xuanhoa_app.scripts.import_data.run
```

---

## 🛠️ Tùy chỉnh dữ liệu mẫu

### Thêm Item mới
Chỉnh sửa file `example/item.csv`:
```csv
Item Code,Item Name,Item Group,Default Unit of Measure,Is Stock Item,Standard Selling Rate
NEW-ITEM-001,Tên sản phẩm mới,Nguyên vật liệu,Cái,1,10000
```

### Thêm BOM mới
1. Thêm vào `example/bom.csv`:
```csv
BOM ID,Item,Quantity,UOM
BOM-NEW-001,NEW-PRODUCT,1,Cái
```

2. Thêm items vào `example/bom_item.csv`:
```csv
BOM ID,Item Code,Quantity,Unit of Measure,Rate Per Unit
BOM-NEW-001,NVL-001,10,Cái,1000
BOM-NEW-001,NVL-002,5,Cái,500
```

### Đơn vị tính (UOM)
Script tự động convert UOM tiếng Việt sang tiếng Anh:
- Cái → Nos
- Bộ → Set
- Hộp → Box
- Cuộn → Roll
- Kg → Kg
- Mét → Meter

---

## 📞 Hỗ trợ

Nếu gặp lỗi khi import, kiểm tra:
1. Company `Xuân Hòa Thái Bình` đã tồn tại
2. Các UOM tiêu chuẩn đã được tạo (Nos, Set, Box, Roll, Kg, Meter)
3. Log lỗi trong terminal để xác định vấn đề cụ thể

```bash
# Xem log chi tiết
bench --site erpnext.localhost execute xuanhoa_app.scripts.import_data.run 2>&1 | tee import.log
```
