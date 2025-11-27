# Hướng dẫn cài đặt dữ liệu mẫu - Xuân Hòa ERP

## ⚠️ YÊU CẦU BẮT BUỘC

> **QUAN TRỌNG**: Trước khi chạy bất kỳ script nào, bạn **PHẢI** chạy `bench start` ở một terminal khác!
>
> ```bash
> # Terminal 1: Khởi động bench (PHẢI chạy trước)
> cd /path/to/frappe-bench
> bench start
> ```
>
> Sau đó mới mở Terminal 2 để chạy các lệnh import/reset bên dưới.

---

## ⚡ Quick Start - Cài đặt 1 lệnh duy nhất

```bash
# Terminal 2: Setup toàn bộ hệ thống
bench --site erpnext.localhost execute xuanhoa_app.scripts.reset_all_data.setup_all
```

Lệnh này sẽ tự động:
1. ✅ Reset toàn bộ dữ liệu (xóa và tạo lại)
2. ✅ Tạo Company: Xuân Hòa Thái Bình (XHTB)
3. ✅ Tạo 6 Users với đầy đủ roles và permissions
4. ✅ Import Warehouses, Items, Suppliers, Customers
5. ✅ Import Item Prices (giá mua + giá bán)
6. ✅ Setup Bank Accounts và Mode of Payment
7. ✅ Import BOMs và tạo Work Orders mẫu
8. ✅ Tạo tồn kho ban đầu

---

## 📁 Cấu trúc thư mục

```
scripts/
├── README.md              # File hướng dẫn này
├── __init__.py
├── reset_all_data.py      # Script reset & import chính (RECOMMENDED)
├── import_data.py         # Script import dữ liệu + thiết lập accounting
├── import_bom.py          # Script import BOM riêng
├── create_users.py        # Script tạo users
└── example/               # Thư mục chứa dữ liệu mẫu CSV
    ├── company.csv
    ├── warehouse.csv
    ├── item.csv
    ├── item_group.csv
    ├── item_price.csv     # Giá mua/bán cho items
    ├── supplier.csv
    ├── supplier_group.csv
    ├── customer.csv
    ├── customer_group.csv
    ├── bom.csv
    ├── bom_item.csv
    ├── account.csv
    ├── mode_of_payment.csv
    ├── mode_of_payment_account.csv
    ├── role_permission.csv
    ├── user.csv
    ├── user_role.csv
    └── ...
```

---

## 🚀 Cài đặt dữ liệu mẫu

### Cách 1: Setup toàn bộ (KHUYẾN NGHỊ - 1 lệnh duy nhất)

```bash
# ⚠️ Đảm bảo bench start đang chạy ở terminal khác!
bench --site erpnext.localhost execute xuanhoa_app.scripts.reset_all_data.setup_all
```

### Cách 2: Reset dữ liệu cơ bản (chỉ 3 users)

Script này sẽ:
1. ✅ Thiết lập prerequisites (Currency VND, UOMs, Country Vietnam)
2. ✅ Xóa toàn bộ dữ liệu cũ (transactions, master data, companies, users)
3. ✅ Tạo Company mới: "Xuân Hòa Thái Bình" (XHTB)
4. ✅ **Set default company** cho tất cả users (tránh lỗi warehouse mismatch)
5. ✅ Tạo 3 Users cơ bản (admin, kho, sanxuat)
6. ✅ Import Warehouses, Items, BOMs (đã submit)
7. ✅ Tạo tồn kho ban đầu qua Stock Entry (đã submit)
8. ✅ Tạo Work Orders (Draft)
9. ✅ Verify cấu hình

```bash
# ⚠️ Đảm bảo bench start đang chạy ở terminal khác!
bench --site erpnext.localhost execute xuanhoa_app.scripts.reset_all_data.run
```

### Cách 3: Chỉ import master data (giữ giao dịch)

```bash
# ⚠️ Đảm bảo bench start đang chạy ở terminal khác!
bench --site erpnext.localhost execute xuanhoa_app.scripts.import_data.run_master_data_only
```

### Cách 4: Chỉ setup accounting (Bank accounts, Mode of Payment)

```bash
# ⚠️ Đảm bảo bench start đang chạy ở terminal khác!
bench --site erpnext.localhost execute xuanhoa_app.scripts.import_data.run_accounting_setup
```

### Cách 5: Chỉ tạo/cập nhật users

```bash
# ⚠️ Đảm bảo bench start đang chạy ở terminal khác!
bench --site erpnext.localhost execute xuanhoa_app.scripts.import_data.run_users_only
```

### Cách 6: Chỉ thiết lập permissions

```bash
# ⚠️ Đảm bảo bench start đang chạy ở terminal khác!
bench --site erpnext.localhost execute xuanhoa_app.scripts.import_data.run_permissions_only
```

---

## 👥 Danh sách Users mẫu

| Email | Password | Role | Mô tả |
|-------|----------|------|-------|
| `admin@xuanhoa.local` | `admin123` | System Manager + All | Quản trị hệ thống |
| `kho@xuanhoa.local` | `kho123` | Stock Manager/User | Quản lý kho |
| `sanxuat@xuanhoa.local` | `sanxuat123` | Manufacturing Manager/User + Stock User | Quản lý sản xuất |
| `muahang@xuanhoa.local` | `muahang123` | Purchase Manager/User + Stock User | Quản lý mua hàng |
| `banhang@xuanhoa.local` | `banhang123` | Sales Manager/User + Stock User | Quản lý bán hàng |
| `ketoan@xuanhoa.local` | `ketoan123` | Accounts Manager/User | Quản lý kế toán |

---

## 💰 Accounting Setup

### Bank Accounts
| Account | Sử dụng cho |
|---------|-------------|
| Cash - XHTB | Thanh toán tiền mặt |
| Ngân hàng Nội địa - XHTB | Chuyển khoản nội địa (Cheque, Credit Card, Bank Draft) |
| Ngân hàng Quốc tế - XHTB | Wire Transfer (thanh toán quốc tế) |

### Mode of Payment
| Phương thức | Tài khoản liên kết |
|------------|-------------------|
| Cash | Cash - XHTB |
| Wire Transfer | Ngân hàng Quốc tế - XHTB |
| Cheque | Ngân hàng Nội địa - XHTB |
| Credit Card | Ngân hàng Nội địa - XHTB |
| Bank Draft | Ngân hàng Nội địa - XHTB |

---

## 📦 Dữ liệu mẫu

### Nhà cung cấp (Suppliers)
| Tên | Loại | Nhóm |
|-----|------|------|
| NCC Linh Kiện Hà Nội | Individual | Nhà Cung Cấp Nội Địa |
| NCC Cơ Khí Hải Phòng | Company | Nhà Cung Cấp Nội Địa |
| Công Ty Điện Tử Trung Quốc | Company | Nhà Cung Cấp Quốc Tế |
| NCC Vật Liệu Đóng Gói | Company | Nhà Cung Cấp Nội Địa |

### Khách hàng (Customers)
| Tên | Loại | Nhóm | Khu vực |
|-----|------|------|--------|
| Bán lẻ | Individual | Bán Lẻ | Hà Nội |
| Công ty TNHH Đại Phát | Company | Công Ty | Hà Nội |
| Công ty CP Minh Quang | Company | Công Ty | TP.HCM |
| Tiệm Tạp Hóa Hồng Loan | Company | Bán Lẻ | Đà Nẵng |
| Cửa Hàng Điện Máy Thanh Tùng | Company | Bán Lẻ | Hải Phòng |

### Item Prices (Giá mua/bán)
| Item | Giá bán | Giá mua |
|------|---------|---------|
| LED-5W | 15,000 | 5,000 |
| LED-10W | 25,000 | 8,000 |
| CAP-ALUMINUM | 8,000 | 3,000 |
| HEAT-SINK | 5,000 | 2,000 |
| PCB-DRIVER | 12,000 | 5,000 |
| WIRE-COPPER | 50,000 | 20,000 |
| BOX-PAPER | 2,000 | 800 |
| LAMP-5W-30LED | 80,000 | - |
| LAMP-10W-50LED | 140,000 | - |
| SPOTLIGHT-30W | 250,000 | - |

---

## 🔢 Quy ước đặt mã (Naming Conventions)

### Stock Entry (Phiếu kho)
| Loại | Prefix | Ví dụ |
|------|--------|-------|
| Phiếu nhập kho | NK- | NK-2025-00001 |
| Phiếu xuất kho | XK- | XK-2025-00001 |
| Phiếu chuyển kho | CK- | CK-2025-00001 |
| Phiếu cấp phát NVL | CP- | CP-2025-00001 |
| Phiếu sản xuất | SX- | SX-2025-00001 |
| Phiếu đóng gói | DG- | DG-2025-00001 |
| Phiếu tháo gỡ | TG- | TG-2025-00001 |

### Purchase Invoice (Hóa đơn mua hàng)
- Format: `ACC-PINV-YYYY-XXXXX`

### Sales Invoice (Hóa đơn bán hàng)
- Format: `ACC-SINV-YYYY-XXXXX`

### Payment Entry (Phiếu thanh toán)
- Format: `ACC-PAY-YYYY-XXXXX`

---

## ⚠️ Lỗi thường gặp và cách xử lý

### 1. Lỗi "Warehouse does not belong to company"

**Nguyên nhân**: Warehouse thuộc company khác với company trên phiếu.

**Giải pháp**: Script đã xử lý bằng cách tất cả warehouses được tạo với đúng company "Xuân Hòa Thái Bình"

### 2. Lỗi "Default Company not set"

**Nguyên nhân**: User chưa có default company.

**Giải pháp**: Chạy `run_users_only()` để cập nhật user settings.

### 3. Lỗi "Mode of Payment Account not found"

**Nguyên nhân**: Mode of Payment chưa được liên kết với Account.

**Giải pháp**: Chạy `run_accounting_setup()` để thiết lập.

---

## 🔧 Tùy chỉnh dữ liệu

### Thêm Customer mới
Chỉnh sửa file `example/customer.csv`:
```csv
Customer Name,Customer Group,Customer Type,Territory
Công ty ABC,Công Ty,Company,Hà Nội
```

### Thêm Item Price mới
Chỉnh sửa file `example/item_price.csv`:
```csv
item_code,price_list,price_list_rate,selling,buying
NEW-ITEM,Standard Selling,100000,1,0
NEW-ITEM,Standard Buying,50000,0,1
```

---

## 📞 Debug

```bash
# Kiểm tra trong console
bench --site erpnext.localhost console
>>> frappe.get_all('Customer', pluck='name')
>>> frappe.get_all('Supplier', pluck='name')
>>> frappe.get_all('Item Price', fields=['item_code', 'price_list', 'price_list_rate'])
>>> frappe.get_all('Mode of Payment Account', fields=['parent', 'default_account'])
```
