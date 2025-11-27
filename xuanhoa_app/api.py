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
def create_material_receipt(items=None, posting_date=None, remarks=None, item_code=None, qty=None, warehouse=None, rate=None):
    """
    Tạo phiếu nhập kho - Hỗ trợ 1 hoặc nhiều sản phẩm
    
    Args:
        items: Danh sách sản phẩm (JSON array)
            [{"item_code": "NVL-001", "qty": 100, "basic_rate": 1000, "t_warehouse": "Kho Chính"}]
        posting_date: Ngày nhập (YYYY-MM-DD)
        remarks: Ghi chú
        
        # Legacy params (tương thích ngược)
        item_code: Mã hàng hóa (nếu nhập 1 sản phẩm)
        qty: Số lượng nhập
        warehouse: Kho nhập (target warehouse)
        rate: Đơn giá
    
    Returns:
        dict: {success: bool, name: str, message: str}
    
    Example (Multi-item):
        POST /api/method/xuanhoa_app.api.create_material_receipt
        {
            "items": [
                {"item_code": "NVL-001", "qty": 100, "basic_rate": 1000, "t_warehouse": "Kho Chính - XHTB"},
                {"item_code": "NVL-002", "qty": 50, "basic_rate": 500, "t_warehouse": "Kho Chính - XHTB"}
            ],
            "posting_date": "2025-01-15",
            "remarks": "Nhập hàng theo PO-001"
        }
    
    Example (Single item - Legacy):
        POST /api/method/xuanhoa_app.api.create_material_receipt
        {
            "item_code": "NVL-001",
            "qty": 100,
            "warehouse": "Kho Chính - XHTB",
            "rate": 1000
        }
    """
    import json
    
    try:
        doc = frappe.new_doc("Stock Entry")
        doc.purpose = "Material Receipt"
        doc.stock_entry_type = "Material Receipt"
        doc.company = frappe.defaults.get_user_default("Company") or "XUÂN HÒA THÁI BÌNH"
        
        if posting_date:
            doc.posting_date = posting_date
        
        if remarks:
            doc.remarks = remarks
        
        # Parse items if it's a JSON string
        if items and isinstance(items, str):
            items = json.loads(items)
        
        # Multi-item mode
        if items and isinstance(items, list) and len(items) > 0:
            for item_data in items:
                row = doc.append("items", {})
                row.item_code = item_data.get("item_code")
                row.qty = float(item_data.get("qty", 0))
                row.t_warehouse = item_data.get("t_warehouse")
                if item_data.get("basic_rate"):
                    row.basic_rate = float(item_data.get("basic_rate"))
        
        # Legacy single-item mode
        elif item_code and qty and warehouse:
            row = doc.append("items", {})
            row.item_code = item_code
            row.qty = float(qty)
            row.t_warehouse = warehouse
            if rate:
                row.basic_rate = float(rate)
        else:
            return {
                "success": False,
                "message": _("Vui lòng cung cấp danh sách sản phẩm")
            }
        
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
def get_stock_entries(purpose=None, stock_entry_type=None, limit=20, offset=0, search=None, from_date=None, to_date=None, warehouse=None, page=None, page_size=None):
    """
    Lấy danh sách Stock Entry (phiếu nhập/xuất kho) với tìm kiếm, filter và phân trang
    
    Args:
        purpose: Loại phiếu (Material Receipt, Material Issue, Manufacture, etc.)
        stock_entry_type: Loại Stock Entry (Material Receipt, Material Issue, etc.)
        limit: Số lượng kết quả tối đa (mặc định 20)
        offset: Vị trí bắt đầu (dùng cho phân trang)
        page: Số trang (1-based, dùng thay cho offset)
        page_size: Số bản ghi mỗi trang (dùng thay cho limit)
        search: Từ khóa tìm kiếm (mã phiếu, tên item)
        from_date: Ngày bắt đầu (YYYY-MM-DD)
        to_date: Ngày kết thúc (YYYY-MM-DD)
        warehouse: Lọc theo kho
    
    Returns:
        dict: {data: list, total: int, page: int, page_size: int, total_pages: int}
    """
    # Hỗ trợ cả offset/limit và page/page_size
    if page is not None and page_size is not None:
        page = int(page)
        page_size = int(page_size)
        limit = page_size
        offset = (page - 1) * page_size
    else:
        limit = int(limit)
        offset = int(offset)
        page_size = limit
        page = (offset // limit) + 1 if limit > 0 else 1
    
    filters = {}  # Lấy cả draft và submitted
    if purpose:
        filters["purpose"] = purpose
    if stock_entry_type:
        filters["stock_entry_type"] = stock_entry_type
    if from_date:
        filters["posting_date"] = [">=", from_date]
    if to_date:
        if "posting_date" in filters:
            filters["posting_date"] = ["between", [from_date, to_date]]
        else:
            filters["posting_date"] = ["<=", to_date]
    
    # Tìm kiếm theo mã phiếu
    if search:
        filters["name"] = ["like", f"%{search}%"]
    
    # Đếm tổng số bản ghi
    total_count = frappe.db.count("Stock Entry", filters=filters)
    
    entries = frappe.get_all(
        "Stock Entry",
        filters=filters,
        fields=[
            "name", "purpose", "stock_entry_type", "posting_date",
            "posting_time", "company", "docstatus", "creation",
            "owner", "modified_by", "remarks", "total_outgoing_value",
            "total_incoming_value", "total_amount"
        ],
        order_by="creation desc",
        limit_start=offset,
        limit_page_length=limit
    )
    
    # Lấy thông tin items cho mỗi entry
    for entry in entries:
        items = frappe.get_all(
            "Stock Entry Detail",
            filters={"parent": entry.name},
            fields=[
                "item_code", "item_name", "qty", "uom",
                "s_warehouse", "t_warehouse", "basic_rate", "amount"
            ]
        )
        entry["items"] = items
        
        # Lấy warehouse đích (cho Material Receipt) hoặc nguồn (cho Material Issue)
        if items:
            entry["to_warehouse"] = items[0].get("t_warehouse")
            entry["from_warehouse"] = items[0].get("s_warehouse")
        
        # Lấy tên người thực hiện
        entry["owner_name"] = frappe.db.get_value("User", entry.owner, "full_name") or entry.owner
        
        # Tính tổng số lượng items
        entry["total_qty"] = sum(item.get("qty", 0) for item in items)
        entry["item_count"] = len(items)
    
    # Lọc theo warehouse nếu có
    if warehouse:
        entries = [e for e in entries if e.get("to_warehouse") == warehouse or e.get("from_warehouse") == warehouse]
        # Cập nhật total_count nếu có filter warehouse
        total_count = len(entries)
    
    # Tính tổng số trang
    total_pages = (total_count + page_size - 1) // page_size if page_size > 0 else 1
    
    return {
        "data": entries,
        "total": total_count,
        "page": page,
        "page_size": page_size,
        "total_pages": total_pages
    }


@frappe.whitelist()
def get_stock_entry_detail(name):
    """
    Lấy chi tiết một Stock Entry
    
    Args:
        name: Mã phiếu (MAT-STE-YYYY-XXXXX)
    
    Returns:
        dict: Chi tiết phiếu với items
    """
    if not frappe.db.exists("Stock Entry", name):
        return {"success": False, "message": _("Không tìm thấy phiếu {0}").format(name)}
    
    doc = frappe.get_doc("Stock Entry", name)
    
    # Lấy thông tin items
    items = []
    for item in doc.items:
        items.append({
            "item_code": item.item_code,
            "item_name": item.item_name,
            "qty": item.qty,
            "uom": item.uom,
            "s_warehouse": item.s_warehouse,
            "t_warehouse": item.t_warehouse,
            "basic_rate": item.basic_rate,
            "valuation_rate": item.valuation_rate,
            "amount": item.amount,
            "batch_no": item.batch_no,
            "serial_no": item.serial_no
        })
    
    # Lấy tên người thực hiện
    owner_name = frappe.db.get_value("User", doc.owner, "full_name") or doc.owner
    modified_by_name = frappe.db.get_value("User", doc.modified_by, "full_name") or doc.modified_by
    
    return {
        "success": True,
        "name": doc.name,
        "purpose": doc.purpose,
        "stock_entry_type": doc.stock_entry_type,
        "posting_date": str(doc.posting_date),
        "posting_time": str(doc.posting_time),
        "company": doc.company,
        "docstatus": doc.docstatus,
        "remarks": doc.remarks,
        "total_outgoing_value": doc.total_outgoing_value,
        "total_incoming_value": doc.total_incoming_value,
        "total_amount": doc.total_amount,
        "items": items,
        "owner": doc.owner,
        "owner_name": owner_name,
        "modified_by": doc.modified_by,
        "modified_by_name": modified_by_name,
        "creation": str(doc.creation),
        "modified": str(doc.modified),
        "to_warehouse": items[0].get("t_warehouse") if items else None,
        "from_warehouse": items[0].get("s_warehouse") if items else None
    }


@frappe.whitelist()
def create_material_issue(items=None, posting_date=None, remarks=None, item_code=None, qty=None, warehouse=None, cost_center=None):
    """
    Tạo phiếu xuất kho - Hỗ trợ 1 hoặc nhiều sản phẩm
    
    Args:
        items: Danh sách sản phẩm (JSON array)
            [{"item_code": "NVL-001", "qty": 100, "s_warehouse": "Kho Chính"}]
        posting_date: Ngày xuất (YYYY-MM-DD)
        remarks: Ghi chú
        cost_center: Trung tâm chi phí (tùy chọn)
        
        # Legacy params (tương thích ngược)
        item_code: Mã hàng hóa (nếu xuất 1 sản phẩm)
        qty: Số lượng xuất
        warehouse: Kho xuất (source warehouse)
    
    Returns:
        dict: {success: bool, name: str, message: str}
    
    Example (Multi-item):
        POST /api/method/xuanhoa_app.api.create_material_issue
        {
            "items": [
                {"item_code": "NVL-001", "qty": 100, "s_warehouse": "Kho Chính - XHTB"},
                {"item_code": "NVL-002", "qty": 50, "s_warehouse": "Kho Chính - XHTB"}
            ],
            "posting_date": "2025-01-15",
            "remarks": "Xuất kho cho sản xuất"
        }
    
    Example (Single item - Legacy):
        POST /api/method/xuanhoa_app.api.create_material_issue
        {
            "item_code": "NVL-001",
            "qty": 100,
            "warehouse": "Kho Chính - XHTB"
        }
    """
    import json
    
    try:
        doc = frappe.new_doc("Stock Entry")
        doc.purpose = "Material Issue"
        doc.stock_entry_type = "Material Issue"
        doc.company = frappe.defaults.get_user_default("Company") or "XUÂN HÒA THÁI BÌNH"
        
        if posting_date:
            doc.posting_date = posting_date
        
        if remarks:
            doc.remarks = remarks
        
        # Parse items if it's a JSON string
        if items and isinstance(items, str):
            items = json.loads(items)
        
        # Multi-item mode
        if items and isinstance(items, list) and len(items) > 0:
            for item_data in items:
                row = doc.append("items", {})
                row.item_code = item_data.get("item_code")
                row.qty = float(item_data.get("qty", 0))
                row.s_warehouse = item_data.get("s_warehouse")
                if cost_center:
                    row.cost_center = cost_center
        
        # Legacy single-item mode
        elif item_code and qty and warehouse:
            row = doc.append("items", {})
            row.item_code = item_code
            row.qty = float(qty)
            row.s_warehouse = warehouse
            if cost_center:
                row.cost_center = cost_center
        else:
            return {
                "success": False,
                "message": _("Vui lòng cung cấp danh sách sản phẩm")
            }
        
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


@frappe.whitelist()
def get_recent_activities(limit=10):
    """
    Lấy hoạt động gần đây cho Dashboard
    
    Bao gồm:
    - Phiếu nhập/xuất kho đã duyệt
    - Work Order hoàn thành
    - Các giao dịch Stock Entry
    
    Returns:
        list: Danh sách hoạt động gần đây
    """
    from frappe.utils import time_diff_in_seconds, now_datetime
    
    activities = []
    
    # Lấy Stock Entry gần đây (nhập/xuất kho)
    stock_entries = frappe.get_all(
        "Stock Entry",
        filters={"docstatus": 1},
        fields=[
            "name", "purpose", "stock_entry_type", "posting_date", "posting_time",
            "creation", "owner", "modified_by", "modified"
        ],
        order_by="modified desc",
        limit=int(limit)
    )
    
    for entry in stock_entries:
        # Lấy thông tin items
        items = frappe.get_all(
            "Stock Entry Detail",
            filters={"parent": entry.name},
            fields=["item_code", "item_name", "qty", "uom", "t_warehouse", "s_warehouse"]
        )
        
        # Xây dựng description
        if items:
            first_item = items[0]
            item_count = len(items)
            if entry.purpose == "Material Receipt":
                desc = f"{first_item.item_name} - {first_item.qty} {first_item.uom}"
                if first_item.t_warehouse:
                    desc += f" vào {first_item.t_warehouse.split(' - ')[0]}"
                if item_count > 1:
                    desc += f" (+{item_count - 1} sản phẩm khác)"
            elif entry.purpose == "Material Issue":
                desc = f"{first_item.item_name} - {first_item.qty} {first_item.uom}"
                if first_item.s_warehouse:
                    desc += f" từ {first_item.s_warehouse.split(' - ')[0]}"
                if item_count > 1:
                    desc += f" (+{item_count - 1} sản phẩm khác)"
            elif entry.purpose == "Manufacture":
                desc = f"Hoàn thành sản xuất {first_item.item_name} - {first_item.qty} {first_item.uom}"
            else:
                desc = f"{first_item.item_name} - {first_item.qty} {first_item.uom}"
        else:
            desc = entry.purpose
        
        # Lấy tên người thực hiện
        owner_name = frappe.db.get_value("User", entry.owner, "full_name") or entry.owner
        owner_initial = owner_name[0].upper() if owner_name else "?"
        
        # Lấy tên người duyệt (modified_by nếu khác owner)
        approver = None
        if entry.modified_by and entry.modified_by != entry.owner:
            approver = frappe.db.get_value("User", entry.modified_by, "full_name") or entry.modified_by
        
        # Tính thời gian
        time_ago = get_time_ago(entry.modified)
        
        # Xác định loại activity
        activity_type = "receipt" if entry.purpose == "Material Receipt" else \
                       "issue" if entry.purpose == "Material Issue" else \
                       "manufacture" if entry.purpose == "Manufacture" else "transfer"
        
        # Xác định title
        title_map = {
            "Material Receipt": f"Nhập kho {entry.name}",
            "Material Issue": f"Xuất kho {entry.name}",
            "Manufacture": f"Hoàn thành sản xuất {entry.name}",
            "Material Transfer for Manufacture": f"Cấp phát NVL {entry.name}",
        }
        title = title_map.get(entry.purpose, f"{entry.purpose} {entry.name}")
        
        activities.append({
            "id": entry.name,
            "type": activity_type,
            "title": title,
            "description": desc,
            "time": time_ago,
            "timestamp": str(entry.modified),
            "user": owner_name,
            "userInitial": owner_initial,
            "approver": approver,
            "doctype": "Stock Entry",
            "docname": entry.name
        })
    
    # Sắp xếp theo thời gian
    activities.sort(key=lambda x: x["timestamp"], reverse=True)
    
    return activities[:int(limit)]


def get_time_ago(dt):
    """
    Chuyển đổi datetime thành chuỗi "X phút trước", "X giờ trước"
    """
    from frappe.utils import now_datetime, time_diff_in_seconds
    
    if not dt:
        return ""
    
    seconds = time_diff_in_seconds(now_datetime(), dt)
    
    if seconds < 60:
        return "Vừa xong"
    elif seconds < 3600:
        minutes = int(seconds / 60)
        return f"{minutes} phút trước"
    elif seconds < 86400:
        hours = int(seconds / 3600)
        return f"{hours} giờ trước"
    elif seconds < 604800:
        days = int(seconds / 86400)
        return f"{days} ngày trước"
    else:
        weeks = int(seconds / 604800)
        return f"{weeks} tuần trước"


# ============================================
# ITEM APIs
# ============================================

@frappe.whitelist()
def search_items(query, item_group=None, warehouse=None, limit=10):
    """
    Tìm kiếm Item cho autocomplete
    
    Args:
        query: Từ khóa tìm kiếm
        item_group: Lọc theo nhóm hàng (tùy chọn)
        warehouse: Kho cụ thể để lấy tồn kho (tùy chọn)
        limit: Số kết quả tối đa
    
    Returns:
        list: Danh sách items với giá và số lượng tồn kho
            - actual_qty: Tổng tồn kho tất cả kho
            - warehouse_qty: Tồn kho của kho được chọn (nếu có)
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
        fields=["item_code", "item_name", "stock_uom", "item_group", "image", "standard_rate", "valuation_rate"],
        limit=int(limit)
    )
    
    # Thêm thông tin tồn kho từ Bin
    for item in items:
        # Lấy tổng tồn kho từ tất cả kho
        bin_data = frappe.db.sql("""
            SELECT SUM(actual_qty) as total_qty, 
                   MAX(valuation_rate) as bin_valuation_rate
            FROM `tabBin` 
            WHERE item_code = %s
        """, item.item_code, as_dict=True)
        
        if bin_data and bin_data[0]:
            item["actual_qty"] = bin_data[0].get("total_qty") or 0
            # Ưu tiên valuation_rate từ Bin, rồi đến standard_rate từ Item
            if bin_data[0].get("bin_valuation_rate"):
                item["valuation_rate"] = bin_data[0].get("bin_valuation_rate")
        else:
            item["actual_qty"] = 0
        
        # Nếu có warehouse, lấy thêm tồn kho của kho đó
        if warehouse:
            wh_bin = frappe.db.sql("""
                SELECT actual_qty, valuation_rate
                FROM `tabBin` 
                WHERE item_code = %s AND warehouse = %s
            """, (item.item_code, warehouse), as_dict=True)
            
            if wh_bin and wh_bin[0]:
                item["warehouse_qty"] = wh_bin[0].get("actual_qty") or 0
                # Cập nhật valuation_rate từ kho được chọn
                if wh_bin[0].get("valuation_rate"):
                    item["valuation_rate"] = wh_bin[0].get("valuation_rate")
            else:
                item["warehouse_qty"] = 0
        else:
            item["warehouse_qty"] = None  # Chưa chọn kho
        
        # Đảm bảo có rate để frontend sử dụng
        item["rate"] = item.get("valuation_rate") or item.get("standard_rate") or 0
    
    return items


@frappe.whitelist()
def get_item_stock(item_code, warehouse=None):
    """
    Lấy số lượng tồn kho của Item
    
    Args:
        item_code: Mã hàng hóa
        warehouse: Kho cụ thể (tùy chọn, nếu không sẽ lấy tất cả kho)
    
    Returns:
        dict: {item_code, total_qty, total_value, by_warehouse: [...]}
    """
    # Always get all warehouses first for accurate totals
    all_bins = frappe.get_all(
        "Bin",
        filters={"item_code": item_code},
        fields=["warehouse", "actual_qty", "reserved_qty", "ordered_qty", "stock_value", "valuation_rate"]
    )
    
    total_qty = sum(b.actual_qty or 0 for b in all_bins)
    total_value = sum(b.stock_value or 0 for b in all_bins)
    
    # Calculate average valuation rate
    avg_valuation_rate = 0
    if total_qty > 0:
        avg_valuation_rate = total_value / total_qty
    
    # If specific warehouse requested, filter the results
    if warehouse:
        filtered_bins = [b for b in all_bins if b.warehouse == warehouse]
        warehouse_qty = sum(b.actual_qty or 0 for b in filtered_bins)
        warehouse_value = sum(b.stock_value or 0 for b in filtered_bins)
        warehouse_rate = 0
        if filtered_bins and filtered_bins[0].valuation_rate:
            warehouse_rate = filtered_bins[0].valuation_rate
        elif warehouse_qty > 0:
            warehouse_rate = warehouse_value / warehouse_qty
        
        return {
            "item_code": item_code,
            "total_qty": total_qty,  # Total across all warehouses
            "total_value": total_value,
            "warehouse_qty": warehouse_qty,  # Specific warehouse qty
            "warehouse_value": warehouse_value,
            "valuation_rate": warehouse_rate or avg_valuation_rate,
            "by_warehouse": all_bins  # Return all for reference
        }
    
    return {
        "item_code": item_code,
        "total_qty": total_qty,
        "total_value": total_value,
        "valuation_rate": avg_valuation_rate,
        "by_warehouse": all_bins
    }


# ============================================
# WAREHOUSE APIs
# ============================================

@frappe.whitelist()
def get_warehouses(is_group=None, company=None):
    """
    Lấy danh sách kho (chỉ lấy kho không bị disabled và không phải group)
    
    Args:
        is_group: Lọc theo loại kho (0 = kho thực, 1 = kho nhóm)
        company: Lọc theo công ty (nếu không truyền, lấy theo default company của user)
    
    Returns:
        list: Danh sách warehouse với thông tin cơ bản
    """
    filters = {"disabled": 0}
    if is_group is not None:
        filters["is_group"] = int(is_group)
    else:
        # Mặc định chỉ lấy kho leaf (không phải group)
        filters["is_group"] = 0
    
    # Lọc theo company - QUAN TRỌNG để tránh lỗi warehouse không khớp company
    if company:
        filters["company"] = company
    else:
        default_company = frappe.defaults.get_user_default("Company")
        if default_company:
            filters["company"] = default_company
    
    return frappe.get_all(
        "Warehouse",
        filters=filters,
        fields=["name", "warehouse_name", "parent_warehouse", "is_group", "warehouse_type", "company"],
        order_by="warehouse_name"
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
