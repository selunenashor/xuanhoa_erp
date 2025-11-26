"""Quick script to import BOMs only"""
import frappe
from frappe.utils import flt, cint
import csv
import os

EXAMPLE_DIR = '/media/selune/Selune/Code/httt/apps/xuanhoa_app/xuanhoa_app/scripts/example'
COMPANY = 'Xuân Hòa Thái Bình'

UOM_MAP = {
    'Cái': 'Nos',
    'Bộ': 'Set',
    'Hộp': 'Box',
    'Cuộn': 'Roll',
    'Kg': 'Kg',
    'Mét': 'Meter',
}

def get_uom(vietnamese_uom):
    return UOM_MAP.get(vietnamese_uom, 'Nos')

def read_csv(filename):
    filepath = os.path.join(EXAMPLE_DIR, filename)
    with open(filepath, 'r', encoding='utf-8') as f:
        return list(csv.DictReader(f))

def run():
    print("📦 Import BOMs...")
    count = 0

    bom_items = read_csv('bom_item.csv')

    for row in read_csv('bom.csv'):
        item = row['Item']
        
        # Check if BOM already exists for this item
        existing = frappe.db.get_value('BOM', {'item': item, 'is_active': 1, 'is_default': 1}, 'name')
        if existing:
            print(f"  ⚠️  BOM đã tồn tại cho {item}")
            continue
        
        # Get items for this BOM
        items = [i for i in bom_items if i['BOM ID'] == row['BOM ID']]
        
        if not items:
            print(f"  ⚠️  Không có items cho BOM {row['BOM ID']}")
            continue
        
        try:
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
            doc.submit()
            count += 1
            print(f"  ✅ {item}: {len(items)} components")
        except Exception as e:
            print(f"  ❌ Lỗi {item}: {str(e)}")

    frappe.db.commit()
    print(f"\n✅ Đã import {count} BOMs")
