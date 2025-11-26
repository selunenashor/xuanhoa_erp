"""
Xuân Hòa Manufacturing - API Wrapper
====================================
Custom API endpoints để đơn giản hóa giao tiếp Frontend - Backend

Các API này wrap các chức năng phức tạp của ERPNext thành các endpoint đơn giản
để Frontend (Vue.js) có thể gọi dễ dàng.
"""

import frappe
from frappe import _


# ============================================
# MATERIAL RECEIPT APIs
# ============================================

@frappe.whitelist()
def create_material_receipt(item_code, qty, warehouse, rate=None):
    """
    Tạo phiếu nhập kho đơn giản
    
    Args:
        item_code: Mã hàng hóa
        qty: Số lượng nhập
        warehouse: Kho nhập (target warehouse)
        rate: Đơn giá (tùy chọn, nếu không có sẽ lấy từ Item)
    
    Returns:
        dict: {success: bool, name: str, message: str}
    
    Example:
        POST /api/method/xuanhoa_app.api.create_material_receipt
        {
            "item_code": "NVL-001",
            "qty": 100,
            "warehouse": "Kho Chính - XHTB"
        }
    """
    try:
        doc = frappe.new_doc("Stock Entry")
        doc.purpose = "Material Receipt"
        doc.stock_entry_type = "Material Receipt"
        doc.company = frappe.defaults.get_user_default("Company") or "XUÂN HÒA THÁI BÌNH"
        
        row = doc.append("items", {})
        row.item_code = item_code
        row.qty = float(qty)
        row.t_warehouse = warehouse
        if rate:
            row.basic_rate = float(rate)
        
        doc.insert()
        doc.submit()
        
        return {
            "success": True,
            "name": doc.name,
            "message": _("Phiếu nhập kho {0} đã tạo thành công").format(doc.name)
        }
    except Exception as e:
        frappe.log_error(frappe.get_traceback(), "create_material_receipt Error")
        return {
            "success": False,
            "message": str(e)
        }


@frappe.whitelist()
def create_material_issue(item_code, qty, warehouse, cost_center=None):
    """
    Tạo phiếu xuất kho
    
    Args:
        item_code: Mã hàng hóa
        qty: Số lượng xuất
        warehouse: Kho xuất (source warehouse)
        cost_center: Trung tâm chi phí (tùy chọn)
    """
    try:
        doc = frappe.new_doc("Stock Entry")
        doc.purpose = "Material Issue"
        doc.stock_entry_type = "Material Issue"
        doc.company = frappe.defaults.get_user_default("Company") or "XUÂN HÒA THÁI BÌNH"
        
        row = doc.append("items", {})
        row.item_code = item_code
        row.qty = float(qty)
        row.s_warehouse = warehouse
        if cost_center:
            row.cost_center = cost_center
        
        doc.insert()
        doc.submit()
        
        return {
            "success": True,
            "name": doc.name,
            "message": _("Phiếu xuất kho {0} đã tạo thành công").format(doc.name)
        }
    except Exception as e:
        frappe.log_error(frappe.get_traceback(), "create_material_issue Error")
        return {
            "success": False,
            "message": str(e)
        }


# ============================================
# WORK ORDER APIs
# ============================================

@frappe.whitelist()
def get_work_orders(status=None, limit=20):
    """
    Lấy danh sách Work Order cho dashboard
    
    Args:
        status: Lọc theo trạng thái (Not Started, In Process, Completed, Stopped)
        limit: Số lượng kết quả tối đa
    
    Returns:
        list: Danh sách Work Order với các thông tin cơ bản
    """
    filters = {"docstatus": 1}  # Chỉ lấy submitted
    if status:
        filters["status"] = status
    
    orders = frappe.get_all(
        "Work Order",
        filters=filters,
        fields=[
            "name", "production_item", "item_name", 
            "qty", "produced_qty", "status",
            "planned_start_date", "expected_delivery_date",
            "wip_warehouse", "fg_warehouse"
        ],
        order_by="modified desc",
        limit=int(limit)
    )
    
    # Tính phần trăm hoàn thành
    for order in orders:
        if order.qty > 0:
            order["progress"] = round((order.produced_qty / order.qty) * 100, 1)
        else:
            order["progress"] = 0
    
    return orders


@frappe.whitelist()
def get_work_order_detail(work_order_name):
    """
    Lấy chi tiết Work Order bao gồm nguyên liệu cần thiết
    
    Args:
        work_order_name: Mã Work Order
    
    Returns:
        dict: Thông tin chi tiết Work Order
    """
    doc = frappe.get_doc("Work Order", work_order_name)
    
    # Lấy thông tin nguyên liệu
    required_items = []
    for item in doc.required_items:
        required_items.append({
            "item_code": item.item_code,
            "item_name": item.item_name,
            "required_qty": item.required_qty,
            "transferred_qty": item.transferred_qty,
            "consumed_qty": item.consumed_qty,
            "available_qty_at_source": item.available_qty_at_source_warehouse,
            "source_warehouse": item.source_warehouse
        })
    
    return {
        "name": doc.name,
        "production_item": doc.production_item,
        "item_name": doc.item_name,
        "qty": doc.qty,
        "produced_qty": doc.produced_qty,
        "status": doc.status,
        "bom_no": doc.bom_no,
        "wip_warehouse": doc.wip_warehouse,
        "fg_warehouse": doc.fg_warehouse,
        "source_warehouse": doc.source_warehouse,
        "planned_start_date": doc.planned_start_date,
        "expected_delivery_date": doc.expected_delivery_date,
        "required_items": required_items,
        "progress": round((doc.produced_qty / doc.qty) * 100, 1) if doc.qty > 0 else 0
    }


@frappe.whitelist()
def start_work_order(work_order_name):
    """
    Bắt đầu sản xuất - Chuyển vật tư từ Stores -> WIP
    
    Tạo Stock Entry loại "Material Transfer for Manufacture"
    """
    try:
        from erpnext.manufacturing.doctype.work_order.work_order import make_stock_entry
        
        work_order = frappe.get_doc("Work Order", work_order_name)
        
        if work_order.status not in ["Not Started", "In Process"]:
            return {
                "success": False,
                "message": _("Không thể bắt đầu Work Order với trạng thái {0}").format(work_order.status)
            }
        
        # Tạo Stock Entry loại "Material Transfer for Manufacture"
        stock_entry = make_stock_entry(work_order_name, "Material Transfer for Manufacture", work_order.qty)
        stock_entry.insert()
        stock_entry.submit()
        
        return {
            "success": True,
            "stock_entry": stock_entry.name,
            "message": _("Đã cấp phát vật tư cho Work Order {0}").format(work_order_name)
        }
    except Exception as e:
        frappe.log_error(frappe.get_traceback(), "start_work_order Error")
        return {
            "success": False,
            "message": str(e)
        }


@frappe.whitelist()
def complete_work_order(work_order_name, qty):
    """
    Hoàn thành sản xuất - Tiêu hao NVL từ WIP, nhập thành phẩm vào FG
    
    Tạo Stock Entry loại "Manufacture"
    """
    try:
        from erpnext.manufacturing.doctype.work_order.work_order import make_stock_entry
        
        work_order = frappe.get_doc("Work Order", work_order_name)
        
        # Kiểm tra số lượng hợp lệ
        remaining = work_order.qty - work_order.produced_qty
        if float(qty) > remaining:
            return {
                "success": False,
                "message": _("Số lượng vượt quá ({0} > {1})").format(qty, remaining)
            }
        
        # Tạo Stock Entry loại "Manufacture"
        stock_entry = make_stock_entry(work_order_name, "Manufacture", float(qty))
        stock_entry.insert()
        stock_entry.submit()
        
        return {
            "success": True,
            "stock_entry": stock_entry.name,
            "produced_qty": qty,
            "message": _("Đã hoàn thành sản xuất {0} sản phẩm").format(qty)
        }
    except Exception as e:
        frappe.log_error(frappe.get_traceback(), "complete_work_order Error")
        return {
            "success": False,
            "message": str(e)
        }


# ============================================
# DASHBOARD APIs
# ============================================

@frappe.whitelist()
def get_dashboard_kpi():
    """
    Lấy KPI tổng quan cho Dashboard
    
    Returns:
        dict: Các chỉ số KPI
    """
    company = frappe.defaults.get_user_default("Company") or "XUÂN HÒA THÁI BÌNH"
    
    # Đếm Work Orders theo trạng thái
    wo_stats = {}
    statuses = ["Not Started", "In Process", "Completed", "Stopped"]
    for status in statuses:
        count = frappe.db.count("Work Order", {"status": status, "docstatus": 1})
        wo_stats[status] = count
    
    # Tổng giá trị tồn kho
    stock_value = frappe.db.sql("""
        SELECT COALESCE(SUM(stock_value), 0) as total
        FROM `tabBin`
    """, as_dict=True)[0].get("total", 0)
    
    # Số lượng phiếu nhập/xuất hôm nay
    today = frappe.utils.today()
    receipts_today = frappe.db.count("Stock Entry", {
        "purpose": "Material Receipt",
        "posting_date": today,
        "docstatus": 1
    })
    issues_today = frappe.db.count("Stock Entry", {
        "purpose": "Material Issue", 
        "posting_date": today,
        "docstatus": 1
    })
    
    return {
        "work_orders": wo_stats,
        "stock_value": stock_value,
        "receipts_today": receipts_today,
        "issues_today": issues_today
    }


# ============================================
# ITEM APIs
# ============================================

@frappe.whitelist()
def search_items(query, item_group=None, limit=10):
    """
    Tìm kiếm Item cho autocomplete
    
    Args:
        query: Từ khóa tìm kiếm
        item_group: Lọc theo nhóm hàng (tùy chọn)
        limit: Số kết quả tối đa
    """
    filters = {"is_stock_item": 1, "disabled": 0}
    if item_group:
        filters["item_group"] = item_group
    
    items = frappe.get_all(
        "Item",
        filters=filters,
        or_filters={
            "item_code": ["like", f"%{query}%"],
            "item_name": ["like", f"%{query}%"]
        },
        fields=["item_code", "item_name", "stock_uom", "item_group", "image"],
        limit=int(limit)
    )
    
    return items


@frappe.whitelist()
def get_item_stock(item_code, warehouse=None):
    """
    Lấy số lượng tồn kho của Item
    
    Args:
        item_code: Mã hàng hóa
        warehouse: Kho cụ thể (tùy chọn, nếu không sẽ lấy tất cả kho)
    """
    filters = {"item_code": item_code}
    if warehouse:
        filters["warehouse"] = warehouse
    
    bins = frappe.get_all(
        "Bin",
        filters=filters,
        fields=["warehouse", "actual_qty", "reserved_qty", "ordered_qty", "stock_value"]
    )
    
    total_qty = sum(b.actual_qty for b in bins)
    total_value = sum(b.stock_value for b in bins)
    
    return {
        "item_code": item_code,
        "total_qty": total_qty,
        "total_value": total_value,
        "by_warehouse": bins
    }


# ============================================
# WAREHOUSE APIs
# ============================================

@frappe.whitelist()
def get_warehouses(is_group=None):
    """
    Lấy danh sách kho
    """
    filters = {"disabled": 0}
    if is_group is not None:
        filters["is_group"] = int(is_group)
    
    return frappe.get_all(
        "Warehouse",
        filters=filters,
        fields=["name", "warehouse_name", "parent_warehouse", "is_group", "warehouse_type"],
        order_by="name"
    )


# ============================================
# BOM APIs
# ============================================

@frappe.whitelist()
def get_bom_items(bom_no):
    """
    Lấy danh sách nguyên liệu trong BOM
    """
    bom = frappe.get_doc("BOM", bom_no)
    
    items = []
    for item in bom.items:
        items.append({
            "item_code": item.item_code,
            "item_name": item.item_name,
            "qty": item.qty,
            "qty_required": item.qty * bom.quantity,  # Thêm qty_required cho frontend
            "uom": item.uom,
            "rate": item.rate,
            "amount": item.amount,
            "source_warehouse": item.source_warehouse
        })
    
    return items  # Trả về list thay vì dict cho frontend đơn giản hơn


@frappe.whitelist()
def get_items():
    """
    Lấy danh sách Item cho dropdown
    """
    return frappe.get_all(
        "Item",
        filters={"is_stock_item": 1, "disabled": 0},
        fields=["item_code", "item_name", "stock_uom", "item_group"],
        order_by="item_name",
        limit=100
    )
