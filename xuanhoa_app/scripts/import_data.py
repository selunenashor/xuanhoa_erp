"""
Script import dữ liệu mẫu vào ERPNext
Chạy: bench --site erpnext.localhost execute xuanhoa_app.scripts.import_data.run
"""

import csv
import os
import frappe
from frappe.utils import flt, cint
from frappe.utils.password import update_password

# Đường dẫn thư mục example (trong app)
EXAMPLE_DIR = os.path.join(os.path.dirname(__file__), 'example')
COMPANY = 'Xuân Hòa Thái Bình'

# Mapping UOM tiếng Việt sang tiếng Anh (ERPNext standard)
UOM_MAP = {
    'Cái': 'Nos',
    'Bộ': 'Set',
    'Hộp': 'Box',
    'Cuộn': 'Roll',
    'Kg': 'Kg',
    'Mét': 'Meter',
}

# Dữ liệu users được đọc từ CSV files: user.csv, user_role.csv


def get_uom(vietnamese_uom):
    """Convert Vietnamese UOM to ERPNext standard UOM"""
    return UOM_MAP.get(vietnamese_uom, 'Nos')


def read_csv(filename):
    """Đọc file CSV"""
    filepath = os.path.join(EXAMPLE_DIR, filename)
    if not os.path.exists(filepath):
        print(f"⚠️  File không tồn tại: {filename}")
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


def delete_old_data():
    """Xóa dữ liệu cũ"""
    print("\n🗑️  Xóa dữ liệu cũ...")
    
    # Transactions
    for dt in ['Payment Entry', 'Sales Invoice', 'Purchase Invoice',
               'Delivery Note', 'Stock Entry', 'Purchase Receipt',
               'Work Order', 'BOM']:
        records = frappe.get_all(dt, filters={'company': COMPANY}, pluck='name')
        for name in records:
            try:
                frappe.delete_doc(dt, name, force=True, ignore_permissions=True)
            except:
                pass
    
    # Items
    items = frappe.get_all('Item', pluck='name')
    for name in items:
        try:
            frappe.delete_doc('Item', name, force=True, ignore_permissions=True)
        except:
            pass
    
    # Suppliers
    suppliers = frappe.get_all('Supplier', pluck='name')
    for name in suppliers:
        try:
            frappe.delete_doc('Supplier', name, force=True, ignore_permissions=True)
        except:
            pass
    
    # Customers
    customers = frappe.get_all('Customer', pluck='name')
    for name in customers:
        try:
            frappe.delete_doc('Customer', name, force=True, ignore_permissions=True)
        except:
            pass
    
    frappe.db.commit()
    print("  ✅ Đã xóa dữ liệu cũ")


def setup_role_permissions():
    """Thiết lập permissions cho các DocType từ CSV"""
    print("\n🔐 Setup Role Permissions...")
    
    permissions_data = read_csv('role_permission.csv')
    if not permissions_data:
        print("  ⚠️  Không tìm thấy file role_permission.csv")
        return 0
    
    # Group by doctype
    doctypes = {}
    for row in permissions_data:
        dt = row['doctype']
        if dt not in doctypes:
            doctypes[dt] = []
        doctypes[dt].append(row)
    
    count = 0
    for doctype, perms in doctypes.items():
        try:
            # Check if doctype exists
            if not frappe.db.exists('DocType', doctype):
                continue
            
            doc = frappe.get_doc('DocType', doctype)
            
            for perm in perms:
                role = perm['role']
                
                # Check if role exists
                if not frappe.db.exists('Role', role):
                    continue
                
                # Check if permission already exists
                existing = None
                for p in doc.permissions:
                    if p.role == role:
                        existing = p
                        break
                
                if existing:
                    # Update existing permission
                    existing.read = cint(perm.get('read', 0))
                    existing.write = cint(perm.get('write', 0))
                    existing.create = cint(perm.get('create', 0))
                    existing.delete = cint(perm.get('delete', 0))
                    existing.submit = cint(perm.get('submit', 0))
                    existing.cancel = cint(perm.get('cancel', 0))
                    existing.amend = cint(perm.get('amend', 0))
                    existing.report = cint(perm.get('report', 0))
                    existing.export = cint(perm.get('export', 0))
                    existing.set_user_permissions = cint(perm.get('import', 0))
                    existing.share = cint(perm.get('share', 0))
                    existing.print = cint(perm.get('print', 0))
                    existing.email = cint(perm.get('email', 0))
                else:
                    # Add new permission
                    doc.append('permissions', {
                        'role': role,
                        'read': cint(perm.get('read', 0)),
                        'write': cint(perm.get('write', 0)),
                        'create': cint(perm.get('create', 0)),
                        'delete': cint(perm.get('delete', 0)),
                        'submit': cint(perm.get('submit', 0)),
                        'cancel': cint(perm.get('cancel', 0)),
                        'amend': cint(perm.get('amend', 0)),
                        'report': cint(perm.get('report', 0)),
                        'export': cint(perm.get('export', 0)),
                        'set_user_permissions': cint(perm.get('import', 0)),
                        'share': cint(perm.get('share', 0)),
                        'print': cint(perm.get('print', 0)),
                        'email': cint(perm.get('email', 0))
                    })
                count += 1
            
            doc.save(ignore_permissions=True)
            
        except Exception as e:
            print(f"  ❌ Lỗi {doctype}: {str(e)}")
    
    frappe.db.commit()
    print(f"  ✅ {len(doctypes)} DocTypes, {count} permissions")
    return count


def setup_users():
    """Tạo users với roles đầy đủ"""
    print("\n👥 Setup Users...")
    
    users = load_users_data()
    if not users:
        print("  ⚠️  Không có dữ liệu users từ CSV")
        return 0
    
    count = 0
    for u in users:
        email = u['email']
        
        if frappe.db.exists('User', email):
            # Update existing user's roles
            user = frappe.get_doc('User', email)
            existing_roles = [r.role for r in user.roles]
            
            for role in u['roles']:
                if role not in existing_roles:
                    user.append('roles', {'role': role})
            
            user.save(ignore_permissions=True)
            update_password(email, u['password'])
            print(f"  ⚠️  {email} đã tồn tại, cập nhật roles")
        else:
            user = frappe.get_doc({
                'doctype': 'User',
                'email': email,
                'first_name': u['first_name'],
                'last_name': u['last_name'],
                'full_name': f"{u['first_name']} {u['last_name']}",
                'enabled': 1,
                'user_type': 'System User',
                'language': 'vi',
                'time_zone': 'Asia/Ho_Chi_Minh',
                'send_welcome_email': 0,
                'roles': [{'role': role} for role in u['roles']]
            })
            user.insert(ignore_permissions=True)
            update_password(email, u['password'])
            count += 1
    
    frappe.db.commit()
    print(f"  ✅ {count} Users")
    
    # Print user table
    print("\n  " + "-"*65)
    print(f"  {'Email':<28} {'Password':<12} {'Roles':<25}")
    print("  " + "-"*65)
    for u in users:
        roles_str = ', '.join(u['roles'][:2]) + ('...' if len(u['roles']) > 2 else '')
        print(f"  {u['email']:<28} {u['password']:<12} {roles_str:<25}")
    
    return count


def import_item_groups():
    """Import Item Groups"""
    print("\n📦 Import Item Groups...")
    count = 0
    
    # Parent groups first
    for row in read_csv('item_group.csv'):
        name = row['Item Group Name']
        if not row.get('Parent Item Group') and not frappe.db.exists('Item Group', name):
            frappe.get_doc({
                'doctype': 'Item Group',
                'item_group_name': name,
                'is_group': cint(row.get('Is Group', 0))
            }).insert(ignore_permissions=True)
            count += 1
    
    # Child groups
    for row in read_csv('item_group.csv'):
        name = row['Item Group Name']
        if row.get('Parent Item Group') and not frappe.db.exists('Item Group', name):
            frappe.get_doc({
                'doctype': 'Item Group',
                'item_group_name': name,
                'parent_item_group': row['Parent Item Group'],
                'is_group': cint(row.get('Is Group', 0))
            }).insert(ignore_permissions=True)
            count += 1
    
    frappe.db.commit()
    print(f"  ✅ {count} Item Groups")
    return count


def import_supplier_groups():
    """Import Supplier Groups"""
    print("\n📦 Import Supplier Groups...")
    count = 0
    
    for row in read_csv('supplier_group.csv'):
        name = row['Supplier Group Name']
        if not frappe.db.exists('Supplier Group', name):
            frappe.get_doc({
                'doctype': 'Supplier Group',
                'supplier_group_name': name,
                'is_group': cint(row.get('Is Group', 0))
            }).insert(ignore_permissions=True)
            count += 1
    
    frappe.db.commit()
    print(f"  ✅ {count} Supplier Groups")
    return count


def import_customer_groups():
    """Import Customer Groups"""
    print("\n📦 Import Customer Groups...")
    count = 0
    
    # Parent groups first
    for row in read_csv('customer_group.csv'):
        name = row['Customer Group Name']
        if not row.get('Parent Customer Group') and not frappe.db.exists('Customer Group', name):
            frappe.get_doc({
                'doctype': 'Customer Group',
                'customer_group_name': name,
                'is_group': cint(row.get('Is Group', 0))
            }).insert(ignore_permissions=True)
            count += 1
    
    # Child groups
    for row in read_csv('customer_group.csv'):
        name = row['Customer Group Name']
        if row.get('Parent Customer Group') and not frappe.db.exists('Customer Group', name):
            frappe.get_doc({
                'doctype': 'Customer Group',
                'customer_group_name': name,
                'parent_customer_group': row['Parent Customer Group'],
                'is_group': cint(row.get('Is Group', 0))
            }).insert(ignore_permissions=True)
            count += 1
    
    frappe.db.commit()
    print(f"  ✅ {count} Customer Groups")
    return count


def import_territories():
    """Import Territories"""
    print("\n📦 Import Territories...")
    count = 0
    
    # Parent territories first
    for row in read_csv('territory.csv'):
        name = row['Territory Name']
        if not row.get('Parent Territory') and not frappe.db.exists('Territory', name):
            frappe.get_doc({
                'doctype': 'Territory',
                'territory_name': name,
                'is_group': cint(row.get('Is Group', 0))
            }).insert(ignore_permissions=True)
            count += 1
    
    # Child territories
    for row in read_csv('territory.csv'):
        name = row['Territory Name']
        if row.get('Parent Territory') and not frappe.db.exists('Territory', name):
            frappe.get_doc({
                'doctype': 'Territory',
                'territory_name': name,
                'parent_territory': row['Parent Territory'],
                'is_group': cint(row.get('Is Group', 0))
            }).insert(ignore_permissions=True)
            count += 1
    
    frappe.db.commit()
    print(f"  ✅ {count} Territories")
    return count


def import_warehouses():
    """Import Warehouses"""
    print("\n📦 Import Warehouses...")
    count = 0
    
    for row in read_csv('warehouse.csv'):
        wh_name = row['Warehouse Name']
        if not frappe.db.exists('Warehouse', wh_name):
            # Remove suffix for warehouse_name field
            clean_name = wh_name.replace(' - XHTB', '')
            parent = row.get('Parent Warehouse') or None
            
            frappe.get_doc({
                'doctype': 'Warehouse',
                'warehouse_name': clean_name,
                'company': COMPANY,
                'parent_warehouse': parent,
                'is_group': cint(row.get('Is Group', 0))
            }).insert(ignore_permissions=True)
            count += 1
    
    frappe.db.commit()
    print(f"  ✅ {count} Warehouses")
    return count


def import_suppliers():
    """Import Suppliers"""
    print("\n📦 Import Suppliers...")
    count = 0
    
    for row in read_csv('supplier.csv'):
        name = row['Supplier Name']
        if not frappe.db.exists('Supplier', name):
            frappe.get_doc({
                'doctype': 'Supplier',
                'supplier_name': name,
                'supplier_group': row.get('Supplier Group'),
                'supplier_type': row.get('Supplier Type', 'Company'),
                'country': row.get('Country', 'Vietnam')
            }).insert(ignore_permissions=True)
            count += 1
    
    frappe.db.commit()
    print(f"  ✅ {count} Suppliers")
    return count


def import_customers():
    """Import Customers"""
    print("\n📦 Import Customers...")
    count = 0
    
    for row in read_csv('customer.csv'):
        name = row['Customer Name']
        if not frappe.db.exists('Customer', name):
            frappe.get_doc({
                'doctype': 'Customer',
                'customer_name': name,
                'customer_group': row.get('Customer Group'),
                'customer_type': row.get('Customer Type', 'Company'),
                'territory': row.get('Territory')
            }).insert(ignore_permissions=True)
            count += 1
    
    frappe.db.commit()
    print(f"  ✅ {count} Customers")
    return count


def import_items():
    """Import Items"""
    print("\n📦 Import Items...")
    count = 0
    
    for row in read_csv('item.csv'):
        item_code = row['Item Code']
        if not frappe.db.exists('Item', item_code):
            uom = get_uom(row.get('Default Unit of Measure', 'Cái'))
            frappe.get_doc({
                'doctype': 'Item',
                'item_code': item_code,
                'item_name': row.get('Item Name', item_code),
                'item_group': row.get('Item Group', 'All Item Groups'),
                'stock_uom': uom,
                'description': row.get('Description', ''),
                'is_stock_item': cint(row.get('Is Stock Item', 1)),
                'include_item_in_manufacturing': cint(row.get('Include Item In Manufacturing', 1)),
                'valuation_method': row.get('Valuation Method', 'FIFO'),
                'standard_rate': flt(row.get('Standard Selling Rate', 0))
            }).insert(ignore_permissions=True)
            count += 1
    
    frappe.db.commit()
    print(f"  ✅ {count} Items")
    return count


def import_item_prices():
    """Import Item Prices"""
    print("\n📦 Import Item Prices...")
    count = 0
    
    for row in read_csv('item_price.csv'):
        item_code = row['item_code']
        price_list = row['price_list']
        
        # Check if price already exists
        existing = frappe.db.exists('Item Price', {
            'item_code': item_code,
            'price_list': price_list
        })
        if existing:
            continue
        
        frappe.get_doc({
            'doctype': 'Item Price',
            'item_code': item_code,
            'price_list': price_list,
            'price_list_rate': flt(row['price_list_rate']),
            'selling': cint(row.get('selling', 0)),
            'buying': cint(row.get('buying', 0))
        }).insert(ignore_permissions=True)
        count += 1
    
    frappe.db.commit()
    print(f"  ✅ {count} Item Prices")
    return count


def setup_accounts():
    """Tạo accounts cần thiết (Bank accounts)"""
    print("\n📦 Setup Bank Accounts...")
    count = 0
    
    # Kiểm tra và tạo Bank Accounts
    bank_accounts = [
        {
            'account_name': 'Ngân hàng Nội địa',
            'parent_account': 'Bank Accounts - XHTB',
            'account_type': 'Bank',
            'company': COMPANY,
            'account_currency': 'VND'
        },
        {
            'account_name': 'Ngân hàng Quốc tế',
            'parent_account': 'Bank Accounts - XHTB',
            'account_type': 'Bank',
            'company': COMPANY,
            'account_currency': 'VND'
        }
    ]
    
    for acc in bank_accounts:
        account_name = f"{acc['account_name']} - XHTB"
        if not frappe.db.exists('Account', account_name):
            try:
                frappe.get_doc({
                    'doctype': 'Account',
                    **acc
                }).insert(ignore_permissions=True)
                count += 1
                print(f"  ✅ {account_name}")
            except Exception as e:
                print(f"  ⚠️  {account_name}: {e}")
    
    frappe.db.commit()
    print(f"  ✅ {count} Bank Accounts created")
    return count


def setup_mode_of_payment_accounts():
    """Setup Mode of Payment với Account liên kết"""
    print("\n📦 Setup Mode of Payment Accounts...")
    count = 0
    
    # Mapping Mode of Payment với Account
    mop_accounts = [
        ('Cash', 'Cash - XHTB'),
        ('Wire Transfer', 'Ngân hàng Quốc tế - XHTB'),
        ('Cheque', 'Ngân hàng Nội địa - XHTB'),
        ('Credit Card', 'Ngân hàng Nội địa - XHTB'),
        ('Bank Draft', 'Ngân hàng Nội địa - XHTB'),
    ]
    
    for mop_name, account in mop_accounts:
        if not frappe.db.exists('Mode of Payment', mop_name):
            print(f"  ⚠️  Mode of Payment '{mop_name}' không tồn tại")
            continue
        
        if not frappe.db.exists('Account', account):
            print(f"  ⚠️  Account '{account}' không tồn tại")
            continue
        
        mop = frappe.get_doc('Mode of Payment', mop_name)
        
        # Check if account already linked for this company
        existing = False
        for acc in mop.accounts:
            if acc.company == COMPANY:
                if acc.default_account != account:
                    acc.default_account = account
                    mop.save(ignore_permissions=True)
                    count += 1
                    print(f"  ✅ {mop_name} -> {account} (updated)")
                existing = True
                break
        
        if not existing:
            mop.append('accounts', {
                'company': COMPANY,
                'default_account': account
            })
            mop.save(ignore_permissions=True)
            count += 1
            print(f"  ✅ {mop_name} -> {account}")
    
    frappe.db.commit()
    print(f"  ✅ {count} Mode of Payment Accounts")
    return count


def import_boms():
    """Import BOMs"""
    print("\n📦 Import BOMs...")
    count = 0
    
    bom_items = read_csv('bom_item.csv')
    
    for row in read_csv('bom.csv'):
        item = row['Item']
        
        # Check if BOM already exists for this item
        existing = frappe.db.get_value('BOM', {'item': item, 'is_active': 1, 'is_default': 1}, 'name')
        if existing:
            continue
        
        # Get items for this BOM
        items = [i for i in bom_items if i['BOM ID'] == row['BOM ID']]
        
        doc = frappe.get_doc({
            'doctype': 'BOM',
            'item': item,
            'company': COMPANY,
            'quantity': flt(row.get('Quantity', 1)),
            'uom': get_uom(row.get('UOM', 'Cái')),
            'is_active': 1,
            'is_default': 1,
            'items': [{
                'item_code': i['Item Code'],
                'qty': flt(i['Quantity']),
                'uom': get_uom(i.get('Unit of Measure', 'Cái')),
                'rate': flt(i.get('Rate Per Unit', 0))
            } for i in items]
        })
        doc.insert(ignore_permissions=True)
        # Submit BOM so it can be used in Work Orders
        doc.submit()
        count += 1
    
    frappe.db.commit()
    print(f"  ✅ {count} BOMs (submitted)")
    return count


def import_work_orders():
    """Import Work Orders"""
    print("\n📦 Import Work Orders...")
    count = 0
    
    for row in read_csv('work_order.csv'):
        item = row['Item']
        
        # Get BOM for this item
        bom = frappe.db.get_value('BOM', {'item': item, 'is_active': 1, 'is_default': 1}, 'name')
        if not bom:
            print(f"  ⚠️  Không tìm thấy BOM cho {item}")
            continue
        
        doc = frappe.get_doc({
            'doctype': 'Work Order',
            'production_item': item,
            'item_name': row.get('Item Name', ''),
            'qty': flt(row['Qty to Manufacture']),
            'bom_no': bom,
            'company': COMPANY,
            'source_warehouse': row.get('Source Warehouse'),
            'wip_warehouse': row.get('WIP Warehouse'),
            'fg_warehouse': row.get('FG Warehouse'),
            'planned_start_date': row.get('Planned Start Date'),
            'status': 'Draft'
        })
        doc.insert(ignore_permissions=True)
        count += 1
    
    frappe.db.commit()
    print(f"  ✅ {count} Work Orders")
    return count


def import_purchase_receipts():
    """Import Purchase Receipts"""
    print("\n📦 Import Purchase Receipts...")
    count = 0
    
    pr_items = read_csv('purchase_receipt_item.csv')
    
    for row in read_csv('purchase_receipt.csv'):
        pr_id = row['Receipt No']
        items = [i for i in pr_items if i['Receipt No'] == pr_id]
        
        if not items:
            continue
        
        doc = frappe.get_doc({
            'doctype': 'Purchase Receipt',
            'supplier': row['Supplier'],
            'posting_date': row['Date'],
            'company': COMPANY,
            'set_warehouse': row.get('Warehouse'),
            'items': [{
                'item_code': i['Item Code'],
                'qty': flt(i['Received Quantity']),
                'uom': get_uom(i.get('UOM', 'Cái')),
                'rate': flt(i['Rate']),
                'warehouse': i.get('Warehouse')
            } for i in items]
        })
        doc.insert(ignore_permissions=True)
        # Submit to update stock
        doc.submit()
        count += 1
    
    frappe.db.commit()
    print(f"  ✅ {count} Purchase Receipts (submitted)")
    return count


def import_stock_entries():
    """Import Stock Entries (Manufacturing)"""
    print("\n📦 Import Stock Entries...")
    count = 0
    
    se_items = read_csv('stock_entry_item.csv')
    
    for row in read_csv('stock_entry.csv'):
        se_id = row['Stock Entry No']
        items = [i for i in se_items if i['Stock Entry No'] == se_id]
        
        if not items:
            continue
        
        # Build items list - separate source and target items
        item_list = []
        for i in items:
            qty = abs(flt(i['Quantity']))
            item_data = {
                'item_code': i['Item Code'],
                'qty': qty,
                'uom': get_uom(i.get('UOM', 'Cái')),
                'basic_rate': flt(i['Rate']),
            }
            
            # Source warehouse (xuất)
            if i.get('S Warehouse'):
                item_data['s_warehouse'] = i['S Warehouse']
            
            # Target warehouse (nhập)
            if i.get('T Warehouse'):
                item_data['t_warehouse'] = i['T Warehouse']
            
            # Is finished item flag
            if cint(i.get('Is Finished Item', 0)):
                item_data['is_finished_item'] = 1
            
            item_list.append(item_data)
        
        doc = frappe.get_doc({
            'doctype': 'Stock Entry',
            'stock_entry_type': row['Stock Entry Type'],
            'posting_date': row['Date'],
            'company': COMPANY,
            'items': item_list
        })
        
        try:
            doc.insert(ignore_permissions=True)
            doc.submit()
            count += 1
        except Exception as e:
            print(f"  ⚠️  Lỗi Stock Entry {se_id}: {e}")
    
    frappe.db.commit()
    print(f"  ✅ {count} Stock Entries (submitted)")
    return count


def import_delivery_notes():
    """Import Delivery Notes"""
    print("\n📦 Import Delivery Notes...")
    count = 0
    
    dn_items = read_csv('delivery_note_item.csv')
    
    for row in read_csv('delivery_note.csv'):
        dn_id = row['Delivery Note No']
        items = [i for i in dn_items if i['Delivery Note No'] == dn_id]
        
        if not items:
            continue
        
        doc = frappe.get_doc({
            'doctype': 'Delivery Note',
            'customer': row['Customer'],
            'posting_date': row['Date'],
            'company': COMPANY,
            'set_warehouse': row.get('Warehouse'),
            'items': [{
                'item_code': i['Item Code'],
                'qty': flt(i['Qty']),
                'uom': get_uom(i.get('UOM', 'Cái')),
                'rate': flt(i['Rate']),
                'warehouse': i.get('Warehouse')
            } for i in items]
        })
        doc.insert(ignore_permissions=True)
        doc.submit()
        count += 1
    
    frappe.db.commit()
    print(f"  ✅ {count} Delivery Notes (submitted)")
    return count


def import_purchase_invoices():
    """Import Purchase Invoices"""
    print("\n📦 Import Purchase Invoices...")
    count = 0
    
    pi_items = read_csv('purchase_invoice_item.csv')
    
    for row in read_csv('purchase_invoice.csv'):
        pi_id = row['name']
        items = [i for i in pi_items if i['parent'] == pi_id]
        
        if not items:
            continue
        
        doc = frappe.get_doc({
            'doctype': 'Purchase Invoice',
            'supplier': row['supplier'],
            'posting_date': row['posting_date'],
            'due_date': row['due_date'],
            'company': COMPANY,
            'bill_no': row.get('bill_no'),
            'bill_date': row.get('bill_date'),
            'update_stock': 0,
            'items': [{
                'item_code': i['item_code'],
                'qty': flt(i['qty']),
                'uom': get_uom(i.get('uom', 'Cái')),
                'rate': flt(i['rate']),
                'expense_account': i.get('expense_account')
            } for i in items]
        })
        doc.insert(ignore_permissions=True)
        doc.submit()
        count += 1
    
    frappe.db.commit()
    print(f"  ✅ {count} Purchase Invoices (submitted)")
    return count


def import_sales_invoices():
    """Import Sales Invoices"""
    print("\n📦 Import Sales Invoices...")
    count = 0
    
    si_items = read_csv('sales_invoice_item.csv')
    
    for row in read_csv('sales_invoice.csv'):
        si_id = row['name']
        items = [i for i in si_items if i['parent'] == si_id]
        
        if not items:
            continue
        
        doc = frappe.get_doc({
            'doctype': 'Sales Invoice',
            'customer': row['customer'],
            'posting_date': row['posting_date'],
            'due_date': row['due_date'],
            'company': COMPANY,
            'update_stock': 0,
            'items': [{
                'item_code': i['item_code'],
                'qty': flt(i['qty']),
                'uom': get_uom(i.get('uom', 'Cái')),
                'rate': flt(i['rate']),
                'income_account': i.get('income_account')
            } for i in items]
        })
        doc.insert(ignore_permissions=True)
        doc.submit()
        count += 1
    
    frappe.db.commit()
    print(f"  ✅ {count} Sales Invoices (submitted)")
    return count


def run():
    """Main function"""
    print("\n" + "="*60)
    print("🚀 IMPORT DỮ LIỆU MẪU ERPNext")
    print("="*60)
    
    # Step 0: Setup permissions and users
    setup_role_permissions()
    setup_users()
    
    # Step 1: Delete old data
    delete_old_data()
    
    # Step 2: Import master data
    import_item_groups()
    import_supplier_groups()
    import_customer_groups()
    import_territories()
    import_warehouses()
    import_suppliers()
    import_customers()
    import_items()
    import_item_prices()
    
    # Step 3: Setup accounting
    setup_accounts()
    setup_mode_of_payment_accounts()
    
    # Step 4: Import manufacturing
    import_boms()
    import_work_orders()
    
    # Step 5: Import stock transactions
    import_purchase_receipts()
    
    print("\n" + "="*60)
    print("🎉 HOÀN TẤT IMPORT DỮ LIỆU MẪU!")
    print("="*60)


def run_permissions_only():
    """Chỉ chạy setup permissions và users"""
    print("\n" + "="*60)
    print("🔐 SETUP PERMISSIONS & USERS")
    print("="*60)
    
    setup_role_permissions()
    setup_users()
    
    print("\n" + "="*60)
    print("✅ HOÀN TẤT!")
    print("="*60)


def run_users_only():
    """Chỉ tạo users"""
    print("\n" + "="*60)
    print("👥 TẠO USERS")
    print("="*60)
    
    setup_users()
    
    print("\n" + "="*60)
    print("✅ HOÀN TẤT!")
    print("="*60)


def run_master_data_only():
    """Import master data mà KHÔNG xóa giao dịch hiện có"""
    print("\n" + "="*60)
    print("📥 IMPORT MASTER DATA (KHÔNG XÓA GIAO DỊCH)")
    print("="*60)
    
    # Import master data
    import_item_groups()
    import_supplier_groups()
    import_customer_groups()
    import_territories()
    import_warehouses()
    import_suppliers()
    import_customers()
    import_items()
    import_item_prices()
    
    # Setup accounting
    setup_accounts()
    setup_mode_of_payment_accounts()
    
    # Import BOMs only (không xóa)
    import_boms()
    
    print("\n" + "="*60)
    print("✅ HOÀN TẤT IMPORT MASTER DATA!")
    print("="*60)


def run_accounting_setup():
    """Chỉ setup accounting (Bank accounts, Mode of Payment)"""
    print("\n" + "="*60)
    print("💰 SETUP ACCOUNTING")
    print("="*60)
    
    setup_accounts()
    setup_mode_of_payment_accounts()
    
    print("\n" + "="*60)
    print("✅ HOÀN TẤT!")
    print("="*60)

