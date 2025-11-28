"""
Script XÓA TOÀN BỘ DỮ LIỆU và cài lại từ đầu
============================================

⚠️ CẢNH BÁO: Script này sẽ XÓA TẤT CẢ dữ liệu trong hệ thống!

Chạy: bench --site erpnext.localhost execute xuanhoa_app.scripts.reset_all_data.run

Các bước:
1. Thiết lập prerequisites (Currency, UOMs, etc.)
2. Xóa toàn bộ transactions và master data
3. Tạo Company mới với cấu hình đúng
4. Set default company cho tất cả users
5. Import dữ liệu mẫu từ CSV
6. Tạo tồn kho ban đầu

Lưu ý quan trọng:
- Script này đã xử lý các edge cases như: company-warehouse mismatch, 
  missing UOMs, default company không được set, etc.
- Tất cả warehouses sẽ thuộc về đúng company để tránh lỗi Stock Entry
"""

import csv
import os
import frappe
from frappe.utils import flt, cint, today
from frappe.utils.password import update_password

# =============================================================================
# CONFIGURATION
# =============================================================================
EXAMPLE_DIR = os.path.join(os.path.dirname(__file__), 'example')
COMPANY_NAME = 'Xuân Hòa Thái Bình'
COMPANY_ABBR = 'XHTB'
DEFAULT_CURRENCY = 'VND'
COUNTRY = 'Vietnam'

# UOM mapping: Vietnamese -> ERPNext standard
UOM_MAP = {
    'Cái': 'Nos',
    'Bộ': 'Set', 
    'Hộp': 'Box',
    'Cuộn': 'Roll',
    'Kg': 'Kg',
    'Mét': 'Meter',
    'Nos': 'Nos',
    'Set': 'Set',
    'Box': 'Box',
    'Roll': 'Roll',
    'Meter': 'Meter',
}

# Dữ liệu được đọc từ CSV files trong thư mục example/
# - user.csv, user_role.csv: Danh sách users và roles
# - initial_stock.csv: Tồn kho ban đầu
# - work_order.csv: Work orders mẫu


# =============================================================================
# HELPER FUNCTIONS
# =============================================================================

def get_uom(vn_uom):
    """Convert Vietnamese UOM to ERPNext standard UOM"""
    return UOM_MAP.get(vn_uom, 'Nos')


def get_warehouse_name(short_name):
    """Get full warehouse name with company abbreviation"""
    return f"{short_name} - {COMPANY_ABBR}"


def read_csv(filename):
    """Read CSV file from example directory"""
    filepath = os.path.join(EXAMPLE_DIR, filename)
    if not os.path.exists(filepath):
        print(f"  ⚠️  File không tồn tại: {filename}")
        return []
    with open(filepath, 'r', encoding='utf-8') as f:
        return list(csv.DictReader(f))


def load_users_data():
    """Load users data from CSV files (user.csv + user_role.csv)"""
    users_csv = read_csv('user.csv')
    roles_csv = read_csv('user_role.csv')
    
    # Build roles mapping per user
    user_roles = {}
    for row in roles_csv:
        email = row['parent']
        role = row['role']
        if email not in user_roles:
            user_roles[email] = []
        user_roles[email].append(role)
    
    # Build users list
    users = []
    for row in users_csv:
        email = row['email']
        users.append({
            'email': email,
            'first_name': row['first_name'],
            'last_name': row['last_name'],
            'roles': user_roles.get(email, ['System Manager']),
            'password': row.get('new_password', 'admin123')
        })
    
    return users


def load_initial_stock():
    """Load initial stock data from CSV"""
    rows = read_csv('initial_stock.csv')
    return [{
        'item_code': row['item_code'],
        'qty': flt(row['qty']),
        'rate': flt(row['rate']),
        'warehouse': row['warehouse']
    } for row in rows]


def load_work_orders_data():
    """Load work orders data from CSV"""
    rows = read_csv('work_order.csv')
    return [{
        'item': row['Item'],
        'qty': flt(row['Qty to Manufacture']),
        'fg_warehouse': row.get('FG Warehouse', 'Kho Thành Phẩm').replace(f' - {COMPANY_ABBR}', ''),
        'wip_warehouse': row.get('WIP Warehouse', 'Kho WIP').replace(f' - {COMPANY_ABBR}', ''),
        'source_warehouse': row.get('Source Warehouse', 'Kho Chính').replace(f' - {COMPANY_ABBR}', '')
    } for row in rows]


def safe_delete_doc(doctype, name):
    """Safely delete a document, handling errors"""
    try:
        doc = frappe.get_doc(doctype, name)
        if hasattr(doc, 'docstatus') and doc.docstatus == 1:
            doc.cancel()
        frappe.delete_doc(doctype, name, force=True, ignore_permissions=True)
        return True
    except Exception:
        try:
            frappe.db.sql(f"DELETE FROM `tab{doctype}` WHERE name = %s", name)
            return True
        except Exception:
            return False


# =============================================================================
# PREREQUISITES SETUP
# =============================================================================

def setup_prerequisites():
    """Setup required data before importing (Currency, UOMs, etc.)"""
    print("\n" + "="*60)
    print("⚙️  THIẾT LẬP PREREQUISITES")
    print("="*60)
    
    # 1. Ensure Currency exists
    print("\n  Checking Currency...")
    if not frappe.db.exists('Currency', DEFAULT_CURRENCY):
        frappe.get_doc({
            'doctype': 'Currency',
            'currency_name': DEFAULT_CURRENCY,
            'enabled': 1,
            'fraction': 'Đồng',
            'fraction_units': 100,
            'number_format': '#,###.##',
            'symbol': '₫'
        }).insert(ignore_permissions=True)
        print(f"    ✅ Tạo Currency: {DEFAULT_CURRENCY}")
    else:
        print(f"    ✅ Currency {DEFAULT_CURRENCY} đã tồn tại")
    
    # 2. Ensure UOMs exist
    print("\n  Checking UOMs...")
    required_uoms = list(set(UOM_MAP.values()))
    for uom in required_uoms:
        if not frappe.db.exists('UOM', uom):
            frappe.get_doc({
                'doctype': 'UOM',
                'uom_name': uom,
                'enabled': 1
            }).insert(ignore_permissions=True)
            print(f"    ✅ Tạo UOM: {uom}")
    
    # 3. Ensure Country exists
    print("\n  Checking Country...")
    if not frappe.db.exists('Country', COUNTRY):
        frappe.get_doc({
            'doctype': 'Country',
            'country_name': COUNTRY,
            'code': 'vn'
        }).insert(ignore_permissions=True)
        print(f"    ✅ Tạo Country: {COUNTRY}")
    else:
        print(f"    ✅ Country {COUNTRY} đã tồn tại")
    
    # 4. Ensure default Item Groups exist
    print("\n  Checking default Item Groups...")
    if not frappe.db.exists('Item Group', 'All Item Groups'):
        frappe.get_doc({
            'doctype': 'Item Group',
            'item_group_name': 'All Item Groups',
            'is_group': 1
        }).insert(ignore_permissions=True)
        print("    ✅ Tạo Item Group: All Item Groups")
    
    # 5. Ensure default Supplier Groups exist
    print("\n  Checking default Supplier Groups...")
    if not frappe.db.exists('Supplier Group', 'All Supplier Groups'):
        frappe.get_doc({
            'doctype': 'Supplier Group',
            'supplier_group_name': 'All Supplier Groups',
            'is_group': 1
        }).insert(ignore_permissions=True)
        print("    ✅ Tạo Supplier Group: All Supplier Groups")
    
    # 6. Ensure default Customer Groups exist
    print("\n  Checking default Customer Groups...")
    if not frappe.db.exists('Customer Group', 'All Customer Groups'):
        frappe.get_doc({
            'doctype': 'Customer Group',
            'customer_group_name': 'All Customer Groups',
            'is_group': 1
        }).insert(ignore_permissions=True)
        print("    ✅ Tạo Customer Group: All Customer Groups")
    
    # 7. Ensure default Territories exist
    print("\n  Checking default Territories...")
    if not frappe.db.exists('Territory', 'All Territories'):
        frappe.get_doc({
            'doctype': 'Territory',
            'territory_name': 'All Territories',
            'is_group': 1
        }).insert(ignore_permissions=True)
        print("    ✅ Tạo Territory: All Territories")
    
    frappe.db.commit()
    print("\n  ✅ Prerequisites đã sẵn sàng!")


# =============================================================================
# DELETE FUNCTIONS
# =============================================================================

def delete_all_transactions():
    """Delete all transactions"""
    print("\n" + "="*60)
    print("🗑️  XÓA GIAO DỊCH")
    print("="*60)
    
    # Order matters - delete dependent transactions first
    doctypes = [
        'Payment Entry',
        'Journal Entry',
        'Sales Invoice',
        'Purchase Invoice',
        'Delivery Note',
        'Stock Entry',
        'Stock Reconciliation',
        'Purchase Receipt',
        'Job Card',
        'Work Order',
        'BOM',
        'Purchase Order',
        'Sales Order',
        'Quotation',
        'Request for Quotation',
        'Supplier Quotation',
        'Material Request',
    ]
    
    for dt in doctypes:
        try:
            records = frappe.get_all(dt, pluck='name')
            count = 0
            for name in records:
                if safe_delete_doc(dt, name):
                    count += 1
            if count > 0:
                print(f"  ✅ Xóa {count} {dt}")
        except Exception as e:
            print(f"  ⚠️  Lỗi xóa {dt}: {str(e)[:50]}")
    
    frappe.db.commit()


def delete_all_master_data():
    """Delete all master data"""
    print("\n" + "="*60)
    print("🗑️  XÓA MASTER DATA")
    print("="*60)
    
    # Delete stock-related tables first
    try:
        frappe.db.sql("DELETE FROM `tabBin`")
        print("  ✅ Xóa Bin (stock balance)")
    except Exception as e:
        print(f"  ⚠️  Lỗi xóa Bin: {e}")
    
    try:
        frappe.db.sql("DELETE FROM `tabStock Ledger Entry`")
        print("  ✅ Xóa Stock Ledger Entry")
    except Exception as e:
        print(f"  ⚠️  Lỗi xóa Stock Ledger Entry: {e}")
    
    try:
        frappe.db.sql("DELETE FROM `tabGL Entry`")
        print("  ✅ Xóa GL Entry")
    except Exception as e:
        print(f"  ⚠️  Lỗi xóa GL Entry: {e}")
    
    # Master data with defaults to preserve
    master_data = [
        ('Item', []),
        ('Supplier', []),
        ('Customer', []),
        ('Warehouse', []),
        ('Item Group', ['All Item Groups']),
        ('Supplier Group', ['All Supplier Groups']),
        ('Customer Group', ['All Customer Groups', 'Commercial', 'Individual']),
        ('Territory', ['All Territories']),
    ]
    
    for dt, preserve in master_data:
        try:
            records = frappe.get_all(dt, pluck='name')
            count = 0
            for name in records:
                if name not in preserve:
                    if safe_delete_doc(dt, name):
                        count += 1
            if count > 0:
                print(f"  ✅ Xóa {count} {dt}")
        except Exception as e:
            print(f"  ⚠️  Lỗi xóa {dt}: {str(e)[:50]}")
    
    frappe.db.commit()


def delete_companies():
    """Delete all companies"""
    print("\n" + "="*60)
    print("🗑️  XÓA COMPANIES")
    print("="*60)
    
    companies = frappe.get_all('Company', pluck='name')
    for name in companies:
        try:
            # Delete linked records first
            for dt in ['Account', 'Cost Center', 'Warehouse']:
                records = frappe.get_all(dt, filters={'company': name}, pluck='name')
                for rec in records:
                    safe_delete_doc(dt, rec)
            
            frappe.delete_doc('Company', name, force=True, ignore_permissions=True)
            print(f"  ✅ Xóa Company: {name}")
        except Exception as e:
            print(f"  ⚠️  Lỗi xóa {name}: {str(e)[:50]}")
    
    frappe.db.commit()


def delete_users():
    """Delete users created by script (keep Administrator and Guest)"""
    print("\n" + "="*60)
    print("🗑️  XÓA USERS")
    print("="*60)
    
    keep_users = ['Administrator', 'Guest']
    users = frappe.get_all('User', filters={'name': ['not in', keep_users]}, pluck='name')
    
    for email in users:
        try:
            frappe.delete_doc('User', email, force=True, ignore_permissions=True)
            print(f"  ✅ Xóa User: {email}")
        except Exception as e:
            print(f"  ⚠️  Lỗi xóa {email}: {str(e)[:50]}")
    
    frappe.db.commit()


# =============================================================================
# CREATE/IMPORT FUNCTIONS
# =============================================================================

def create_company():
    """Create company with proper configuration"""
    print("\n" + "="*60)
    print("🏢 TẠO COMPANY")
    print("="*60)
    
    if frappe.db.exists('Company', COMPANY_NAME):
        print(f"  ⚠️  Company '{COMPANY_NAME}' đã tồn tại")
    else:
        try:
            doc = frappe.get_doc({
                'doctype': 'Company',
                'company_name': COMPANY_NAME,
                'abbr': COMPANY_ABBR,
                'default_currency': DEFAULT_CURRENCY,
                'country': COUNTRY,
                'enable_perpetual_inventory': 1
            })
            doc.insert(ignore_permissions=True)
            print(f"  ✅ Tạo Company: {COMPANY_NAME} ({COMPANY_ABBR})")
        except Exception as e:
            print(f"  ❌ Lỗi tạo Company: {e}")
            raise
    
    frappe.db.commit()
    
    # Xóa các warehouse mặc định của ERPNext (tiếng Anh)
    delete_default_warehouses()


def delete_default_warehouses():
    """Delete default ERPNext warehouses (English) - keep only custom Vietnamese warehouses"""
    print("\n  🗑️  Xóa Warehouses mặc định...")
    
    # Các warehouse mặc định của ERPNext khi tạo company
    default_warehouses = [
        f'Finished Goods - {COMPANY_ABBR}',
        f'Goods In Transit - {COMPANY_ABBR}',
        f'Stores - {COMPANY_ABBR}',
        f'Work In Progress - {COMPANY_ABBR}',
    ]
    
    for wh_name in default_warehouses:
        if frappe.db.exists('Warehouse', wh_name):
            try:
                frappe.delete_doc('Warehouse', wh_name, force=True, ignore_permissions=True)
                print(f"    ✅ Xóa: {wh_name}")
            except Exception as e:
                print(f"    ⚠️  Không thể xóa {wh_name}: {str(e)[:40]}")
    
    frappe.db.commit()


def set_default_company():
    """Set default company for all users - CRITICAL for avoiding warehouse mismatch"""
    print("\n" + "="*60)
    print("⚙️  SET DEFAULT COMPANY")
    print("="*60)
    
    try:
        # 1. Set Global Defaults using set_single_value (most reliable method)
        frappe.db.set_single_value("Global Defaults", "default_company", COMPANY_NAME)
        print(f"  ✅ Set Global Defaults company: {COMPANY_NAME}")
    except Exception as e:
        print(f"  ⚠️  Lỗi set Global Defaults: {e}")
        # Fallback: Direct SQL update
        try:
            frappe.db.sql("""
                UPDATE `tabSingles` 
                SET value = %s 
                WHERE doctype = 'Global Defaults' AND field = 'default_company'
            """, (COMPANY_NAME,))
            # Insert if not exists
            if not frappe.db.sql("SELECT 1 FROM `tabSingles` WHERE doctype='Global Defaults' AND field='default_company'"):
                frappe.db.sql("""
                    INSERT INTO `tabSingles` (doctype, field, value)
                    VALUES ('Global Defaults', 'default_company', %s)
                """, (COMPANY_NAME,))
            print(f"  ✅ Set Global Defaults via SQL: {COMPANY_NAME}")
        except Exception as e2:
            print(f"  ❌ SQL fallback failed: {e2}")
    
    try:
        # 2. Delete old company defaults
        frappe.db.sql("DELETE FROM `tabDefaultValue` WHERE defkey = 'Company'")
        
        # 3. Set for __default (system default)
        frappe.db.sql("""
            INSERT INTO `tabDefaultValue` (name, parent, parenttype, defkey, defvalue)
            VALUES (%s, '__default', '', 'Company', %s)
        """, (frappe.generate_hash()[:10], COMPANY_NAME))
        print(f"  ✅ Set system default company: {COMPANY_NAME}")
    except Exception as e:
        print(f"  ⚠️  Lỗi set system default: {e}")
    
    try:
        # 4. Set for Administrator
        frappe.db.sql("""
            INSERT INTO `tabDefaultValue` (name, parent, parenttype, defkey, defvalue)
            VALUES (%s, 'Administrator', 'User', 'Company', %s)
        """, (frappe.generate_hash()[:10], COMPANY_NAME))
        print(f"  ✅ Set Administrator default company: {COMPANY_NAME}")
    except Exception as e:
        print(f"  ⚠️  Lỗi set Administrator default: {e}")
    
    frappe.db.commit()
    frappe.clear_cache()
    
    # Verify
    default = frappe.db.get_single_value("Global Defaults", "default_company")
    if default == COMPANY_NAME:
        print(f"\n  ✅ Verified: Default company = {default}")
    else:
        print(f"\n  ⚠️  Warning: Default company = {default} (expected: {COMPANY_NAME})")


def setup_users():
    """Create users with proper roles"""
    print("\n" + "="*60)
    print("👥 TẠO USERS")
    print("="*60)
    
    users_data = load_users_data()
    if not users_data:
        print("  ⚠️  Không có dữ liệu users từ CSV")
        return
    
    for u in users_data:
        try:
            if frappe.db.exists('User', u['email']):
                user = frappe.get_doc('User', u['email'])
                user.roles = []
                for role in u['roles']:
                    user.append('roles', {'role': role})
                user.save(ignore_permissions=True)
                update_password(u['email'], u['password'])
                print(f"  ⚠️  Cập nhật User: {u['email']}")
            else:
                user = frappe.get_doc({
                    'doctype': 'User',
                    'email': u['email'],
                    'first_name': u['first_name'],
                    'last_name': u['last_name'],
                    'enabled': 1,
                    'user_type': 'System User',
                    'send_welcome_email': 0,
                    'roles': [{'role': r} for r in u['roles']]
                })
                user.insert(ignore_permissions=True)
                update_password(u['email'], u['password'])
                print(f"  ✅ Tạo User: {u['email']}")
            
            # Set default company for this user
            frappe.db.sql("""
                INSERT INTO `tabDefaultValue` (name, parent, parenttype, defkey, defvalue)
                VALUES (%s, %s, 'User', 'Company', %s)
                ON DUPLICATE KEY UPDATE defvalue = %s
            """, (frappe.generate_hash()[:10], u['email'], COMPANY_NAME, COMPANY_NAME))
            
        except Exception as e:
            print(f"  ❌ Lỗi tạo user {u['email']}: {e}")
    
    frappe.db.commit()
    
    print("\n  📋 Danh sách Users:")
    print("  " + "-"*50)
    for u in users_data:
        print(f"  {u['email']} / {u['password']}")


def import_warehouses():
    """Import warehouses - ensure they belong to correct company"""
    print("\n📦 Import Warehouses...")
    count = 0
    
    for row in read_csv('warehouse.csv'):
        wh_name = row['Warehouse Name']
        if not frappe.db.exists('Warehouse', wh_name):
            clean_name = wh_name.replace(f' - {COMPANY_ABBR}', '')
            try:
                frappe.get_doc({
                    'doctype': 'Warehouse',
                    'warehouse_name': clean_name,
                    'company': COMPANY_NAME,  # CRITICAL: must match company
                    'is_group': cint(row.get('Is Group', 0))
                }).insert(ignore_permissions=True)
                count += 1
            except Exception as e:
                print(f"  ⚠️  Lỗi tạo warehouse {wh_name}: {e}")
    
    frappe.db.commit()
    print(f"  ✅ {count} Warehouses")
    
    # Verify all warehouses belong to correct company
    wrong_company_wh = frappe.get_all('Warehouse', 
        filters={'company': ['!=', COMPANY_NAME], 'disabled': 0, 'is_group': 0},
        fields=['name', 'company'])
    if wrong_company_wh:
        print(f"\n  ⚠️  WARNING: {len(wrong_company_wh)} warehouses thuộc company khác!")
        for wh in wrong_company_wh:
            print(f"     - {wh.name} => {wh.company}")


def import_item_groups():
    """Import item groups"""
    print("\n📦 Import Item Groups...")
    count = 0
    
    # Import parent groups first (is_group = 1)
    for row in read_csv('item_group.csv'):
        if cint(row.get('Is Group', 0)) == 1:
            name = row['Item Group Name']
            if not frappe.db.exists('Item Group', name):
                try:
                    frappe.get_doc({
                        'doctype': 'Item Group',
                        'item_group_name': name,
                        'parent_item_group': row.get('Parent Item Group') or 'All Item Groups',
                        'is_group': 1
                    }).insert(ignore_permissions=True)
                    count += 1
                except Exception as e:
                    print(f"  ⚠️  Lỗi tạo item group {name}: {e}")
    
    # Then import child groups
    for row in read_csv('item_group.csv'):
        if cint(row.get('Is Group', 0)) == 0:
            name = row['Item Group Name']
            if not frappe.db.exists('Item Group', name):
                parent = row.get('Parent Item Group') or 'All Item Groups'
                # Check parent exists
                if not frappe.db.exists('Item Group', parent):
                    parent = 'All Item Groups'
                try:
                    frappe.get_doc({
                        'doctype': 'Item Group',
                        'item_group_name': name,
                        'parent_item_group': parent,
                        'is_group': 0
                    }).insert(ignore_permissions=True)
                    count += 1
                except Exception as e:
                    print(f"  ⚠️  Lỗi tạo item group {name}: {e}")
    
    frappe.db.commit()
    print(f"  ✅ {count} Item Groups")


def import_supplier_groups():
    """Import supplier groups"""
    print("\n📦 Import Supplier Groups...")
    count = 0
    
    for row in read_csv('supplier_group.csv'):
        name = row['Supplier Group Name']
        if not frappe.db.exists('Supplier Group', name):
            parent = row.get('Parent Supplier Group') or 'All Supplier Groups'
            if not frappe.db.exists('Supplier Group', parent):
                parent = 'All Supplier Groups'
            try:
                frappe.get_doc({
                    'doctype': 'Supplier Group',
                    'supplier_group_name': name,
                    'parent_supplier_group': parent,
                    'is_group': cint(row.get('Is Group', 0))
                }).insert(ignore_permissions=True)
                count += 1
            except Exception as e:
                print(f"  ⚠️  Lỗi tạo supplier group {name}: {e}")
    
    frappe.db.commit()
    print(f"  ✅ {count} Supplier Groups")


def import_suppliers():
    """Import suppliers"""
    print("\n📦 Import Suppliers...")
    count = 0
    
    for row in read_csv('supplier.csv'):
        name = row['Supplier Name']
        if not frappe.db.exists('Supplier', name):
            supplier_group = row.get('Supplier Group') or 'All Supplier Groups'
            if not frappe.db.exists('Supplier Group', supplier_group):
                supplier_group = 'All Supplier Groups'
            
            try:
                frappe.get_doc({
                    'doctype': 'Supplier',
                    'supplier_name': name,
                    'supplier_group': supplier_group,
                    'supplier_type': row.get('Supplier Type', 'Company'),
                }).insert(ignore_permissions=True)
                count += 1
            except Exception as e:
                print(f"  ⚠️  Lỗi tạo supplier {name}: {e}")
    
    frappe.db.commit()
    print(f"  ✅ {count} Suppliers")


def import_items():
    """Import items"""
    print("\n📦 Import Items...")
    count = 0
    
    for row in read_csv('item.csv'):
        item_code = row['Item Code']
        if not frappe.db.exists('Item', item_code):
            uom = get_uom(row.get('Default Unit of Measure', 'Cái'))
            item_group = row.get('Item Group', 'All Item Groups')
            if not frappe.db.exists('Item Group', item_group):
                item_group = 'All Item Groups'
            
            try:
                frappe.get_doc({
                    'doctype': 'Item',
                    'item_code': item_code,
                    'item_name': row.get('Item Name', item_code),
                    'item_group': item_group,
                    'stock_uom': uom,
                    'is_stock_item': cint(row.get('Is Stock Item', 1)),
                    'include_item_in_manufacturing': 1,
                    'valuation_method': 'FIFO',
                    'standard_rate': flt(row.get('Standard Selling Rate', 0))
                }).insert(ignore_permissions=True)
                count += 1
            except Exception as e:
                print(f"  ⚠️  Lỗi tạo item {item_code}: {e}")
    
    frappe.db.commit()
    print(f"  ✅ {count} Items")


def import_boms():
    """Import BOMs and submit them"""
    print("\n📦 Import BOMs...")
    count = 0
    
    bom_items = read_csv('bom_item.csv')
    
    for row in read_csv('bom.csv'):
        item = row['Item']
        
        # Skip if BOM already exists
        existing = frappe.db.get_value('BOM', {'item': item, 'is_active': 1}, 'name')
        if existing:
            continue
        
        # Skip if item doesn't exist
        if not frappe.db.exists('Item', item):
            print(f"  ⚠️  Item {item} không tồn tại, bỏ qua BOM")
            continue
        
        items = [i for i in bom_items if i['BOM ID'] == row['BOM ID']]
        
        # Validate all items exist
        valid_items = []
        for i in items:
            if frappe.db.exists('Item', i['Item Code']):
                valid_items.append(i)
            else:
                print(f"  ⚠️  BOM item {i['Item Code']} không tồn tại")
        
        if not valid_items:
            continue
        
        try:
            doc = frappe.get_doc({
                'doctype': 'BOM',
                'item': item,
                'company': COMPANY_NAME,
                'quantity': flt(row.get('Quantity', 1)),
                'uom': get_uom(row.get('UOM', 'Cái')),
                'is_active': 1,
                'is_default': 1,
                'items': [{
                    'item_code': i['Item Code'],
                    'qty': flt(i['Quantity']),
                    'uom': get_uom(i.get('Unit of Measure', 'Cái')),
                    'rate': flt(i.get('Rate Per Unit', 0))
                } for i in valid_items]
            })
            doc.insert(ignore_permissions=True)
            doc.submit()
            count += 1
        except Exception as e:
            print(f"  ⚠️  Lỗi tạo BOM cho {item}: {e}")
    
    frappe.db.commit()
    print(f"  ✅ {count} BOMs (submitted)")


def create_initial_stock():
    """Create initial stock via Stock Entry"""
    print("\n📦 Tạo tồn kho ban đầu...")
    
    initial_stock = load_initial_stock()
    if not initial_stock:
        print("  ⚠️  Không có dữ liệu initial_stock.csv")
        return
    
    # Filter to only existing items
    existing_items = []
    for item in initial_stock:
        if frappe.db.exists('Item', item['item_code']):
            wh_name = get_warehouse_name(item['warehouse'])
            if frappe.db.exists('Warehouse', wh_name):
                existing_items.append({
                    'item_code': item['item_code'],
                    'qty': item['qty'],
                    'rate': item['rate'],
                    'warehouse': wh_name
                })
            else:
                print(f"  ⚠️  Warehouse {wh_name} không tồn tại, bỏ qua {item['item_code']}")
        else:
            print(f"  ⚠️  Item {item['item_code']} không tồn tại, bỏ qua")
    
    if not existing_items:
        print("  ⚠️  Không có items để tạo tồn kho")
        return
    
    try:
        doc = frappe.get_doc({
            'doctype': 'Stock Entry',
            'stock_entry_type': 'Material Receipt',
            'purpose': 'Material Receipt',
            'posting_date': today(),
            'company': COMPANY_NAME,
            'remarks': 'Nhập tồn kho ban đầu - Auto generated by setup script',
            'items': [{
                'item_code': item['item_code'],
                'qty': item['qty'],
                't_warehouse': item['warehouse'],
                'basic_rate': item['rate']
            } for item in existing_items]
        })
        doc.insert(ignore_permissions=True)
        doc.submit()
        print(f"  ✅ Tạo Stock Entry {doc.name} với {len(existing_items)} items")
    except Exception as e:
        print(f"  ❌ Lỗi tạo Stock Entry: {e}")
        import traceback
        traceback.print_exc()
    
    frappe.db.commit()


def import_work_orders():
    """Import work orders"""
    print("\n📦 Import Work Orders...")
    count = 0
    
    work_orders_data = load_work_orders_data()
    if not work_orders_data:
        print("  ⚠️  Không có dữ liệu work_order.csv")
        return
    
    for wo in work_orders_data:
        item = wo['item']
        
        if not frappe.db.exists('Item', item):
            print(f"  ⚠️  Item {item} không tồn tại, bỏ qua")
            continue
        
        bom = frappe.db.get_value('BOM', {'item': item, 'is_active': 1, 'is_default': 1}, 'name')
        if not bom:
            print(f"  ⚠️  Không có BOM cho {item}")
            continue
        
        try:
            doc = frappe.get_doc({
                'doctype': 'Work Order',
                'production_item': item,
                'qty': wo['qty'],
                'bom_no': bom,
                'company': COMPANY_NAME,
                'fg_warehouse': get_warehouse_name(wo['fg_warehouse']),
                'wip_warehouse': get_warehouse_name(wo['wip_warehouse']),
                'source_warehouse': get_warehouse_name(wo['source_warehouse']),
                'planned_start_date': today()
            })
            doc.insert(ignore_permissions=True)
            count += 1
        except Exception as e:
            print(f"  ⚠️  Lỗi tạo Work Order cho {item}: {e}")
    
    frappe.db.commit()
    print(f"  ✅ {count} Work Orders (Draft)")


def verify_setup():
    """Verify setup is correct"""
    print("\n" + "="*60)
    print("🔍 KIỂM TRA CẤU HÌNH")
    print("="*60)
    
    errors = []
    
    # 1. Check company exists
    if not frappe.db.exists('Company', COMPANY_NAME):
        errors.append(f"Company {COMPANY_NAME} không tồn tại")
    else:
        print(f"  ✅ Company: {COMPANY_NAME}")
    
    # 2. Check default company
    frappe.clear_cache()
    default_company = frappe.db.get_single_value("Global Defaults", "default_company")
    if default_company != COMPANY_NAME:
        errors.append(f"Default company = {default_company}, expected {COMPANY_NAME}")
    else:
        print(f"  ✅ Default Company: {default_company}")
    
    # 3. Check warehouses belong to correct company
    warehouses = frappe.get_all('Warehouse', 
        filters={'company': COMPANY_NAME, 'disabled': 0, 'is_group': 0},
        pluck='name')
    print(f"  ✅ Warehouses: {len(warehouses)} kho thuộc {COMPANY_NAME}")
    
    wrong_wh = frappe.get_all('Warehouse',
        filters={'company': ['!=', COMPANY_NAME], 'disabled': 0, 'is_group': 0},
        pluck='name')
    if wrong_wh:
        errors.append(f"{len(wrong_wh)} warehouses thuộc company khác: {wrong_wh[:3]}")
    
    # 4. Check stock exists
    bins = frappe.get_all('Bin', fields=['item_code', 'warehouse', 'actual_qty'])
    if bins:
        print(f"  ✅ Stock: {len(bins)} records")
    else:
        print(f"  ⚠️  Stock: Không có tồn kho")
    
    # 5. Check BOMs
    boms = frappe.get_all('BOM', filters={'is_active': 1, 'docstatus': 1})
    print(f"  ✅ BOMs: {len(boms)} active & submitted")
    
    # 6. Check Work Orders
    wos = frappe.get_all('Work Order')
    print(f"  ✅ Work Orders: {len(wos)}")
    
    if errors:
        print("\n  ❌ ERRORS:")
        for e in errors:
            print(f"     - {e}")
        return False
    
    print("\n  ✅ Tất cả cấu hình OK!")
    return True


# =============================================================================
# MAIN FUNCTIONS
# =============================================================================

def run():
    """Main function - DELETE ALL AND RECREATE"""
    print("\n" + "="*70)
    print("🔄 RESET TOÀN BỘ DỮ LIỆU ERPNEXT")
    print("="*70)
    print("⚠️  Script này sẽ XÓA TẤT CẢ dữ liệu và tạo lại từ đầu!")
    print("="*70)
    
    # Step 0: Setup prerequisites
    setup_prerequisites()
    
    # Step 1: Delete everything
    delete_all_transactions()
    delete_all_master_data()
    delete_companies()
    delete_users()
    
    # Step 2: Create fresh data
    print("\n" + "="*60)
    print("📥 TẠO DỮ LIỆU MỚI")
    print("="*60)
    
    create_company()
    set_default_company()  # CRITICAL
    setup_users()
    import_warehouses()
    import_item_groups()
    import_supplier_groups()
    import_suppliers()
    import_items()
    import_boms()
    create_initial_stock()
    import_work_orders()
    
    # Step 3: Setup Role Permissions
    from xuanhoa_app.scripts import import_data
    import_data.setup_role_permissions()
    
    # Step 4: Verify
    frappe.clear_cache()
    verify_setup()
    
    print("\n" + "="*70)
    print("🎉 HOÀN TẤT RESET DỮ LIỆU!")
    print("="*70)


def run_delete_only():
    """Delete all data only"""
    print("\n" + "="*70)
    print("🗑️  XÓA TOÀN BỘ DỮ LIỆU")
    print("="*70)
    
    delete_all_transactions()
    delete_all_master_data()
    delete_companies()
    delete_users()
    
    frappe.clear_cache()
    print("\n✅ Hoàn tất xóa dữ liệu!")


def run_import_only():
    """Import data only (no delete)"""
    print("\n" + "="*70)
    print("📥 IMPORT DỮ LIỆU")
    print("="*70)
    
    setup_prerequisites()
    create_company()
    set_default_company()
    setup_users()
    import_warehouses()
    import_item_groups()
    import_supplier_groups()
    import_suppliers()
    import_items()
    import_boms()
    create_initial_stock()
    import_work_orders()
    
    frappe.clear_cache()
    verify_setup()
    print("\n✅ Hoàn tất import dữ liệu!")


def run_verify():
    """Just verify current setup"""
    verify_setup()


def setup_all():
    """
    🚀 SETUP TOÀN BỘ HỆ THỐNG - CHẠY 1 LẦN DUY NHẤT
    ================================================
    
    Script này thực hiện:
    1. Reset toàn bộ dữ liệu (xóa và tạo lại)
    2. Import thêm Customers, Item Prices, Territories
    3. Setup Bank Accounts và Mode of Payment
    4. Thiết lập Role Permissions
    5. Tạo đủ 6 users cho các phòng ban
    
    Chạy: bench --site erpnext.localhost execute xuanhoa_app.scripts.reset_all_data.setup_all
    
    ⚠️ YÊU CẦU: Phải chạy `bench start` ở terminal khác trước!
    """
    print("\n" + "="*70)
    print("🚀 SETUP TOÀN BỘ HỆ THỐNG XUÂN HÒA ERP")
    print("="*70)
    print("Script này sẽ:")
    print("  1. Reset toàn bộ dữ liệu")
    print("  2. Import Customers, Item Prices, Territories")
    print("  3. Setup Bank Accounts và Mode of Payment")
    print("  4. Thiết lập Role Permissions")
    print("  5. Tạo 6 users (admin, kho, sanxuat, muahang, banhang, ketoan)")
    print("="*70 + "\n")
    
    # Step 1: Reset data (from reset_all_data.py)
    run()
    
    # Step 2: Import additional data (from import_data.py)
    # Note: Role Permissions và Users đã được setup trong run()
    print("\n" + "="*70)
    print("📥 IMPORT DỮ LIỆU BỔ SUNG")
    print("="*70)
    
    from xuanhoa_app.scripts import import_data
    
    # Import customer groups and territories
    import_data.import_customer_groups()
    import_data.import_territories()
    
    # Import customers
    import_data.import_customers()
    
    # Import item prices
    import_data.import_item_prices()
    
    # Setup accounting
    import_data.setup_accounts()
    import_data.setup_mode_of_payment_accounts()
    
    frappe.db.commit()
    frappe.clear_cache()
    
    print("\n" + "="*70)
    print("🎉 HOÀN TẤT SETUP TOÀN BỘ HỆ THỐNG!")
    print("="*70)
    print(f"""
✅ Hệ thống đã sẵn sàng sử dụng!
⚠️ Hãy đăng nhập lại để refresh session.
""")
