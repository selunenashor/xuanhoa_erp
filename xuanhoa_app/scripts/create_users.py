"""
Script tạo users từ file CSV
Chạy: bench --site erpnext.localhost execute xuanhoa_app.scripts.create_users.run
"""

import os
import csv
import frappe
from frappe.utils.password import update_password


def get_example_path():
    """Lấy đường dẫn đến thư mục example"""
    return os.path.join(os.path.dirname(__file__), 'example')


def read_csv(filename):
    """Đọc file CSV và trả về list of dicts"""
    filepath = os.path.join(get_example_path(), filename)
    if not os.path.exists(filepath):
        print(f"⚠️  File không tồn tại: {filepath}")
        return []
    
    with open(filepath, 'r', encoding='utf-8') as f:
        reader = csv.DictReader(f)
        return list(reader)


def run():
    print("=" * 60)
    print("TẠO USERS TỪ FILE CSV")
    print("=" * 60)
    
    # Đọc users từ CSV
    users = read_csv('user.csv')
    user_roles = read_csv('user_role.csv')
    
    if not users:
        print("❌ Không tìm thấy dữ liệu user trong CSV")
        return
    
    # Nhóm roles theo user
    roles_by_user = {}
    for role in user_roles:
        email = role['parent']
        if email not in roles_by_user:
            roles_by_user[email] = []
        roles_by_user[email].append(role['role'])
    
    created = 0
    updated = 0
    
    for u in users:
        email = u['email']
        password = u.get('new_password', 'password123')
        
        if frappe.db.exists('User', email):
            print(f"⚠️  {email} đã tồn tại, cập nhật password...")
            update_password(email, password)
            updated += 1
            continue
        
        # Lấy roles cho user này
        user_role_list = roles_by_user.get(email, [])
        
        user = frappe.get_doc({
            'doctype': 'User',
            'email': email,
            'first_name': u['first_name'],
            'last_name': u['last_name'],
            'full_name': u['full_name'],
            'username': u.get('username', ''),
            'enabled': int(u.get('enabled', 1)),
            'user_type': u.get('user_type', 'System User'),
            'language': u.get('language', 'vi'),
            'time_zone': u.get('time_zone', 'Asia/Ho_Chi_Minh'),
            'send_welcome_email': int(u.get('send_welcome_email', 0)),
            'roles': [{'role': r} for r in user_role_list]
        })
        user.insert(ignore_permissions=True)
        update_password(email, password)
        print(f"✅ {email} - Roles: {', '.join(user_role_list)}")
        created += 1
    
    frappe.db.commit()
    
    print()
    print("=" * 60)
    print(f"KẾT QUẢ: Tạo mới {created}, Cập nhật {updated}")
    print("=" * 60)
    print()
    print("DANH SÁCH USERS ĐỂ TEST ĐĂNG NHẬP")
    print("=" * 60)
    print(f"{'Email':<30} {'Họ tên':<25} {'Password':<15}")
    print("-" * 70)
    for u in users:
        password = u.get('new_password', 'password123')
        print(f"{u['email']:<30} {u['full_name']:<25} {password:<15}")

