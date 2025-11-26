"""
Script tạo users cho từng role
Chạy: bench --site erpnext.localhost execute xuanhoa_app.create_users.run
"""

import frappe
from frappe.utils.password import update_password


USERS = [
    {
        'email': 'admin@xuanhoa.local',
        'first_name': 'Admin',
        'last_name': 'Hệ Thống',
        'role': 'System Manager',
        'password': 'admin123'
    },
    {
        'email': 'kho@xuanhoa.local',
        'first_name': 'Quản Lý',
        'last_name': 'Kho',
        'role': 'Stock Manager',
        'password': 'kho123'
    },
    {
        'email': 'sanxuat@xuanhoa.local',
        'first_name': 'Quản Lý',
        'last_name': 'Sản Xuất',
        'role': 'Manufacturing Manager',
        'password': 'sanxuat123'
    },
    {
        'email': 'muahang@xuanhoa.local',
        'first_name': 'Quản Lý',
        'last_name': 'Mua Hàng',
        'role': 'Purchase Manager',
        'password': 'muahang123'
    },
    {
        'email': 'banhang@xuanhoa.local',
        'first_name': 'Quản Lý',
        'last_name': 'Bán Hàng',
        'role': 'Sales Manager',
        'password': 'banhang123'
    },
    {
        'email': 'ketoan@xuanhoa.local',
        'first_name': 'Quản Lý',
        'last_name': 'Kế Toán',
        'role': 'Accounts Manager',
        'password': 'ketoan123'
    },
]


def run():
    print("=" * 60)
    print("TẠO USERS CHO TỪNG ROLE")
    print("=" * 60)
    
    for u in USERS:
        email = u['email']
        
        if frappe.db.exists('User', email):
            print(f"⚠️  {email} đã tồn tại, cập nhật password...")
            update_password(email, u['password'])
            continue
        
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
            'roles': [{'role': u['role']}]
        })
        user.insert(ignore_permissions=True)
        update_password(email, u['password'])
        print(f"✅ {email} - Role: {u['role']}")
    
    frappe.db.commit()
    
    print()
    print("=" * 60)
    print("DANH SÁCH USERS ĐỂ TEST ĐĂNG NHẬP")
    print("=" * 60)
    print(f"{'Email':<30} {'Role':<25} {'Password':<15}")
    print("-" * 70)
    for u in USERS:
        print(f"{u['email']:<30} {u['role']:<25} {u['password']:<15}")
