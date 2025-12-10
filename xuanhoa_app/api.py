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
def get_work_orders(status=None, docstatus=None, limit=50, page=1):
    """
    Lấy danh sách Work Order với filter và phân trang
    
    Args:
        status: Lọc theo trạng thái (Draft, Not Started, In Process, Completed, Stopped)
        docstatus: Lọc theo trạng thái duyệt (0=Draft, 1=Submitted)
        limit: Số lượng kết quả mỗi trang
        page: Số trang (bắt đầu từ 1)
    
    Returns:
        dict: {data: list, total: int, page: int, total_pages: int}
    """
    filters = {}
    
    # Lọc theo docstatus
    if docstatus is not None:
        filters["docstatus"] = int(docstatus)
    
    # Lọc theo status
    if status:
        if status == "Draft":
            filters["docstatus"] = 0
        else:
            filters["status"] = status
            if "docstatus" not in filters:
                filters["docstatus"] = 1  # Submitted by default for non-draft
    
    # Pagination
    limit = int(limit)
    page = int(page)
    offset = (page - 1) * limit
    
    # Count total
    total_count = frappe.db.count("Work Order", filters=filters)
    
    orders = frappe.get_all(
        "Work Order",
        filters=filters,
        fields=[
            "name", "production_item", "item_name", 
            "qty", "produced_qty", "status", "docstatus",
            "planned_start_date", "expected_delivery_date",
            "wip_warehouse", "fg_warehouse", "source_warehouse",
            "bom_no", "creation", "modified", "owner"
        ],
        order_by="modified desc",
        limit_start=offset,
        limit_page_length=limit
    )
    
    # Enhance data
    for order in orders:
        # Tính phần trăm hoàn thành
        if order.qty > 0:
            order["progress"] = round((order.produced_qty / order.qty) * 100, 1)
        else:
            order["progress"] = 0
        
        # Lấy tên người tạo
        order["owner_name"] = frappe.db.get_value("User", order.owner, "full_name") or order.owner
        
        # Thêm status display
        if order.docstatus == 0:
            order["status_display"] = "Chờ duyệt"
            order["status_color"] = "warning"
        elif order.status == "Not Started":
            order["status_display"] = "Chưa bắt đầu"
            order["status_color"] = "info"
        elif order.status == "In Process":
            order["status_display"] = "Đang sản xuất"
            order["status_color"] = "primary"
        elif order.status == "Completed":
            order["status_display"] = "Hoàn thành"
            order["status_color"] = "success"
        elif order.status == "Stopped":
            order["status_display"] = "Đã dừng"
            order["status_color"] = "error"
        else:
            order["status_display"] = order.status
            order["status_color"] = "gray"
    
    total_pages = (total_count + limit - 1) // limit if limit > 0 else 1
    
    return {
        "data": orders,
        "total": total_count,
        "page": page,
        "page_size": limit,
        "total_pages": total_pages
    }


@frappe.whitelist()
def get_work_order_detail(work_order_name):
    """
    Lấy chi tiết Work Order bao gồm nguyên liệu cần thiết
    
    Args:
        work_order_name: Mã Work Order
    
    Returns:
        dict: Thông tin chi tiết Work Order
    """
    if not frappe.db.exists("Work Order", work_order_name):
        return {"success": False, "message": _("Không tìm thấy lệnh sản xuất {0}").format(work_order_name)}
    
    doc = frappe.get_doc("Work Order", work_order_name)
    
    # Lấy thông tin nguyên liệu
    required_items = []
    for item in doc.required_items:
        # Lấy tồn kho hiện tại - ưu tiên dùng source_warehouse của Work Order
        warehouse = doc.source_warehouse or item.source_warehouse
        actual_qty = frappe.db.get_value("Bin", {
            "item_code": item.item_code,
            "warehouse": warehouse
        }, "actual_qty") or 0
        
        required_items.append({
            "item_code": item.item_code,
            "item_name": item.item_name,
            "required_qty": item.required_qty,
            "transferred_qty": item.transferred_qty or 0,
            "consumed_qty": item.consumed_qty or 0,
            "available_qty": actual_qty,  # Tồn kho tại kho nguồn
            "available_qty_at_source": actual_qty,  # Alias for backward compatibility
            "source_warehouse": warehouse,  # Dùng warehouse thực tế
            "uom": frappe.db.get_value("Item", item.item_code, "stock_uom") or "Nos"
        })
    
    # Lấy tên người tạo/duyệt
    owner_name = frappe.db.get_value("User", doc.owner, "full_name") or doc.owner
    
    # Lấy Stock Entries liên quan
    stock_entries = frappe.get_all(
        "Stock Entry",
        filters={"work_order": work_order_name, "docstatus": 1},
        fields=["name", "purpose", "posting_date", "fg_completed_qty", "creation"],
        order_by="creation desc"
    )
    
    # Status display
    if doc.docstatus == 0:
        status_display = "Chờ duyệt"
        status_color = "warning"
    elif doc.status == "Not Started":
        status_display = "Chưa bắt đầu"
        status_color = "info"
    elif doc.status == "In Process":
        status_display = "Đang sản xuất"
        status_color = "primary"
    elif doc.status == "Completed":
        status_display = "Hoàn thành"
        status_color = "success"
    elif doc.status == "Stopped":
        status_display = "Đã dừng"
        status_color = "error"
    else:
        status_display = doc.status
        status_color = "gray"
    
    return {
        "success": True,
        "name": doc.name,
        "production_item": doc.production_item,
        "item_name": doc.item_name,
        "qty": doc.qty,
        "produced_qty": doc.produced_qty,
        "status": doc.status,
        "docstatus": doc.docstatus,
        "status_display": status_display,
        "status_color": status_color,
        "bom_no": doc.bom_no,
        "wip_warehouse": doc.wip_warehouse,
        "fg_warehouse": doc.fg_warehouse,
        "source_warehouse": doc.source_warehouse,
        "planned_start_date": str(doc.planned_start_date) if doc.planned_start_date else None,
        "expected_delivery_date": str(doc.expected_delivery_date) if doc.expected_delivery_date else None,
        "required_items": required_items,
        "stock_entries": stock_entries,
        "progress": round((doc.produced_qty / doc.qty) * 100, 1) if doc.qty > 0 else 0,
        "owner": doc.owner,
        "owner_name": owner_name,
        "creation": str(doc.creation),
        "modified": str(doc.modified)
    }


@frappe.whitelist()
def get_boms(item_code=None, is_active=1, is_default=None):
    """
    Lấy danh sách BOM để chọn khi tạo Work Order
    
    Args:
        item_code: Lọc theo sản phẩm (tùy chọn)
        is_active: Chỉ lấy BOM đang hoạt động (mặc định = 1)
        is_default: Chỉ lấy BOM mặc định (tùy chọn, chỉ filter khi = 1)
    
    Returns:
        list: Danh sách BOM
    """
    filters = {"docstatus": 1}
    
    if is_active is not None and int(is_active) == 1:
        filters["is_active"] = 1
    
    # Chỉ filter is_default khi muốn lấy BOM mặc định (is_default=1)
    # Không filter khi is_default=0 hoặc None (lấy tất cả)
    if is_default is not None and int(is_default) == 1:
        filters["is_default"] = 1
    
    if item_code:
        filters["item"] = item_code
    
    boms = frappe.get_all(
        "BOM",
        filters=filters,
        fields=[
            "name", "item", "item_name", "quantity", 
            "is_active", "is_default", "total_cost",
            "company", "currency"
        ],
        order_by="is_default desc, modified desc"
    )
    
    # Thêm thông tin bổ sung
    for bom in boms:
        # Đếm số nguyên liệu
        bom["item_count"] = frappe.db.count("BOM Item", {"parent": bom.name})
        
        # Lấy stock_uom của sản phẩm
        bom["uom"] = frappe.db.get_value("Item", bom.item, "stock_uom") or "Nos"
    
    return boms


@frappe.whitelist()
def get_bom_detail(bom_no):
    """
    Lấy chi tiết BOM bao gồm danh sách nguyên liệu
    
    Args:
        bom_no: Mã BOM
    
    Returns:
        dict: Chi tiết BOM
    """
    if not frappe.db.exists("BOM", bom_no):
        return {"success": False, "message": _("Không tìm thấy BOM {0}").format(bom_no)}
    
    doc = frappe.get_doc("BOM", bom_no)
    
    items = []
    for item in doc.items:
        items.append({
            "item_code": item.item_code,
            "item_name": item.item_name,
            "qty": item.qty,
            "uom": item.uom,
            "stock_uom": item.stock_uom,
            "rate": item.rate or 0,
            "amount": item.amount or 0,
            "source_warehouse": item.source_warehouse
        })
    
    return {
        "success": True,
        "name": doc.name,
        "item": doc.item,
        "item_name": doc.item_name,
        "quantity": doc.quantity,
        "uom": doc.uom,
        "is_active": doc.is_active,
        "is_default": doc.is_default,
        "raw_material_cost": doc.raw_material_cost or 0,
        "total_cost": doc.total_cost or 0,
        "items": items
    }


@frappe.whitelist()
def create_work_order(bom_no, qty, planned_start_date=None, expected_delivery_date=None, 
                      source_warehouse=None, wip_warehouse=None, fg_warehouse=None):
    """
    Tạo Work Order mới (Draft - chờ duyệt)
    
    Args:
        bom_no: Mã BOM
        qty: Số lượng cần sản xuất
        planned_start_date: Ngày bắt đầu dự kiến
        expected_delivery_date: Ngày hoàn thành dự kiến
        source_warehouse: Kho nguồn nguyên liệu
        wip_warehouse: Kho sản xuất dở dang
        fg_warehouse: Kho thành phẩm
    
    Returns:
        dict: {success: bool, name: str, message: str}
    """
    try:
        # Validate BOM
        if not frappe.db.exists("BOM", bom_no):
            return {"success": False, "message": _("Định mức sản xuất (BOM) không tồn tại. Vui lòng chọn BOM khác.")}
        
        bom = frappe.get_doc("BOM", bom_no)
        
        if not bom.is_active:
            return {"success": False, "message": _("Định mức sản xuất (BOM) đã ngừng sử dụng. Vui lòng chọn BOM đang hoạt động.")}
        
        company = frappe.defaults.get_user_default("Company") or frappe.db.get_single_value("Global Defaults", "default_company")
        
        if not company:
            return {"success": False, "message": _("Chưa thiết lập công ty mặc định. Vui lòng liên hệ quản trị viên.")}
        
        # Validate qty
        if not qty or float(qty) <= 0:
            return {"success": False, "message": _("Số lượng sản xuất phải lớn hơn 0.")}
        
        # Tạo Work Order
        doc = frappe.new_doc("Work Order")
        doc.production_item = bom.item
        doc.bom_no = bom_no
        doc.qty = float(qty)
        doc.company = company
        
        if planned_start_date:
            doc.planned_start_date = planned_start_date
        
        if expected_delivery_date:
            doc.expected_delivery_date = expected_delivery_date
        
        # Warehouse settings - Tự động lấy warehouse mặc định nếu không truyền vào
        if not source_warehouse:
            # Ưu tiên lấy "Kho Chính - XHTB" trước
            company_abbr = frappe.db.get_value("Company", company, "abbr")
            source_warehouse = f"Kho Chính - {company_abbr}"
            
            # Nếu không tồn tại, lấy kho mặc định từ Stock Settings
            if not frappe.db.exists("Warehouse", source_warehouse):
                source_warehouse = frappe.db.get_single_value("Stock Settings", "default_warehouse")
            
            # Nếu vẫn không có, lấy warehouse đầu tiên không phải group
            if not source_warehouse:
                source_warehouse = frappe.db.get_value("Warehouse", {"is_group": 0}, "name")
        
        if source_warehouse:
            doc.source_warehouse = source_warehouse
            
        if not wip_warehouse:
            # Ưu tiên lấy "Kho Chính - XHTB"
            company_abbr = frappe.db.get_value("Company", company, "abbr")
            wip_warehouse = f"Kho Chính - {company_abbr}"
            if not frappe.db.exists("Warehouse", wip_warehouse):
                # Lấy kho WIP mặc định
                wip_warehouse = frappe.db.get_value("Warehouse", {"warehouse_type": "Work In Progress"}, "name")
            
        if wip_warehouse:
            doc.wip_warehouse = wip_warehouse
            
        if not fg_warehouse:
            # Ưu tiên lấy "Kho Chính - XHTB"
            company_abbr = frappe.db.get_value("Company", company, "abbr")
            fg_warehouse = f"Kho Chính - {company_abbr}"
            if not frappe.db.exists("Warehouse", fg_warehouse):
                # Lấy kho thành phẩm mặc định
                fg_warehouse = frappe.db.get_value("Warehouse", {"warehouse_type": "Finished Goods"}, "name")
                if not fg_warehouse:
                    fg_warehouse = source_warehouse  # Dùng kho nguồn làm kho đích nếu không có kho FG
                
        if fg_warehouse:
            doc.fg_warehouse = fg_warehouse
        
        doc.insert()
        
        # CRITICAL FIX: Cập nhật warehouse cho tất cả Work Order Items
        # ERPNext tự động tạo items từ BOM nhưng có thể dùng warehouse sai
        if doc.required_items:
            for item in doc.required_items:
                if source_warehouse:
                    item.source_warehouse = source_warehouse
            doc.save()
        
        return {
            "success": True,
            "name": doc.name,
            "message": _("Đã tạo lệnh sản xuất {0} - Đang chờ duyệt").format(doc.name)
        }
    except frappe.exceptions.ValidationError as e:
        return {
            "success": False,
            "message": _("Dữ liệu không hợp lệ: {0}").format(str(e))
        }
    except Exception as e:
        frappe.log_error(frappe.get_traceback(), "create_work_order Error")
        error_msg = str(e)
        # Parse common errors
        if "company" in error_msg.lower():
            error_msg = _("Chưa thiết lập công ty. Vui lòng liên hệ quản trị viên.")
        elif "warehouse" in error_msg.lower():
            error_msg = _("Thiết lập kho không hợp lệ. Vui lòng kiểm tra lại cấu hình kho.")
        elif "bom" in error_msg.lower():
            error_msg = _("Định mức sản xuất (BOM) không hợp lệ.")
        return {
            "success": False,
            "message": error_msg
        }


# Helper function để parse lỗi thân thiện
def _parse_friendly_error(error_msg):
    """Parse error message thành thông báo thân thiện với người dùng"""
    error_lower = error_msg.lower()
    
    if "company" in error_lower:
        return _("Chưa thiết lập công ty. Vui lòng liên hệ quản trị viên.")
    elif "warehouse" in error_lower and "not found" in error_lower:
        return _("Kho không tồn tại. Vui lòng kiểm tra lại cấu hình kho.")
    elif "insufficient" in error_lower or "not enough" in error_lower:
        return _("Không đủ tồn kho nguyên vật liệu.")
    elif "permission" in error_lower or "not permitted" in error_lower:
        return _("Bạn không có quyền thực hiện thao tác này.")
    elif "already submitted" in error_lower:
        return _("Lệnh sản xuất đã được duyệt trước đó.")
    elif "cancelled" in error_lower:
        return _("Lệnh sản xuất đã bị hủy.")
    elif "bom" in error_lower:
        return _("Định mức sản xuất (BOM) không hợp lệ.")
    elif "item" in error_lower and "not found" in error_lower:
        return _("Sản phẩm không tồn tại trong hệ thống.")
    else:
        return error_msg


@frappe.whitelist()
def submit_work_order(work_order_name):
    """
    Duyệt Work Order (Draft -> Submitted)
    
    Args:
        work_order_name: Mã Work Order
    
    Returns:
        dict: {success: bool, message: str}
    """
    try:
        if not frappe.db.exists("Work Order", work_order_name):
            return {"success": False, "message": _("Không tìm thấy lệnh sản xuất. Có thể đã bị xóa.")}
        
        doc = frappe.get_doc("Work Order", work_order_name)
        
        if doc.docstatus == 1:
            return {"success": False, "message": _("Lệnh sản xuất này đã được duyệt trước đó.")}
        elif doc.docstatus == 2:
            return {"success": False, "message": _("Lệnh sản xuất này đã bị hủy, không thể duyệt.")}
        
        # CRITICAL FIX: Đảm bảo tất cả Work Order Items có warehouse đúng trước khi submit
        source_warehouse = doc.source_warehouse
        if not source_warehouse:
            # Lấy warehouse mặc định
            company_abbr = frappe.db.get_value("Company", doc.company, "abbr")
            source_warehouse = f"Kho Chính - {company_abbr}"
            if not frappe.db.exists("Warehouse", source_warehouse):
                source_warehouse = frappe.db.get_single_value("Stock Settings", "default_warehouse")
            if source_warehouse:
                doc.source_warehouse = source_warehouse
        
        # Cập nhật warehouse cho tất cả items
        if source_warehouse and doc.required_items:
            for item in doc.required_items:
                if not item.source_warehouse or item.source_warehouse == "Stores - XHTB":
                    item.source_warehouse = source_warehouse
        
        doc.submit()
        
        return {
            "success": True,
            "message": _("Đã duyệt lệnh sản xuất {0}").format(work_order_name)
        }
    except Exception as e:
        frappe.log_error(frappe.get_traceback(), "submit_work_order Error")
        return {
            "success": False,
            "message": _parse_friendly_error(str(e))
        }


@frappe.whitelist()
def start_work_order(work_order_name):
    """
    Bắt đầu sản xuất - Chuyển vật tư từ Stores -> WIP
    
    Tạo Stock Entry loại "Material Transfer for Manufacture"
    """
    try:
        from erpnext.manufacturing.doctype.work_order.work_order import make_stock_entry
        
        if not frappe.db.exists("Work Order", work_order_name):
            return {"success": False, "message": _("Không tìm thấy lệnh sản xuất. Có thể đã bị xóa.")}
        
        work_order = frappe.get_doc("Work Order", work_order_name)
        
        if work_order.docstatus != 1:
            return {
                "success": False,
                "message": _("Lệnh sản xuất chưa được duyệt. Vui lòng duyệt trước khi cấp phát nguyên liệu.")
            }
        
        status_map = {
            "Completed": "đã hoàn thành",
            "Stopped": "đã dừng"
        }
        if work_order.status in status_map:
            return {
                "success": False,
                "message": _("Không thể cấp phát NVL vì lệnh sản xuất {0}.").format(status_map[work_order.status])
            }
        
        # Kiểm tra tồn kho trước khi cấp phát
        insufficient_items = []
        source_warehouse = work_order.source_warehouse
        
        # Nếu chưa có source warehouse, lấy kho "Kho Chính - XHTB" mặc định
        if not source_warehouse:
            # Ưu tiên lấy "Kho Chính - XHTB"
            company_abbr = frappe.db.get_value("Company", work_order.company, "abbr")
            source_warehouse = f"Kho Chính - {company_abbr}"
            
            # Nếu không tồn tại, lấy kho từ Stock Settings
            if not frappe.db.exists("Warehouse", source_warehouse):
                source_warehouse = frappe.db.get_single_value("Stock Settings", "default_warehouse")
            
            # Cập nhật lại Work Order
            if source_warehouse:
                work_order.source_warehouse = source_warehouse
                # CRITICAL FIX: Cập nhật warehouse cho tất cả Work Order Items
                for item in work_order.required_items:
                    item.source_warehouse = source_warehouse
                work_order.save()
            else:
                # Lấy warehouse đầu tiên trong hệ thống
                warehouse = frappe.db.get_value("Warehouse", {"is_group": 0}, "name")
                if warehouse:
                    source_warehouse = warehouse
                    work_order.source_warehouse = source_warehouse
                    # CRITICAL FIX: Cập nhật warehouse cho tất cả Work Order Items
                    for item in work_order.required_items:
                        item.source_warehouse = source_warehouse
                    work_order.save()
        
        if not source_warehouse:
            return {
                "success": False,
                "message": _("Chưa thiết lập kho nguồn nguyên liệu. Vui lòng cập nhật lệnh sản xuất và chọn kho nguồn.")
            }
        
        for item in work_order.required_items:
            required_qty = item.required_qty - item.transferred_qty
            if required_qty <= 0:
                continue
                
            # Lấy tồn kho từ source warehouse
            available_qty = frappe.db.get_value("Bin", 
                {"item_code": item.item_code, "warehouse": source_warehouse},
                "actual_qty"
            ) or 0
            
            if available_qty < required_qty:
                item_name = frappe.db.get_value("Item", item.item_code, "item_name") or item.item_code
                insufficient_items.append({
                    "item_code": item.item_code,
                    "item_name": item_name,
                    "required": required_qty,
                    "available": available_qty,
                    "shortage": required_qty - available_qty
                })
        
        if insufficient_items:
            # Tạo thông báo lỗi chi tiết
            error_lines = [_("Không đủ nguyên vật liệu trong kho:")]
            for item in insufficient_items:
                error_lines.append(
                    f"• {item['item_name']} ({item['item_code']}): Cần {item['required']}, Có {item['available']}, Thiếu {item['shortage']}"
                )
            return {
                "success": False,
                "message": "\n".join(error_lines),
                "insufficient_items": insufficient_items
            }
        
        # Tạo Stock Entry loại "Material Transfer for Manufacture"
        # make_stock_entry returns a dict, so we need to create a doc from it
        stock_entry_dict = make_stock_entry(work_order_name, "Material Transfer for Manufacture", work_order.qty)
        stock_entry = frappe.get_doc(stock_entry_dict)
        stock_entry.insert()
        stock_entry.submit()
        
        return {
            "success": True,
            "stock_entry": stock_entry.name,
            "message": _("Đã cấp phát nguyên vật liệu và bắt đầu sản xuất.")
        }
    except Exception as e:
        frappe.log_error(frappe.get_traceback(), "start_work_order Error")
        return {
            "success": False,
            "message": _parse_friendly_error(str(e))
        }


@frappe.whitelist()
def complete_work_order(work_order_name, qty):
    """
    Hoàn thành sản xuất - Tiêu hao NVL từ WIP, nhập thành phẩm vào FG
    
    Tạo Stock Entry loại "Manufacture"
    """
    try:
        from erpnext.manufacturing.doctype.work_order.work_order import make_stock_entry
        
        if not frappe.db.exists("Work Order", work_order_name):
            return {"success": False, "message": _("Không tìm thấy lệnh sản xuất. Có thể đã bị xóa.")}
        
        work_order = frappe.get_doc("Work Order", work_order_name)
        
        if work_order.docstatus != 1:
            return {
                "success": False,
                "message": _("Lệnh sản xuất chưa được duyệt. Không thể ghi nhận hoàn thành.")
            }
        
        if work_order.status == "Completed":
            return {
                "success": False,
                "message": _("Lệnh sản xuất đã hoàn thành trước đó.")
            }
        
        if work_order.status == "Stopped":
            return {
                "success": False,
                "message": _("Lệnh sản xuất đã dừng. Không thể ghi nhận hoàn thành.")
            }
        
        # Kiểm tra số lượng hợp lệ
        remaining = work_order.qty - work_order.produced_qty
        
        if remaining <= 0:
            return {
                "success": False,
                "message": _("Lệnh sản xuất đã hoàn thành đủ số lượng.")
            }
        
        if float(qty) <= 0:
            return {
                "success": False,
                "message": _("Số lượng hoàn thành phải lớn hơn 0.")
            }
        
        if float(qty) > remaining:
            return {
                "success": False,
                "message": _("Số lượng hoàn thành ({0}) vượt quá số lượng còn lại ({1}).").format(int(qty), int(remaining))
            }
        
        # Tạo Stock Entry loại "Manufacture"
        # make_stock_entry returns a dict, so we need to create a doc from it
        stock_entry_dict = make_stock_entry(work_order_name, "Manufacture", float(qty))
        stock_entry = frappe.get_doc(stock_entry_dict)
        stock_entry.insert()
        stock_entry.submit()
        
        return {
            "success": True,
            "stock_entry": stock_entry.name,
            "produced_qty": qty,
            "message": _("Đã ghi nhận hoàn thành {0} sản phẩm.").format(int(qty))
        }
    except Exception as e:
        frappe.log_error(frappe.get_traceback(), "complete_work_order Error")
        return {
            "success": False,
            "message": _parse_friendly_error(str(e))
        }


@frappe.whitelist()
def stop_work_order(work_order_name):
    """
    Dừng lệnh sản xuất
    
    Args:
        work_order_name: Tên Work Order
    
    Returns:
        dict: {success: bool, message: str}
    """
    try:
        if not frappe.db.exists("Work Order", work_order_name):
            return {"success": False, "message": _("Không tìm thấy lệnh sản xuất. Có thể đã bị xóa.")}
        
        work_order = frappe.get_doc("Work Order", work_order_name)
        
        if work_order.docstatus != 1:
            return {
                "success": False,
                "message": _("Lệnh sản xuất chưa được duyệt. Không cần dừng.")
            }
        
        if work_order.status == "Completed":
            return {
                "success": False,
                "message": _("Lệnh sản xuất đã hoàn thành. Không thể dừng.")
            }
        
        if work_order.status == "Stopped":
            return {
                "success": False,
                "message": _("Lệnh sản xuất đã dừng trước đó.")
            }
        
        # Stop work order
        work_order.db_set("status", "Stopped")
        frappe.db.commit()
        
        return {
            "success": True,
            "message": _("Đã dừng lệnh sản xuất.")
        }
    except Exception as e:
        frappe.log_error(frappe.get_traceback(), "stop_work_order Error")
        return {
            "success": False,
            "message": _parse_friendly_error(str(e))
        }


@frappe.whitelist()
def cancel_work_order(work_order_name):
    """
    Hủy lệnh sản xuất - Chỉ có thể hủy nếu chưa bắt đầu sản xuất
    
    Args:
        work_order_name: Tên Work Order
    
    Returns:
        dict: {success: bool, message: str}
    """
    try:
        if not frappe.db.exists("Work Order", work_order_name):
            return {"success": False, "message": _("Không tìm thấy lệnh sản xuất. Có thể đã bị xóa.")}
        
        work_order = frappe.get_doc("Work Order", work_order_name)
        
        # Nếu còn là Draft (chờ duyệt) -> chỉ cần xóa
        if work_order.docstatus == 0:
            work_order.delete()
            return {
                "success": True,
                "message": _("Đã xóa lệnh sản xuất.")
            }
        
        # Nếu đã submitted
        if work_order.docstatus == 1:
            # Chỉ cho phép hủy nếu chưa bắt đầu sản xuất (chưa có Stock Entry nào)
            stock_entries = frappe.get_all("Stock Entry", 
                filters={"work_order": work_order_name, "docstatus": 1},
                limit=1
            )
            
            if stock_entries:
                return {
                    "success": False,
                    "message": _("Không thể hủy vì đã có phiếu xuất/nhập kho. Vui lòng sử dụng chức năng 'Dừng sản xuất'.")
                }
            
            if work_order.produced_qty > 0:
                return {
                    "success": False,
                    "message": _("Không thể hủy vì đã có sản phẩm hoàn thành. Vui lòng sử dụng chức năng 'Dừng sản xuất'.")
                }
            
            # Cancel work order
            work_order.cancel()
            return {
                "success": True,
                "message": _("Đã hủy lệnh sản xuất.")
            }
        
        # Đã bị hủy rồi
        if work_order.docstatus == 2:
            return {
                "success": False,
                "message": _("Lệnh sản xuất đã được hủy trước đó.")
            }
        
        return {
            "success": False,
            "message": _("Không thể hủy lệnh sản xuất ở trạng thái hiện tại.")
        }
    except Exception as e:
        frappe.log_error(frappe.get_traceback(), "cancel_work_order Error")
        return {
            "success": False,
            "message": _parse_friendly_error(str(e))
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
            - standard_selling_rate: Giá bán tiêu chuẩn
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
    
    # Thêm thông tin tồn kho từ Bin và giá bán từ Item Price
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
        
        # Lấy giá bán tiêu chuẩn từ Item Price (Selling)
        selling_price = frappe.db.sql("""
            SELECT price_list_rate 
            FROM `tabItem Price` 
            WHERE item_code = %s 
              AND selling = 1 
              AND (valid_from IS NULL OR valid_from <= CURDATE())
              AND (valid_upto IS NULL OR valid_upto >= CURDATE())
            ORDER BY valid_from DESC
            LIMIT 1
        """, item.item_code, as_dict=True)
        
        if selling_price and selling_price[0]:
            item["standard_selling_rate"] = selling_price[0].get("price_list_rate") or 0
        else:
            # Fallback: dùng standard_rate hoặc valuation_rate
            item["standard_selling_rate"] = item.get("standard_rate") or item.get("valuation_rate") or 0
        
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


# ============================================
# SUPPLIER APIs
# ============================================

@frappe.whitelist()
def get_suppliers(query=None, limit=20):
    """
    Lấy danh sách nhà cung cấp
    
    Args:
        query: Từ khóa tìm kiếm (tên hoặc mã NCC)
        limit: Số lượng kết quả tối đa
    
    Returns:
        list: Danh sách suppliers
    """
    filters = {"disabled": 0}
    or_filters = {}
    
    if query:
        or_filters = {
            "name": ["like", f"%{query}%"],
            "supplier_name": ["like", f"%{query}%"]
        }
    
    suppliers = frappe.get_all(
        "Supplier",
        filters=filters,
        or_filters=or_filters if query else None,
        fields=["name", "supplier_name", "supplier_group", "country", "default_currency"],
        order_by="supplier_name",
        limit=int(limit)
    )
    
    return suppliers


# ============================================
# CUSTOMER APIs
# ============================================

@frappe.whitelist()
def get_customers(query=None, limit=20):
    """
    Lấy danh sách khách hàng
    
    Args:
        query: Từ khóa tìm kiếm (tên hoặc mã KH)
        limit: Số lượng kết quả tối đa
    
    Returns:
        list: Danh sách customers
    """
    filters = {"disabled": 0}
    or_filters = {}
    
    if query:
        or_filters = {
            "name": ["like", f"%{query}%"],
            "customer_name": ["like", f"%{query}%"]
        }
    
    customers = frappe.get_all(
        "Customer",
        filters=filters,
        or_filters=or_filters if query else None,
        fields=["name", "customer_name", "customer_group", "territory", "default_currency"],
        order_by="customer_name",
        limit=int(limit)
    )
    
    return customers


# ============================================
# PURCHASE INVOICE APIs
# ============================================

@frappe.whitelist()
def get_purchase_invoices(status=None, supplier=None, from_date=None, to_date=None, 
                          search=None, limit=20, page=1):
    """
    Lấy danh sách hóa đơn mua hàng
    
    Args:
        status: Lọc theo trạng thái (Draft, Unpaid, Paid, Overdue, Cancelled)
        supplier: Lọc theo nhà cung cấp
        from_date: Ngày bắt đầu
        to_date: Ngày kết thúc
        search: Tìm kiếm theo mã hóa đơn
        limit: Số bản ghi mỗi trang
        page: Số trang
    
    Returns:
        dict: {data: list, total: int, page: int, total_pages: int}
    """
    filters = {}
    
    # Lọc theo status
    if status:
        if status == "Draft":
            filters["docstatus"] = 0
        elif status == "Cancelled":
            filters["docstatus"] = 2
        elif status == "Unpaid":
            filters["docstatus"] = 1
            filters["outstanding_amount"] = [">", 0]
        elif status == "Paid":
            filters["docstatus"] = 1
            filters["outstanding_amount"] = 0
        elif status == "Overdue":
            filters["docstatus"] = 1
            filters["outstanding_amount"] = [">", 0]
            filters["due_date"] = ["<", frappe.utils.today()]
    
    if supplier:
        filters["supplier"] = supplier
    
    if from_date:
        filters["posting_date"] = [">=", from_date]
    if to_date:
        if "posting_date" in filters:
            filters["posting_date"] = ["between", [from_date, to_date]]
        else:
            filters["posting_date"] = ["<=", to_date]
    
    if search:
        filters["name"] = ["like", f"%{search}%"]
    
    # Pagination
    limit = int(limit)
    page = int(page)
    offset = (page - 1) * limit
    
    # Count total
    total_count = frappe.db.count("Purchase Invoice", filters=filters)
    
    invoices = frappe.get_all(
        "Purchase Invoice",
        filters=filters,
        fields=[
            "name", "supplier", "supplier_name", "posting_date", "due_date",
            "grand_total", "outstanding_amount", "currency", "docstatus",
            "is_paid", "status", "creation", "owner"
        ],
        order_by="creation desc",
        limit_start=offset,
        limit_page_length=limit
    )
    
    # Enhance data
    for inv in invoices:
        # Lấy số lượng items
        inv["item_count"] = frappe.db.count("Purchase Invoice Item", {"parent": inv.name})
        
        # Lấy tên người tạo
        inv["owner_name"] = frappe.db.get_value("User", inv.owner, "full_name") or inv.owner
        
        # Status display
        if inv.docstatus == 0:
            inv["status_display"] = "Chờ duyệt"
            inv["status_color"] = "warning"
        elif inv.docstatus == 2:
            inv["status_display"] = "Đã hủy"
            inv["status_color"] = "gray"
        elif inv.outstanding_amount == 0:
            inv["status_display"] = "Đã thanh toán"
            inv["status_color"] = "success"
        elif inv.due_date and str(inv.due_date) < frappe.utils.today():
            inv["status_display"] = "Quá hạn"
            inv["status_color"] = "error"
        else:
            inv["status_display"] = "Chưa thanh toán"
            inv["status_color"] = "info"
        
        # Kiểm tra đã tạo Stock Entry chưa
        inv["has_stock_entry"] = frappe.db.exists("Stock Entry", {
            "purchase_invoice": inv.name,
            "docstatus": ["!=", 2]
        }) or False
    
    total_pages = (total_count + limit - 1) // limit if limit > 0 else 1
    
    return {
        "data": invoices,
        "total": total_count,
        "page": page,
        "page_size": limit,
        "total_pages": total_pages
    }


@frappe.whitelist()
def get_purchase_invoice_detail(name):
    """
    Lấy chi tiết hóa đơn mua hàng
    
    Args:
        name: Mã hóa đơn
    
    Returns:
        dict: Chi tiết hóa đơn
    """
    if not frappe.db.exists("Purchase Invoice", name):
        return {"success": False, "message": _("Không tìm thấy hóa đơn {0}").format(name)}
    
    doc = frappe.get_doc("Purchase Invoice", name)
    
    # Lấy thông tin items
    items = []
    for item in doc.items:
        items.append({
            "item_code": item.item_code,
            "item_name": item.item_name,
            "qty": item.qty,
            "uom": item.uom,
            "rate": item.rate,
            "amount": item.amount,
            "warehouse": item.warehouse,
            "received_qty": item.received_qty or 0,
            "stock_qty": item.stock_qty or item.qty
        })
    
    # Lấy tên người thực hiện
    owner_name = frappe.db.get_value("User", doc.owner, "full_name") or doc.owner
    
    # Lấy Stock Entries liên quan (tìm qua remarks vì Stock Entry không có trường purchase_invoice)
    # Khi tạo Stock Entry từ Purchase Invoice, ta sẽ lưu reference trong remarks
    stock_entries = []
    se_list = frappe.get_all(
        "Stock Entry",
        filters={
            "docstatus": ["!=", 2],
            "remarks": ["like", f"%{name}%"]
        },
        fields=["name", "purpose", "posting_date", "docstatus", "creation", "remarks"],
        order_by="creation desc"
    )
    # Lọc chính xác để tránh trùng tên (vì LIKE có thể match PINV-001 với PINV-0010)
    for se in se_list:
        se_remarks = se.get("remarks") or ""
        # Check exact match: name should be at word boundary or standalone
        if name in se_remarks:
            stock_entries.append(se)
    
    # Status display
    if doc.docstatus == 0:
        status_display = "Chờ duyệt"
        status_color = "warning"
    elif doc.docstatus == 2:
        status_display = "Đã hủy"
        status_color = "gray"
    elif doc.outstanding_amount == 0:
        status_display = "Đã thanh toán"
        status_color = "success"
    elif doc.due_date and str(doc.due_date) < frappe.utils.today():
        status_display = "Quá hạn"
        status_color = "error"
    else:
        status_display = "Chưa thanh toán"
        status_color = "info"
    
    return {
        "success": True,
        "name": doc.name,
        "supplier": doc.supplier,
        "supplier_name": doc.supplier_name,
        "posting_date": str(doc.posting_date),
        "due_date": str(doc.due_date) if doc.due_date else None,
        "grand_total": doc.grand_total,
        "net_total": doc.net_total,
        "total_taxes_and_charges": doc.total_taxes_and_charges,
        "outstanding_amount": doc.outstanding_amount,
        "currency": doc.currency,
        "docstatus": doc.docstatus,
        "status": doc.status,
        "status_display": status_display,
        "status_color": status_color,
        "is_paid": doc.is_paid,
        "remarks": doc.remarks,
        "items": items,
        "stock_entries": stock_entries,
        "owner": doc.owner,
        "owner_name": owner_name,
        "creation": str(doc.creation),
        "modified": str(doc.modified),
        "set_warehouse": doc.set_warehouse,
        "update_stock": doc.update_stock
    }


@frappe.whitelist()
def create_purchase_invoice(supplier, items, posting_date=None, due_date=None, 
                            set_warehouse=None, remarks=None, update_stock=0):
    """
    Tạo hóa đơn mua hàng mới (Draft)
    
    Args:
        supplier: Mã nhà cung cấp
        items: Danh sách sản phẩm (JSON array)
            [{"item_code": "NVL-001", "qty": 100, "rate": 1000, "warehouse": "Kho Chính"}]
        posting_date: Ngày hóa đơn
        due_date: Ngày đến hạn thanh toán
        set_warehouse: Kho mặc định cho tất cả items
        remarks: Ghi chú
        update_stock: Cập nhật tồn kho trực tiếp (0 = không, 1 = có)
    
    Returns:
        dict: {success: bool, name: str, message: str}
    """
    import json
    
    try:
        # Validate supplier
        if not frappe.db.exists("Supplier", supplier):
            return {"success": False, "message": _("Nhà cung cấp không tồn tại.")}
        
        # Parse items
        if items and isinstance(items, str):
            items = json.loads(items)
        
        if not items or len(items) == 0:
            return {"success": False, "message": _("Vui lòng thêm ít nhất một sản phẩm.")}
        
        company = frappe.defaults.get_user_default("Company") or frappe.db.get_single_value("Global Defaults", "default_company")
        
        if not company:
            return {"success": False, "message": _("Chưa thiết lập công ty mặc định.")}
        
        # Tạo Purchase Invoice
        doc = frappe.new_doc("Purchase Invoice")
        doc.supplier = supplier
        doc.company = company
        doc.update_stock = int(update_stock)
        
        if posting_date:
            doc.posting_date = posting_date
        
        if due_date:
            doc.due_date = due_date
        
        if set_warehouse:
            doc.set_warehouse = set_warehouse
        
        if remarks:
            doc.remarks = remarks
        
        # Add items
        for item_data in items:
            row = doc.append("items", {})
            row.item_code = item_data.get("item_code")
            row.qty = float(item_data.get("qty", 0))
            row.rate = float(item_data.get("rate", 0))
            if item_data.get("warehouse"):
                row.warehouse = item_data.get("warehouse")
            elif set_warehouse:
                row.warehouse = set_warehouse
        
        doc.insert()
        
        return {
            "success": True,
            "name": doc.name,
            "message": _("Đã tạo hóa đơn mua hàng {0}").format(doc.name)
        }
    except Exception as e:
        frappe.log_error(frappe.get_traceback(), "create_purchase_invoice Error")
        return {
            "success": False,
            "message": _parse_friendly_error(str(e))
        }


@frappe.whitelist()
def submit_purchase_invoice(name):
    """
    Duyệt hóa đơn mua hàng
    
    Args:
        name: Mã hóa đơn
    
    Returns:
        dict: {success: bool, message: str}
    """
    try:
        if not frappe.db.exists("Purchase Invoice", name):
            return {"success": False, "message": _("Không tìm thấy hóa đơn.")}
        
        doc = frappe.get_doc("Purchase Invoice", name)
        
        if doc.docstatus == 1:
            return {"success": False, "message": _("Hóa đơn đã được duyệt trước đó.")}
        elif doc.docstatus == 2:
            return {"success": False, "message": _("Hóa đơn đã bị hủy, không thể duyệt.")}
        
        doc.submit()
        
        return {
            "success": True,
            "message": _("Đã duyệt hóa đơn mua hàng {0}").format(name)
        }
    except Exception as e:
        frappe.log_error(frappe.get_traceback(), "submit_purchase_invoice Error")
        return {
            "success": False,
            "message": _parse_friendly_error(str(e))
        }


@frappe.whitelist()
def cancel_purchase_invoice(name):
    """
    Hủy hóa đơn mua hàng
    
    Args:
        name: Mã hóa đơn
    
    Returns:
        dict: {success: bool, message: str}
    """
    try:
        if not frappe.db.exists("Purchase Invoice", name):
            return {"success": False, "message": _("Không tìm thấy hóa đơn.")}
        
        doc = frappe.get_doc("Purchase Invoice", name)
        
        if doc.docstatus == 0:
            # Draft - just delete
            doc.delete()
            return {
                "success": True,
                "message": _("Đã xóa hóa đơn mua hàng.")
            }
        elif doc.docstatus == 2:
            return {"success": False, "message": _("Hóa đơn đã bị hủy trước đó.")}
        
        # Check if has linked stock entries
        stock_entries = frappe.get_all("Stock Entry", 
            filters={"purchase_invoice": name, "docstatus": 1},
            limit=1
        )
        if stock_entries:
            return {
                "success": False,
                "message": _("Không thể hủy vì đã có phiếu nhập kho liên kết. Vui lòng hủy phiếu nhập kho trước.")
            }
        
        doc.cancel()
        
        return {
            "success": True,
            "message": _("Đã hủy hóa đơn mua hàng {0}").format(name)
        }
    except Exception as e:
        frappe.log_error(frappe.get_traceback(), "cancel_purchase_invoice Error")
        return {
            "success": False,
            "message": _parse_friendly_error(str(e))
        }


@frappe.whitelist()
def create_stock_entry_from_purchase_invoice(purchase_invoice, warehouse=None):
    """
    Tạo phiếu nhập kho từ hóa đơn mua hàng
    
    Args:
        purchase_invoice: Mã hóa đơn mua hàng
        warehouse: Kho nhập (nếu không truyền sẽ lấy từ Invoice)
    
    Returns:
        dict: {success: bool, name: str, message: str}
    """
    try:
        if not frappe.db.exists("Purchase Invoice", purchase_invoice):
            return {"success": False, "message": _("Không tìm thấy hóa đơn mua hàng.")}
        
        pi = frappe.get_doc("Purchase Invoice", purchase_invoice)
        
        if pi.docstatus != 1:
            return {"success": False, "message": _("Hóa đơn chưa được duyệt. Vui lòng duyệt hóa đơn trước.")}
        
        if pi.update_stock:
            return {"success": False, "message": _("Hóa đơn này đã cập nhật tồn kho trực tiếp, không cần tạo phiếu nhập kho.")}
        
        # Check if already has stock entry (tìm trong remarks)
        existing = frappe.get_all("Stock Entry", 
            filters={"docstatus": ["!=", 2], "remarks": ["like", f"%{purchase_invoice}%"]},
            limit=1
        )
        if existing:
            return {"success": False, "message": _("Đã có phiếu nhập kho cho hóa đơn này: {0}").format(existing[0].name)}
        
        # Create Stock Entry
        doc = frappe.new_doc("Stock Entry")
        doc.purpose = "Material Receipt"
        doc.stock_entry_type = "Material Receipt"
        doc.company = pi.company
        # Lưu reference trong remarks vì Stock Entry không có field purchase_invoice
        doc.remarks = _("Nhập kho từ hóa đơn mua hàng: {0}").format(purchase_invoice)
        
        target_warehouse = warehouse or pi.set_warehouse
        
        for item in pi.items:
            row = doc.append("items", {})
            row.item_code = item.item_code
            row.qty = item.qty
            row.t_warehouse = item.warehouse or target_warehouse
            row.basic_rate = item.rate
        
        doc.insert()
        doc.submit()
        
        return {
            "success": True,
            "name": doc.name,
            "message": _("Đã tạo phiếu nhập kho {0}").format(doc.name)
        }
    except Exception as e:
        frappe.log_error(frappe.get_traceback(), "create_stock_entry_from_purchase_invoice Error")
        return {
            "success": False,
            "message": _parse_friendly_error(str(e))
        }


@frappe.whitelist()
def create_payment_for_purchase_invoice(purchase_invoice, amount=None, mode_of_payment=None, 
                                        reference_no=None, reference_date=None):
    """
    Tạo thanh toán cho hóa đơn mua hàng
    
    Args:
        purchase_invoice: Mã hóa đơn mua hàng
        amount: Số tiền thanh toán (nếu không truyền sẽ thanh toán toàn bộ)
        mode_of_payment: Hình thức thanh toán (Cash, Bank Transfer, etc.)
        reference_no: Số tham chiếu (số chứng từ ngân hàng, etc.)
        reference_date: Ngày tham chiếu
    
    Returns:
        dict: {success: bool, name: str, message: str}
    """
    try:
        if not frappe.db.exists("Purchase Invoice", purchase_invoice):
            return {"success": False, "message": _("Không tìm thấy hóa đơn mua hàng.")}
        
        pi = frappe.get_doc("Purchase Invoice", purchase_invoice)
        
        if pi.docstatus != 1:
            return {"success": False, "message": _("Hóa đơn chưa được duyệt. Vui lòng duyệt hóa đơn trước.")}
        
        if pi.outstanding_amount <= 0:
            return {"success": False, "message": _("Hóa đơn đã được thanh toán đầy đủ.")}
        
        # Determine payment amount
        payment_amount = float(amount) if amount else pi.outstanding_amount
        
        if payment_amount > pi.outstanding_amount:
            return {"success": False, "message": _("Số tiền thanh toán ({0}) vượt quá số tiền còn nợ ({1}).").format(
                payment_amount, pi.outstanding_amount
            )}
        
        if payment_amount <= 0:
            return {"success": False, "message": _("Số tiền thanh toán phải lớn hơn 0.")}
        
        # Get default accounts
        company = pi.company
        default_mode = mode_of_payment or "Cash"
        
        # Get payment account (Cash/Bank) from Mode of Payment
        mode_of_payment_doc = frappe.get_doc("Mode of Payment", default_mode) if frappe.db.exists("Mode of Payment", default_mode) else None
        
        paid_from_account = None
        if mode_of_payment_doc:
            for acc in mode_of_payment_doc.accounts:
                if acc.company == company:
                    paid_from_account = acc.default_account
                    break
        
        if not paid_from_account:
            # Fallback to default cash/bank account
            paid_from_account = frappe.db.get_value("Company", company, "default_cash_account") or \
                                frappe.db.get_value("Company", company, "default_bank_account")
        
        if not paid_from_account:
            return {"success": False, "message": _("Chưa thiết lập tài khoản tiền mặt/ngân hàng mặc định cho công ty hoặc hình thức thanh toán.")}
        
        # Create Payment Entry
        # For "Pay" type: paid_from = Cash/Bank (source), paid_to = Creditors (destination)
        pe = frappe.new_doc("Payment Entry")
        pe.payment_type = "Pay"
        pe.posting_date = frappe.utils.today()
        pe.company = company
        pe.mode_of_payment = default_mode
        pe.party_type = "Supplier"
        pe.party = pi.supplier
        pe.party_name = pi.supplier_name
        pe.paid_from = paid_from_account  # Cash/Bank account (source of money)
        pe.paid_to = pi.credit_to  # Creditors/Payable account from invoice
        pe.paid_amount = payment_amount
        pe.received_amount = payment_amount
        pe.source_exchange_rate = 1
        pe.target_exchange_rate = 1
        
        if reference_no:
            pe.reference_no = reference_no
        if reference_date:
            pe.reference_date = reference_date
        
        # Add reference to the invoice
        pe.append("references", {
            "reference_doctype": "Purchase Invoice",
            "reference_name": purchase_invoice,
            "total_amount": pi.grand_total,
            "outstanding_amount": pi.outstanding_amount,
            "allocated_amount": payment_amount
        })
        
        pe.insert()
        pe.submit()
        
        return {
            "success": True,
            "name": pe.name,
            "message": _("Đã tạo phiếu thanh toán {0}").format(pe.name)
        }
    except Exception as e:
        frappe.log_error(frappe.get_traceback(), "create_payment_for_purchase_invoice Error")
        return {
            "success": False,
            "message": _parse_friendly_error(str(e))
        }


@frappe.whitelist()
def get_mode_of_payments():
    """
    Lấy danh sách hình thức thanh toán
    
    Returns:
        list: Danh sách mode of payment
    """
    modes = frappe.get_all(
        "Mode of Payment",
        filters={"enabled": 1},
        fields=["name", "type"],
        order_by="name"
    )
    return {"success": True, "data": modes}


# ============================================
# SALES INVOICE APIs
# ============================================

@frappe.whitelist()
def get_sales_invoices(status=None, customer=None, from_date=None, to_date=None,
                       search=None, limit=20, page=1):
    """
    Lấy danh sách hóa đơn bán hàng
    
    Args:
        status: Lọc theo trạng thái (Draft, Unpaid, Paid, Overdue, Cancelled)
        customer: Lọc theo khách hàng
        from_date: Ngày bắt đầu
        to_date: Ngày kết thúc
        search: Tìm kiếm theo mã hóa đơn
        limit: Số bản ghi mỗi trang
        page: Số trang
    
    Returns:
        dict: {data: list, total: int, page: int, total_pages: int}
    """
    filters = {}
    
    # Lọc theo status
    if status:
        if status == "Draft":
            filters["docstatus"] = 0
        elif status == "Cancelled":
            filters["docstatus"] = 2
        elif status == "Unpaid":
            filters["docstatus"] = 1
            filters["outstanding_amount"] = [">", 0]
        elif status == "Paid":
            filters["docstatus"] = 1
            filters["outstanding_amount"] = 0
        elif status == "Overdue":
            filters["docstatus"] = 1
            filters["outstanding_amount"] = [">", 0]
            filters["due_date"] = ["<", frappe.utils.today()]
    
    if customer:
        filters["customer"] = customer
    
    if from_date:
        filters["posting_date"] = [">=", from_date]
    if to_date:
        if "posting_date" in filters:
            filters["posting_date"] = ["between", [from_date, to_date]]
        else:
            filters["posting_date"] = ["<=", to_date]
    
    if search:
        filters["name"] = ["like", f"%{search}%"]
    
    # Pagination
    limit = int(limit)
    page = int(page)
    offset = (page - 1) * limit
    
    # Count total
    total_count = frappe.db.count("Sales Invoice", filters=filters)
    
    invoices = frappe.get_all(
        "Sales Invoice",
        filters=filters,
        fields=[
            "name", "customer", "customer_name", "posting_date", "due_date",
            "grand_total", "outstanding_amount", "currency", "docstatus",
            "status", "creation", "owner"
        ],
        order_by="creation desc",
        limit_start=offset,
        limit_page_length=limit
    )
    
    # Enhance data
    for inv in invoices:
        # Lấy số lượng items
        inv["item_count"] = frappe.db.count("Sales Invoice Item", {"parent": inv.name})
        
        # Lấy tên người tạo
        inv["owner_name"] = frappe.db.get_value("User", inv.owner, "full_name") or inv.owner
        
        # Status display
        if inv.docstatus == 0:
            inv["status_display"] = "Chờ duyệt"
            inv["status_color"] = "warning"
        elif inv.docstatus == 2:
            inv["status_display"] = "Đã hủy"
            inv["status_color"] = "gray"
        elif inv.outstanding_amount == 0:
            inv["status_display"] = "Đã thanh toán"
            inv["status_color"] = "success"
        elif inv.due_date and str(inv.due_date) < frappe.utils.today():
            inv["status_display"] = "Quá hạn"
            inv["status_color"] = "error"
        else:
            inv["status_display"] = "Chưa thanh toán"
            inv["status_color"] = "info"
        
        # Kiểm tra đã tạo Stock Entry chưa
        inv["has_stock_entry"] = frappe.db.exists("Stock Entry", {
            "sales_invoice": inv.name,
            "docstatus": ["!=", 2]
        }) or False
    
    total_pages = (total_count + limit - 1) // limit if limit > 0 else 1
    
    return {
        "success": True,
        "data": invoices,
        "total": total_count,
        "page": page,
        "page_size": limit,
        "total_pages": total_pages
    }


@frappe.whitelist()
def get_sales_invoice_detail(name):
    """
    Lấy chi tiết hóa đơn bán hàng
    
    Args:
        name: Mã hóa đơn
    
    Returns:
        dict: Chi tiết hóa đơn
    """
    if not frappe.db.exists("Sales Invoice", name):
        return {"success": False, "message": _("Không tìm thấy hóa đơn {0}").format(name)}
    
    doc = frappe.get_doc("Sales Invoice", name)
    
    # Lấy thông tin items
    items = []
    for item in doc.items:
        # Lấy tồn kho hiện tại
        actual_qty = 0
        if item.warehouse:
            actual_qty = frappe.db.get_value("Bin", {
                "item_code": item.item_code,
                "warehouse": item.warehouse
            }, "actual_qty") or 0
        
        items.append({
            "item_code": item.item_code,
            "item_name": item.item_name,
            "qty": item.qty,
            "uom": item.uom,
            "rate": item.rate,
            "amount": item.amount,
            "warehouse": item.warehouse,
            "delivered_qty": item.delivered_qty or 0,
            "stock_qty": item.stock_qty or item.qty,
            "actual_qty": actual_qty
        })
    
    # Lấy tên người thực hiện
    owner_name = frappe.db.get_value("User", doc.owner, "full_name") or doc.owner
    
    # Lấy Stock Entries liên quan (dùng sales_invoice_no)
    stock_entries = frappe.get_all(
        "Stock Entry",
        filters={"sales_invoice_no": name, "docstatus": ["!=", 2]},
        fields=["name", "purpose", "posting_date", "docstatus", "creation"],
        order_by="creation desc"
    )
    
    # Status display
    if doc.docstatus == 0:
        status_display = "Chờ duyệt"
        status_color = "warning"
    elif doc.docstatus == 2:
        status_display = "Đã hủy"
        status_color = "gray"
    elif doc.outstanding_amount == 0:
        status_display = "Đã thanh toán"
        status_color = "success"
    elif doc.due_date and str(doc.due_date) < frappe.utils.today():
        status_display = "Quá hạn"
        status_color = "error"
    else:
        status_display = "Chưa thanh toán"
        status_color = "info"
    
    return {
        "success": True,
        "name": doc.name,
        "customer": doc.customer,
        "customer_name": doc.customer_name,
        "posting_date": str(doc.posting_date),
        "due_date": str(doc.due_date) if doc.due_date else None,
        "grand_total": doc.grand_total,
        "net_total": doc.net_total,
        "total_taxes_and_charges": doc.total_taxes_and_charges,
        "outstanding_amount": doc.outstanding_amount,
        "currency": doc.currency,
        "docstatus": doc.docstatus,
        "status": doc.status,
        "status_display": status_display,
        "status_color": status_color,
        "is_paid": doc.outstanding_amount == 0,
        "remarks": doc.remarks,
        "items": items,
        "stock_entries": stock_entries,
        "owner": doc.owner,
        "owner_name": owner_name,
        "creation": str(doc.creation),
        "modified": str(doc.modified),
        "set_warehouse": doc.set_warehouse,
        "update_stock": doc.update_stock
    }


@frappe.whitelist()
def create_sales_invoice(customer, items, posting_date=None, due_date=None,
                         set_warehouse=None, remarks=None, update_stock=0):
    """
    Tạo hóa đơn bán hàng mới (Draft)
    
    Args:
        customer: Mã khách hàng
        items: Danh sách sản phẩm (JSON array)
            [{"item_code": "SP-001", "qty": 10, "rate": 5000, "warehouse": "Kho Chính"}]
        posting_date: Ngày hóa đơn
        due_date: Ngày đến hạn thanh toán
        set_warehouse: Kho mặc định cho tất cả items
        remarks: Ghi chú
        update_stock: Cập nhật tồn kho trực tiếp (0 = không, 1 = có)
    
    Returns:
        dict: {success: bool, name: str, message: str}
    """
    import json
    
    try:
        # Validate customer
        if not frappe.db.exists("Customer", customer):
            return {"success": False, "message": _("Khách hàng không tồn tại.")}
        
        # Parse items
        if items and isinstance(items, str):
            items = json.loads(items)
        
        if not items or len(items) == 0:
            return {"success": False, "message": _("Vui lòng thêm ít nhất một sản phẩm.")}
        
        company = frappe.defaults.get_user_default("Company") or frappe.db.get_single_value("Global Defaults", "default_company")
        
        if not company:
            return {"success": False, "message": _("Chưa thiết lập công ty mặc định.")}
        
        # Tạo Sales Invoice
        doc = frappe.new_doc("Sales Invoice")
        doc.customer = customer
        doc.company = company
        doc.update_stock = int(update_stock)
        
        if posting_date:
            doc.posting_date = posting_date
        
        if due_date:
            doc.due_date = due_date
        
        if set_warehouse:
            doc.set_warehouse = set_warehouse
        
        if remarks:
            doc.remarks = remarks
        
        # Add items
        for item_data in items:
            row = doc.append("items", {})
            row.item_code = item_data.get("item_code")
            row.qty = float(item_data.get("qty", 0))
            row.rate = float(item_data.get("rate", 0))
            if item_data.get("warehouse"):
                row.warehouse = item_data.get("warehouse")
            elif set_warehouse:
                row.warehouse = set_warehouse
        
        doc.insert()
        
        return {
            "success": True,
            "name": doc.name,
            "message": _("Đã tạo hóa đơn bán hàng {0}").format(doc.name)
        }
    except Exception as e:
        frappe.log_error(frappe.get_traceback(), "create_sales_invoice Error")
        return {
            "success": False,
            "message": _parse_friendly_error(str(e))
        }


@frappe.whitelist()
def submit_sales_invoice(name):
    """
    Duyệt hóa đơn bán hàng
    
    Args:
        name: Mã hóa đơn
    
    Returns:
        dict: {success: bool, message: str}
    """
    try:
        if not frappe.db.exists("Sales Invoice", name):
            return {"success": False, "message": _("Không tìm thấy hóa đơn.")}
        
        doc = frappe.get_doc("Sales Invoice", name)
        
        if doc.docstatus == 1:
            return {"success": False, "message": _("Hóa đơn đã được duyệt trước đó.")}
        elif doc.docstatus == 2:
            return {"success": False, "message": _("Hóa đơn đã bị hủy, không thể duyệt.")}
        
        doc.submit()
        
        return {
            "success": True,
            "message": _("Đã duyệt hóa đơn bán hàng {0}").format(name)
        }
    except Exception as e:
        frappe.log_error(frappe.get_traceback(), "submit_sales_invoice Error")
        return {
            "success": False,
            "message": _parse_friendly_error(str(e))
        }


@frappe.whitelist()
def cancel_sales_invoice(name):
    """
    Hủy hóa đơn bán hàng
    
    Args:
        name: Mã hóa đơn
    
    Returns:
        dict: {success: bool, message: str}
    """
    try:
        if not frappe.db.exists("Sales Invoice", name):
            return {"success": False, "message": _("Không tìm thấy hóa đơn.")}
        
        doc = frappe.get_doc("Sales Invoice", name)
        
        if doc.docstatus == 0:
            # Draft - just delete
            doc.delete()
            return {
                "success": True,
                "message": _("Đã xóa hóa đơn bán hàng.")
            }
        elif doc.docstatus == 2:
            return {"success": False, "message": _("Hóa đơn đã bị hủy trước đó.")}
        
        # Check if has linked stock entries
        stock_entries = frappe.get_all("Stock Entry",
            filters={"sales_invoice": name, "docstatus": 1},
            limit=1
        )
        if stock_entries:
            return {
                "success": False,
                "message": _("Không thể hủy vì đã có phiếu xuất kho liên kết. Vui lòng hủy phiếu xuất kho trước.")
            }
        
        doc.cancel()
        
        return {
            "success": True,
            "message": _("Đã hủy hóa đơn bán hàng {0}").format(name)
        }
    except Exception as e:
        frappe.log_error(frappe.get_traceback(), "cancel_sales_invoice Error")
        return {
            "success": False,
            "message": _parse_friendly_error(str(e))
        }


@frappe.whitelist()
def create_stock_entry_from_sales_invoice(sales_invoice, warehouse=None):
    """
    Tạo phiếu xuất kho từ hóa đơn bán hàng
    
    Args:
        sales_invoice: Mã hóa đơn bán hàng
        warehouse: Kho xuất (nếu không truyền sẽ lấy từ Invoice)
    
    Returns:
        dict: {success: bool, name: str, message: str}
    """
    try:
        if not frappe.db.exists("Sales Invoice", sales_invoice):
            return {"success": False, "message": _("Không tìm thấy hóa đơn bán hàng.")}
        
        si = frappe.get_doc("Sales Invoice", sales_invoice)
        
        if si.docstatus != 1:
            return {"success": False, "message": _("Hóa đơn chưa được duyệt. Vui lòng duyệt hóa đơn trước.")}
        
        if si.update_stock:
            return {"success": False, "message": _("Hóa đơn này đã cập nhật tồn kho trực tiếp, không cần tạo phiếu xuất kho.")}
        
        # Check if already has stock entry (dùng sales_invoice_no)
        existing = frappe.get_all("Stock Entry",
            filters={"sales_invoice_no": sales_invoice, "docstatus": ["!=", 2]},
            limit=1
        )
        if existing:
            return {"success": False, "message": _("Đã có phiếu xuất kho cho hóa đơn này: {0}").format(existing[0].name)}
        
        # Check stock availability
        source_warehouse = warehouse or si.set_warehouse
        insufficient_items = []
        
        for item in si.items:
            item_warehouse = item.warehouse or source_warehouse
            actual_qty = frappe.db.get_value("Bin", {
                "item_code": item.item_code,
                "warehouse": item_warehouse
            }, "actual_qty") or 0
            
            if actual_qty < item.qty:
                item_name = frappe.db.get_value("Item", item.item_code, "item_name") or item.item_code
                insufficient_items.append({
                    "item_code": item.item_code,
                    "item_name": item_name,
                    "required": item.qty,
                    "available": actual_qty,
                    "warehouse": item_warehouse
                })
        
        if insufficient_items:
            error_lines = [_("Không đủ tồn kho để xuất:")]
            for item in insufficient_items:
                error_lines.append(
                    f"• {item['item_name']}: Cần {item['required']}, Có {item['available']} tại {item['warehouse']}"
                )
            return {
                "success": False,
                "message": "\n".join(error_lines),
                "insufficient_items": insufficient_items
            }
        
        # Create Stock Entry
        doc = frappe.new_doc("Stock Entry")
        doc.purpose = "Material Issue"
        doc.stock_entry_type = "Material Issue"
        doc.company = si.company
        doc.sales_invoice_no = sales_invoice  # Đúng field name trong Stock Entry
        doc.remarks = _("Xuất kho từ hóa đơn bán hàng: {0}").format(sales_invoice)
        
        for item in si.items:
            row = doc.append("items", {})
            row.item_code = item.item_code
            row.qty = item.qty
            row.s_warehouse = item.warehouse or source_warehouse
        
        doc.insert()
        doc.submit()
        
        return {
            "success": True,
            "name": doc.name,
            "message": _("Đã tạo phiếu xuất kho {0}").format(doc.name)
        }
    except Exception as e:
        frappe.log_error(frappe.get_traceback(), "create_stock_entry_from_sales_invoice Error")
        return {
            "success": False,
            "message": _parse_friendly_error(str(e))
        }


@frappe.whitelist()
def create_payment_for_sales_invoice(sales_invoice, amount=None, mode_of_payment=None,
                                     reference_no=None, reference_date=None):
    """
    Tạo thanh toán (thu tiền) cho hóa đơn bán hàng
    
    Args:
        sales_invoice: Mã hóa đơn bán hàng
        amount: Số tiền thanh toán (nếu không truyền sẽ thanh toán toàn bộ)
        mode_of_payment: Hình thức thanh toán (Cash, Bank Transfer, etc.)
        reference_no: Số tham chiếu (số chứng từ ngân hàng, etc.)
        reference_date: Ngày tham chiếu
    
    Returns:
        dict: {success: bool, name: str, message: str}
    """
    try:
        if not frappe.db.exists("Sales Invoice", sales_invoice):
            return {"success": False, "message": _("Không tìm thấy hóa đơn bán hàng.")}
        
        si = frappe.get_doc("Sales Invoice", sales_invoice)
        
        if si.docstatus != 1:
            return {"success": False, "message": _("Hóa đơn chưa được duyệt. Vui lòng duyệt hóa đơn trước.")}
        
        if si.outstanding_amount <= 0:
            return {"success": False, "message": _("Hóa đơn đã được thanh toán đầy đủ.")}
        
        # Determine payment amount
        payment_amount = float(amount) if amount else si.outstanding_amount
        
        if payment_amount > si.outstanding_amount:
            return {"success": False, "message": _("Số tiền thanh toán ({0}) vượt quá số tiền còn nợ ({1}).").format(
                payment_amount, si.outstanding_amount
            )}
        
        if payment_amount <= 0:
            return {"success": False, "message": _("Số tiền thanh toán phải lớn hơn 0.")}
        
        # Get default accounts
        company = si.company
        default_mode = mode_of_payment or "Cash"
        
        # Get payment account (Cash/Bank) from Mode of Payment
        mode_of_payment_doc = frappe.get_doc("Mode of Payment", default_mode) if frappe.db.exists("Mode of Payment", default_mode) else None
        
        paid_to_account = None
        if mode_of_payment_doc:
            for acc in mode_of_payment_doc.accounts:
                if acc.company == company:
                    paid_to_account = acc.default_account
                    break
        
        if not paid_to_account:
            # Fallback to default cash/bank account
            paid_to_account = frappe.db.get_value("Company", company, "default_cash_account") or \
                              frappe.db.get_value("Company", company, "default_bank_account")
        
        if not paid_to_account:
            return {"success": False, "message": _("Chưa thiết lập tài khoản tiền mặt/ngân hàng mặc định cho công ty hoặc hình thức thanh toán.")}
        
        # Create Payment Entry
        # For "Receive" type: paid_from = Receivables (source), paid_to = Cash/Bank (destination)
        pe = frappe.new_doc("Payment Entry")
        pe.payment_type = "Receive"
        pe.posting_date = frappe.utils.today()
        pe.company = company
        pe.mode_of_payment = default_mode
        pe.party_type = "Customer"
        pe.party = si.customer
        pe.party_name = si.customer_name
        pe.paid_from = si.debit_to  # Receivables/Debtors account from invoice
        pe.paid_to = paid_to_account  # Cash/Bank account (destination of money)
        pe.paid_amount = payment_amount
        pe.received_amount = payment_amount
        pe.source_exchange_rate = 1
        pe.target_exchange_rate = 1
        
        if reference_no:
            pe.reference_no = reference_no
        if reference_date:
            pe.reference_date = reference_date
        
        # Add reference to the invoice
        pe.append("references", {
            "reference_doctype": "Sales Invoice",
            "reference_name": sales_invoice,
            "total_amount": si.grand_total,
            "outstanding_amount": si.outstanding_amount,
            "allocated_amount": payment_amount
        })
        
        pe.insert()
        pe.submit()
        
        return {
            "success": True,
            "name": pe.name,
            "message": _("Đã tạo phiếu thu tiền {0}").format(pe.name)
        }
    except Exception as e:
        frappe.log_error(frappe.get_traceback(), "create_payment_for_sales_invoice Error")
        return {
            "success": False,
            "message": _parse_friendly_error(str(e))
        }


# ============================================
# BOM MANAGEMENT APIs
# ============================================

@frappe.whitelist()
def get_bom_list(search=None, item=None, is_active=None, is_default=None, page=1, page_size=20):
    """
    Lấy danh sách BOM với phân trang và tìm kiếm
    
    Args:
        search: Tìm kiếm theo tên BOM, item code, item name
        item: Lọc theo item code
        is_active: Lọc BOM đang hoạt động (1/0)
        is_default: Lọc BOM mặc định (1/0)
        page: Trang hiện tại
        page_size: Số items/trang
    
    Returns:
        dict: {success, data, total, page, page_size}
    """
    try:
        filters = {"docstatus": 1}  # Chỉ lấy BOM đã submit
        
        if is_active is not None and is_active != "":
            filters["is_active"] = int(is_active)
        
        if is_default is not None and is_default != "":
            filters["is_default"] = int(is_default)
        
        if item:
            filters["item"] = item
        
        # Search
        or_filters = None
        if search:
            or_filters = [
                ["name", "like", f"%{search}%"],
                ["item", "like", f"%{search}%"],
                ["item_name", "like", f"%{search}%"]
            ]
        
        # Get total count - dùng get_all vì db.count không hỗ trợ or_filters
        if or_filters:
            total = len(frappe.get_all("BOM", filters=filters, or_filters=or_filters, pluck="name"))
        else:
            total = frappe.db.count("BOM", filters=filters)
        
        # Pagination
        page = int(page)
        page_size = int(page_size)
        offset = (page - 1) * page_size
        
        boms = frappe.get_all(
            "BOM",
            filters=filters,
            or_filters=or_filters,
            fields=[
                "name", "item", "item_name", "quantity", "uom",
                "is_active", "is_default", "total_cost",
                "company", "currency", "creation", "modified"
            ],
            order_by="is_default desc, modified desc",
            start=offset,
            page_length=page_size
        )
        
        # Thêm thông tin bổ sung
        for bom in boms:
            # Đếm số nguyên liệu
            bom["item_count"] = frappe.db.count("BOM Item", {"parent": bom.name})
            # Format dates
            bom["creation_formatted"] = frappe.utils.format_date(bom.creation, "dd/MM/yyyy")
            bom["modified_formatted"] = frappe.utils.format_date(bom.modified, "dd/MM/yyyy")
        
        return {
            "success": True,
            "data": boms,
            "total": total,
            "page": page,
            "page_size": page_size,
            "total_pages": (total + page_size - 1) // page_size
        }
    except Exception as e:
        frappe.log_error(frappe.get_traceback(), "get_bom_list Error")
        return {"success": False, "message": str(e)}


@frappe.whitelist()
def create_bom(item, items, quantity=1, is_active=1, is_default=0, remarks=None):
    """
    Tạo BOM mới
    
    Args:
        item: Mã sản phẩm (thành phẩm)
        items: Danh sách nguyên liệu JSON [{item_code, qty, uom, rate}]
        quantity: Số lượng thành phẩm (mặc định = 1)
        is_active: Kích hoạt (1/0)
        is_default: Đặt làm mặc định (1/0)
        remarks: Ghi chú
    
    Returns:
        dict: {success, name, message}
    """
    import json
    
    try:
        # Parse items
        if isinstance(items, str):
            items = json.loads(items)
        
        if not items or len(items) == 0:
            return {"success": False, "message": _("Vui lòng thêm ít nhất 1 nguyên liệu")}
        
        company = frappe.defaults.get_user_default("Company") or "Xuân Hòa Thái Bình"
        
        doc = frappe.new_doc("BOM")
        doc.item = item
        doc.company = company
        doc.quantity = float(quantity)
        doc.is_active = int(is_active)
        doc.is_default = int(is_default)
        
        if remarks:
            doc.remarks = remarks
        
        for bom_item in items:
            row = doc.append("items", {})
            row.item_code = bom_item.get("item_code")
            row.qty = float(bom_item.get("qty", 1))
            if bom_item.get("uom"):
                row.uom = bom_item.get("uom")
            if bom_item.get("rate"):
                row.rate = float(bom_item.get("rate"))
        
        doc.insert()
        doc.submit()
        
        # Update cost after submit to calculate raw_material_cost
        doc.update_cost(update_parent=True, from_child_bom=False, save=True)
        
        return {
            "success": True,
            "name": doc.name,
            "message": _("Đã tạo BOM {0}").format(doc.name)
        }
    except Exception as e:
        frappe.log_error(frappe.get_traceback(), "create_bom Error")
        return {"success": False, "message": _parse_friendly_error(str(e))}


@frappe.whitelist()
def toggle_bom_active(bom_no):
    """
    Bật/tắt trạng thái active của BOM
    
    Args:
        bom_no: Mã BOM
    
    Returns:
        dict: {success, is_active, message}
    """
    try:
        doc = frappe.get_doc("BOM", bom_no)
        doc.is_active = 0 if doc.is_active else 1
        doc.save()
        
        status = "kích hoạt" if doc.is_active else "vô hiệu hóa"
        return {
            "success": True,
            "is_active": doc.is_active,
            "message": _("Đã {0} BOM {1}").format(status, bom_no)
        }
    except Exception as e:
        frappe.log_error(frappe.get_traceback(), "toggle_bom_active Error")
        return {"success": False, "message": str(e)}


@frappe.whitelist()
def set_default_bom(bom_no):
    """
    Đặt BOM làm mặc định cho sản phẩm
    
    Args:
        bom_no: Mã BOM
    
    Returns:
        dict: {success, message}
    """
    try:
        doc = frappe.get_doc("BOM", bom_no)
        
        # Bỏ default của các BOM khác cùng item
        frappe.db.sql("""
            UPDATE `tabBOM` SET is_default = 0 
            WHERE item = %s AND name != %s AND docstatus = 1
        """, (doc.item, bom_no))
        
        doc.is_default = 1
        doc.save()
        
        return {
            "success": True,
            "message": _("Đã đặt {0} làm BOM mặc định cho {1}").format(bom_no, doc.item)
        }
    except Exception as e:
        frappe.log_error(frappe.get_traceback(), "set_default_bom Error")
        return {"success": False, "message": str(e)}


# ============================================
# WAREHOUSE & STOCK MANAGEMENT APIs
# ============================================

@frappe.whitelist()
def get_warehouse_list(search=None, is_group=None, company=None):
    """
    Lấy danh sách kho với thông tin tồn kho
    
    Args:
        search: Tìm kiếm theo tên kho
        is_group: Lọc theo loại (0=kho thực, 1=kho nhóm)
        company: Lọc theo công ty
    
    Returns:
        dict: {success, data}
    """
    try:
        filters = {"disabled": 0}
        
        if is_group is not None and is_group != "":
            filters["is_group"] = int(is_group)
        
        if company:
            filters["company"] = company
        else:
            default_company = frappe.defaults.get_user_default("Company")
            if default_company:
                filters["company"] = default_company
        
        or_filters = None
        if search:
            or_filters = [
                ["name", "like", f"%{search}%"],
                ["warehouse_name", "like", f"%{search}%"]
            ]
        
        warehouses = frappe.get_all(
            "Warehouse",
            filters=filters,
            or_filters=or_filters,
            fields=["name", "warehouse_name", "parent_warehouse", "is_group", "warehouse_type", "company"],
            order_by="warehouse_name"
        )
        
        # Thêm thống kê tồn kho cho mỗi kho
        for wh in warehouses:
            if not wh.is_group:
                # Đếm số item có tồn kho
                stock_stats = frappe.db.sql("""
                    SELECT 
                        COUNT(DISTINCT item_code) as item_count,
                        SUM(actual_qty) as total_qty,
                        SUM(stock_value) as total_value
                    FROM `tabBin`
                    WHERE warehouse = %s AND actual_qty > 0
                """, wh.name, as_dict=True)[0]
                
                wh["item_count"] = stock_stats.get("item_count") or 0
                wh["total_qty"] = stock_stats.get("total_qty") or 0
                wh["total_value"] = stock_stats.get("total_value") or 0
            else:
                wh["item_count"] = 0
                wh["total_qty"] = 0
                wh["total_value"] = 0
        
        return {"success": True, "data": warehouses}
    except Exception as e:
        frappe.log_error(frappe.get_traceback(), "get_warehouse_list Error")
        return {"success": False, "message": str(e)}


@frappe.whitelist()
def get_stock_by_warehouse(search=None, item_group=None):
    """
    Lấy tồn kho nhóm theo kho (cho chế độ "Theo kho")
    
    Returns:
        list: [{warehouse, warehouse_name, total_qty, total_value, items: [...]}, ...]
    """
    try:
        company = frappe.defaults.get_user_default("Company") or "Xuân Hòa Thái Bình"
        
        # Get all warehouses with stock
        warehouses = frappe.db.sql("""
            SELECT DISTINCT 
                b.warehouse,
                w.warehouse_name
            FROM `tabBin` b
            LEFT JOIN `tabWarehouse` w ON b.warehouse = w.name
            WHERE b.actual_qty != 0 AND w.company = %s AND w.is_group = 0
            ORDER BY w.warehouse_name
        """, company, as_dict=True)
        
        result = []
        total_summary = {"totalItems": 0, "totalQty": 0, "totalValue": 0}
        
        for wh in warehouses:
            # Build item conditions
            item_conditions = "b.warehouse = %s AND b.actual_qty != 0"
            params = [wh.warehouse]
            
            if search:
                item_conditions += " AND (b.item_code LIKE %s OR i.item_name LIKE %s)"
                params.extend([f"%{search}%", f"%{search}%"])
            
            if item_group:
                item_conditions += " AND i.item_group = %s"
                params.append(item_group)
            
            # Get items in this warehouse
            items = frappe.db.sql(f"""
                SELECT 
                    b.item_code,
                    i.item_name,
                    i.item_group,
                    i.stock_uom,
                    b.actual_qty,
                    b.valuation_rate,
                    b.stock_value
                FROM `tabBin` b
                LEFT JOIN `tabItem` i ON b.item_code = i.name
                WHERE {item_conditions}
                ORDER BY i.item_name
            """, params, as_dict=True)
            
            if items:  # Only include warehouses with items (after filter)
                total_qty = sum(item.actual_qty or 0 for item in items)
                total_value = sum(item.stock_value or 0 for item in items)
                
                result.append({
                    "warehouse": wh.warehouse,
                    "warehouse_name": wh.warehouse_name,
                    "total_qty": total_qty,
                    "total_value": total_value,
                    "items": items
                })
                
                total_summary["totalItems"] += len(items)
                total_summary["totalQty"] += total_qty
                total_summary["totalValue"] += total_value
        
        return {
            "data": result,
            "summary": total_summary
        }
    except Exception as e:
        frappe.log_error(frappe.get_traceback(), "get_stock_by_warehouse Error")
        return {"data": [], "summary": {"totalItems": 0, "totalQty": 0, "totalValue": 0}}


@frappe.whitelist()
def get_warehouse_stock(warehouse, search=None, page=1, page_size=20):
    """
    Lấy danh sách hàng hóa trong kho
    
    Args:
        warehouse: Tên kho
        search: Tìm kiếm theo item code hoặc tên
        page: Trang
        page_size: Số items/trang
    
    Returns:
        dict: {success, data, total, warehouse_info}
    """
    try:
        page = int(page)
        page_size = int(page_size)
        offset = (page - 1) * page_size
        
        # Build query
        conditions = "b.warehouse = %s AND b.actual_qty != 0"
        params = [warehouse]
        
        if search:
            conditions += " AND (b.item_code LIKE %s OR i.item_name LIKE %s)"
            params.extend([f"%{search}%", f"%{search}%"])
        
        # Get total
        total = frappe.db.sql(f"""
            SELECT COUNT(*) 
            FROM `tabBin` b
            LEFT JOIN `tabItem` i ON b.item_code = i.name
            WHERE {conditions}
        """, params)[0][0]
        
        # Get data
        stocks = frappe.db.sql(f"""
            SELECT 
                b.item_code,
                i.item_name,
                i.item_group,
                i.stock_uom as uom,
                b.actual_qty,
                b.reserved_qty,
                b.ordered_qty,
                b.projected_qty,
                b.valuation_rate,
                b.stock_value
            FROM `tabBin` b
            LEFT JOIN `tabItem` i ON b.item_code = i.name
            WHERE {conditions}
            ORDER BY b.item_code
            LIMIT %s OFFSET %s
        """, params + [page_size, offset], as_dict=True)
        
        # Warehouse info
        wh_info = frappe.db.get_value("Warehouse", warehouse, 
            ["name", "warehouse_name", "company"], as_dict=True)
        
        return {
            "success": True,
            "data": stocks,
            "total": total,
            "page": page,
            "page_size": page_size,
            "total_pages": (total + page_size - 1) // page_size,
            "warehouse_info": wh_info
        }
    except Exception as e:
        frappe.log_error(frappe.get_traceback(), "get_warehouse_stock Error")
        return {"success": False, "message": str(e)}


@frappe.whitelist()
def get_item_stock_across_warehouses(item_code):
    """
    Lấy tồn kho của 1 item trên tất cả các kho
    
    Args:
        item_code: Mã sản phẩm
    
    Returns:
        dict: {success, data, item_info}
    """
    try:
        # Get item info
        item_info = frappe.db.get_value("Item", item_code, 
            ["item_code", "item_name", "item_group", "stock_uom", "valuation_method"], as_dict=True)
        
        if not item_info:
            return {"success": False, "message": _("Không tìm thấy sản phẩm {0}").format(item_code)}
        
        # Get stock in all warehouses
        stocks = frappe.db.sql("""
            SELECT 
                b.warehouse,
                w.warehouse_name,
                b.actual_qty,
                b.reserved_qty,
                b.ordered_qty,
                b.projected_qty,
                b.valuation_rate,
                b.stock_value
            FROM `tabBin` b
            LEFT JOIN `tabWarehouse` w ON b.warehouse = w.name
            WHERE b.item_code = %s AND b.actual_qty != 0
            ORDER BY b.actual_qty DESC
        """, item_code, as_dict=True)
        
        # Total
        total_qty = sum(s.actual_qty for s in stocks)
        total_value = sum(s.stock_value or 0 for s in stocks)
        
        return {
            "success": True,
            "data": stocks,
            "item_info": item_info,
            "total_qty": total_qty,
            "total_value": total_value
        }
    except Exception as e:
        frappe.log_error(frappe.get_traceback(), "get_item_stock_across_warehouses Error")
        return {"success": False, "message": str(e)}


@frappe.whitelist()
def get_stock_summary(warehouse=None):
    """
    Lấy tổng quan tồn kho
    
    Args:
        warehouse: Lọc theo kho (tùy chọn)
    
    Returns:
        dict: {success, summary, by_item_group, low_stock_items}
    """
    try:
        company = frappe.defaults.get_user_default("Company") or "Xuân Hòa Thái Bình"
        
        # Filter conditions
        wh_condition = ""
        params = []
        if warehouse:
            wh_condition = "AND b.warehouse = %s"
            params.append(warehouse)
        else:
            wh_condition = "AND w.company = %s"
            params.append(company)
        
        # Summary stats
        summary = frappe.db.sql(f"""
            SELECT 
                COUNT(DISTINCT b.item_code) as total_items,
                COUNT(DISTINCT b.warehouse) as total_warehouses,
                SUM(b.actual_qty) as total_qty,
                SUM(b.stock_value) as total_value
            FROM `tabBin` b
            LEFT JOIN `tabWarehouse` w ON b.warehouse = w.name
            WHERE b.actual_qty > 0 {wh_condition}
        """, params, as_dict=True)[0]
        
        # By item group
        by_group = frappe.db.sql(f"""
            SELECT 
                i.item_group,
                COUNT(DISTINCT b.item_code) as item_count,
                SUM(b.actual_qty) as qty,
                SUM(b.stock_value) as value
            FROM `tabBin` b
            LEFT JOIN `tabItem` i ON b.item_code = i.name
            LEFT JOIN `tabWarehouse` w ON b.warehouse = w.name
            WHERE b.actual_qty > 0 {wh_condition}
            GROUP BY i.item_group
            ORDER BY value DESC
        """, params, as_dict=True)
        
        # Low stock items (qty < 10)
        low_stock = frappe.db.sql(f"""
            SELECT 
                b.item_code,
                i.item_name,
                b.warehouse,
                b.actual_qty,
                i.stock_uom as uom
            FROM `tabBin` b
            LEFT JOIN `tabItem` i ON b.item_code = i.name
            LEFT JOIN `tabWarehouse` w ON b.warehouse = w.name
            WHERE b.actual_qty > 0 AND b.actual_qty < 10 {wh_condition}
            ORDER BY b.actual_qty
            LIMIT 10
        """, params, as_dict=True)
        
        return {
            "success": True,
            "summary": summary,
            "by_item_group": by_group,
            "low_stock_items": low_stock
        }
    except Exception as e:
        frappe.log_error(frappe.get_traceback(), "get_stock_summary Error")
        return {"success": False, "message": str(e)}


# ============================================
# ADDITIONAL BOM & STOCK APIs
# ============================================

@frappe.whitelist()
def get_all_boms(item=None, is_active=None, is_default=None, search=None, page=1, page_size=20):
    """
    Lấy danh sách tất cả BOM với filter và phân trang
    
    Args:
        item: Lọc theo sản phẩm
        is_active: Lọc theo trạng thái (0/1)
        is_default: Lọc theo mặc định (0/1)
        search: Tìm kiếm theo tên BOM hoặc tên sản phẩm
        page: Trang
        page_size: Số items/trang
    
    Returns:
        dict: {data, total, page, page_size, total_pages}
    """
    try:
        page = int(page)
        page_size = int(page_size)
        offset = (page - 1) * page_size
        
        # Build filters
        conditions = ["b.docstatus = 1"]
        params = []
        
        if item:
            conditions.append("b.item = %s")
            params.append(item)
        
        if is_active is not None and is_active != "":
            conditions.append("b.is_active = %s")
            params.append(int(is_active))
        
        if is_default is not None and is_default != "":
            conditions.append("b.is_default = %s")
            params.append(int(is_default))
        
        if search:
            conditions.append("(b.name LIKE %s OR b.item LIKE %s OR i.item_name LIKE %s)")
            params.extend([f"%{search}%", f"%{search}%", f"%{search}%"])
        
        where_clause = " AND ".join(conditions)
        
        # Get total count
        total = frappe.db.sql(f"""
            SELECT COUNT(*)
            FROM `tabBOM` b
            LEFT JOIN `tabItem` i ON b.item = i.name
            WHERE {where_clause}
        """, params)[0][0]
        
        # Get data
        boms = frappe.db.sql(f"""
            SELECT 
                b.name,
                b.item,
                i.item_name,
                b.quantity,
                b.uom,
                b.is_active,
                b.is_default,
                b.raw_material_cost,
                b.total_cost,
                b.creation,
                (SELECT COUNT(*) FROM `tabBOM Item` bi WHERE bi.parent = b.name) as item_count
            FROM `tabBOM` b
            LEFT JOIN `tabItem` i ON b.item = i.name
            WHERE {where_clause}
            ORDER BY b.creation DESC
            LIMIT %s OFFSET %s
        """, params + [page_size, offset], as_dict=True)
        
        return {
            "data": boms,
            "total": total,
            "page": page,
            "page_size": page_size,
            "total_pages": (total + page_size - 1) // page_size if total > 0 else 1
        }
    except Exception as e:
        frappe.log_error(frappe.get_traceback(), "get_all_boms Error")
        return {"data": [], "total": 0, "page": 1, "page_size": page_size, "total_pages": 1}


@frappe.whitelist()
def update_bom(bom_name, is_active=None, is_default=None, quantity=None, items=None):
    """
    Cập nhật BOM
    - Nếu chỉ thay đổi is_active/is_default: update trực tiếp
    - Nếu thay đổi items/quantity: Cancel BOM cũ, tạo BOM mới (amendment)
    
    Args:
        bom_name: Mã BOM
        is_active: Trạng thái hoạt động (0/1)
        is_default: Mặc định (0/1)
        quantity: Số lượng sản phẩm
        items: Danh sách NVL mới (JSON string hoặc list)
    
    Returns:
        dict: {success, message, name}
    """
    import json
    
    try:
        old_doc = frappe.get_doc("BOM", bom_name)
        
        # Parse items nếu có
        if items:
            if isinstance(items, str):
                items = json.loads(items)
        
        # Nếu có thay đổi items hoặc quantity -> tạo BOM mới (amendment)
        if items is not None and len(items) > 0:
            # Cancel BOM cũ
            if old_doc.docstatus == 1:
                old_doc.cancel()
            
            # Tạo BOM mới (amended from)
            company = frappe.defaults.get_user_default("Company") or "Xuân Hòa Thái Bình"
            new_doc = frappe.new_doc("BOM")
            new_doc.item = old_doc.item
            new_doc.company = company
            new_doc.quantity = float(quantity) if quantity else old_doc.quantity
            new_doc.is_active = int(is_active) if is_active is not None else old_doc.is_active
            new_doc.is_default = int(is_default) if is_default is not None else old_doc.is_default
            new_doc.amended_from = bom_name
            
            for bom_item in items:
                row = new_doc.append("items", {})
                row.item_code = bom_item.get("item_code")
                row.qty = float(bom_item.get("qty", 1))
                if bom_item.get("uom"):
                    row.uom = bom_item.get("uom")
            
            new_doc.insert()
            new_doc.submit()
            
            # Update cost
            new_doc.update_cost(update_parent=True, from_child_bom=False, save=True)
            
            # Nếu is_default, bỏ default các BOM khác
            if new_doc.is_default:
                frappe.db.sql("""
                    UPDATE `tabBOM` SET is_default = 0 
                    WHERE item = %s AND name != %s AND docstatus = 1
                """, (new_doc.item, new_doc.name))
            
            return {
                "success": True,
                "name": new_doc.name,
                "message": _("Đã cập nhật BOM {0} thành {1}").format(bom_name, new_doc.name)
            }
        else:
            # Chỉ update trạng thái
            if is_active is not None:
                old_doc.is_active = int(is_active)
            
            if is_default is not None and int(is_default) == 1:
                # Bỏ default của các BOM khác cùng item
                frappe.db.sql("""
                    UPDATE `tabBOM` SET is_default = 0 
                    WHERE item = %s AND name != %s AND docstatus = 1
                """, (old_doc.item, bom_name))
                old_doc.is_default = 1
            elif is_default is not None:
                old_doc.is_default = 0
            
            old_doc.save()
            
            return {
                "success": True,
                "name": bom_name,
                "message": _("Đã cập nhật BOM {0}").format(bom_name)
            }
    except Exception as e:
        frappe.log_error(frappe.get_traceback(), "update_bom Error")
        return {"success": False, "message": str(e)}


@frappe.whitelist()
def delete_bom(bom_name):
    """
    Xóa BOM (cancel + delete)
    
    Args:
        bom_name: Mã BOM
    
    Returns:
        dict: {success, message}
    """
    try:
        doc = frappe.get_doc("BOM", bom_name)
        
        # Check if BOM is used in Work Orders
        work_orders = frappe.get_all("Work Order", filters={"bom_no": bom_name, "docstatus": ["!=", 2]})
        if work_orders:
            return {
                "success": False,
                "message": _("Không thể xóa BOM {0} vì đang được sử dụng trong {1} lệnh sản xuất").format(
                    bom_name, len(work_orders)
                )
            }
        
        # Cancel if submitted
        if doc.docstatus == 1:
            doc.cancel()
        
        # Delete
        frappe.delete_doc("BOM", bom_name, force=1)
        
        return {
            "success": True,
            "message": _("Đã xóa BOM {0}").format(bom_name)
        }
    except Exception as e:
        frappe.log_error(frappe.get_traceback(), "delete_bom Error")
        return {"success": False, "message": str(e)}


@frappe.whitelist()
def get_all_stock(warehouse=None, item_code=None, item_group=None, search=None, page=1, page_size=50):
    """
    Lấy toàn bộ tồn kho theo sản phẩm (flat list)
    
    Args:
        warehouse: Lọc theo kho
        item_code: Lọc theo mã SP
        item_group: Lọc theo nhóm hàng
        search: Tìm kiếm theo mã/tên SP
        page: Trang
        page_size: Số items/trang
    
    Returns:
        list: Danh sách tồn kho theo sản phẩm
    """
    try:
        page = int(page)
        page_size = int(page_size)
        offset = (page - 1) * page_size
        
        # Build conditions
        conditions = ["b.actual_qty != 0"]
        params = []
        
        if warehouse:
            conditions.append("b.warehouse = %s")
            params.append(warehouse)
        
        if item_code:
            conditions.append("b.item_code = %s")
            params.append(item_code)
        
        if item_group:
            conditions.append("i.item_group = %s")
            params.append(item_group)
        
        if search:
            conditions.append("(b.item_code LIKE %s OR i.item_name LIKE %s)")
            params.extend([f"%{search}%", f"%{search}%"])
        
        where_clause = " AND ".join(conditions)
        
        # Get total
        total = frappe.db.sql(f"""
            SELECT COUNT(*)
            FROM `tabBin` b
            LEFT JOIN `tabItem` i ON b.item_code = i.name
            WHERE {where_clause}
        """, params)[0][0]
        
        # Get data
        stocks = frappe.db.sql(f"""
            SELECT 
                b.item_code,
                i.item_name,
                i.item_group,
                i.stock_uom,
                b.warehouse,
                w.warehouse_name,
                b.actual_qty,
                b.reserved_qty,
                b.ordered_qty,
                b.projected_qty,
                b.valuation_rate,
                b.stock_value
            FROM `tabBin` b
            LEFT JOIN `tabItem` i ON b.item_code = i.name
            LEFT JOIN `tabWarehouse` w ON b.warehouse = w.name
            WHERE {where_clause}
            ORDER BY i.item_name, b.warehouse
            LIMIT %s OFFSET %s
        """, params + [page_size, offset], as_dict=True)
        
        return {
            "data": stocks,
            "total": total,
            "page": page,
            "page_size": page_size,
            "total_pages": (total + page_size - 1) // page_size if total > 0 else 1
        }
    except Exception as e:
        frappe.log_error(frappe.get_traceback(), "get_all_stock Error")
        return []


@frappe.whitelist()
def get_stock_ledger(warehouse=None, item_code=None, from_date=None, to_date=None, page=1, page_size=50):
    """
    Lấy lịch sử xuất nhập kho (Stock Ledger Entry)
    
    Args:
        warehouse: Lọc theo kho
        item_code: Lọc theo mã SP
        from_date: Từ ngày
        to_date: Đến ngày
        page: Trang
        page_size: Số items/trang
    
    Returns:
        list: Danh sách giao dịch kho
    """
    try:
        page = int(page)
        page_size = int(page_size)
        offset = (page - 1) * page_size
        
        # Build conditions
        conditions = ["1=1"]
        params = []
        
        if warehouse:
            conditions.append("sle.warehouse = %s")
            params.append(warehouse)
        
        if item_code:
            conditions.append("sle.item_code = %s")
            params.append(item_code)
        
        if from_date:
            conditions.append("sle.posting_date >= %s")
            params.append(from_date)
        
        if to_date:
            conditions.append("sle.posting_date <= %s")
            params.append(to_date)
        
        where_clause = " AND ".join(conditions)
        
        # Get total
        total = frappe.db.sql(f"""
            SELECT COUNT(*)
            FROM `tabStock Ledger Entry` sle
            WHERE {where_clause}
        """, params)[0][0]
        
        # Get data
        entries = frappe.db.sql(f"""
            SELECT 
                sle.name,
                sle.posting_date,
                sle.posting_time,
                sle.item_code,
                i.item_name,
                sle.warehouse,
                sle.actual_qty,
                sle.qty_after_transaction,
                sle.valuation_rate,
                sle.stock_value,
                sle.stock_value_difference,
                sle.voucher_type,
                sle.voucher_no
            FROM `tabStock Ledger Entry` sle
            LEFT JOIN `tabItem` i ON sle.item_code = i.name
            WHERE {where_clause}
            ORDER BY sle.posting_date DESC, sle.posting_time DESC, sle.creation DESC
            LIMIT %s OFFSET %s
        """, params + [page_size, offset], as_dict=True)
        
        return {
            "data": entries,
            "total": total,
            "page": page,
            "page_size": page_size,
            "total_pages": (total + page_size - 1) // page_size if total > 0 else 1
        }
    except Exception as e:
        frappe.log_error(frappe.get_traceback(), "get_stock_ledger Error")
        return []


@frappe.whitelist()
def get_warehouse_details(warehouse):
    """
    Lấy thông tin chi tiết kho với tổng hợp tồn kho
    
    Args:
        warehouse: Tên kho
    
    Returns:
        dict: Thông tin kho và tồn kho
    """
    try:
        # Warehouse info
        wh = frappe.get_doc("Warehouse", warehouse)
        
        # Stock summary
        stock_summary = frappe.db.sql("""
            SELECT 
                COUNT(DISTINCT item_code) as total_items,
                SUM(actual_qty) as total_qty,
                SUM(stock_value) as total_value
            FROM `tabBin`
            WHERE warehouse = %s AND actual_qty > 0
        """, warehouse, as_dict=True)[0]
        
        # By item group
        by_group = frappe.db.sql("""
            SELECT 
                i.item_group,
                COUNT(*) as item_count,
                SUM(b.actual_qty) as qty,
                SUM(b.stock_value) as value
            FROM `tabBin` b
            LEFT JOIN `tabItem` i ON b.item_code = i.name
            WHERE b.warehouse = %s AND b.actual_qty > 0
            GROUP BY i.item_group
            ORDER BY value DESC
        """, warehouse, as_dict=True)
        
        return {
            "warehouse": {
                "name": wh.name,
                "warehouse_name": wh.warehouse_name,
                "company": wh.company,
                "warehouse_type": wh.warehouse_type,
                "parent_warehouse": wh.parent_warehouse
            },
            "summary": stock_summary,
            "by_item_group": by_group
        }
    except Exception as e:
        frappe.log_error(frappe.get_traceback(), "get_warehouse_details Error")
        return {"warehouse": {}, "summary": {}, "by_item_group": []}


# ============================================
# ITEM MANAGEMENT APIs
# ============================================

@frappe.whitelist()
def get_item_list(search=None, item_group=None, is_stock_item=None, disabled=None, page=1, page_size=20):
    """
    Lấy danh sách Item với phân trang và filter
    
    Args:
        search: Tìm kiếm theo mã hoặc tên item
        item_group: Lọc theo nhóm hàng (bao gồm cả sub-groups)
        is_stock_item: Lọc hàng tồn kho (1/0)
        disabled: Lọc trạng thái (0=active, 1=disabled)
        page: Trang hiện tại
        page_size: Số items/trang
    
    Returns:
        dict: {data, total, page, page_size, total_pages}
    """
    try:
        page = int(page)
        page_size = int(page_size)
        offset = (page - 1) * page_size
        
        # Build filters
        filters = {}
        
        # Filter theo item_group bao gồm cả sub-groups
        if item_group:
            # Lấy lft/rgt của group được chọn
            group_doc = frappe.db.get_value("Item Group", item_group, ["lft", "rgt"], as_dict=True)
            if group_doc:
                # Lấy tất cả sub-groups
                sub_groups = frappe.get_all(
                    "Item Group",
                    filters={"lft": [">=", group_doc.lft], "rgt": ["<=", group_doc.rgt]},
                    pluck="name"
                )
                filters["item_group"] = ["in", sub_groups]
            else:
                filters["item_group"] = item_group
        
        if is_stock_item is not None and is_stock_item != "":
            filters["is_stock_item"] = int(is_stock_item)
        
        if disabled is not None and disabled != "":
            filters["disabled"] = int(disabled)
        else:
            filters["disabled"] = 0  # Default: chỉ lấy active
        
        # Search - sử dụng SQL trực tiếp cho or_filters vì db.count không hỗ trợ or_filters
        or_filters = None
        if search:
            or_filters = [
                ["item_code", "like", f"%{search}%"],
                ["item_name", "like", f"%{search}%"]
            ]
        
        # Get total count - dùng get_all với count
        if or_filters:
            total = len(frappe.get_all("Item", filters=filters, or_filters=or_filters, pluck="name"))
        else:
            total = frappe.db.count("Item", filters=filters)
        
        # Get data
        items = frappe.get_all(
            "Item",
            filters=filters,
            or_filters=or_filters,
            fields=[
                "name", "item_code", "item_name", "item_group",
                "stock_uom", "is_stock_item", "is_purchase_item", "is_sales_item",
                "disabled", "description", "standard_rate", "valuation_rate",
                "opening_stock", "image", "creation", "modified"
            ],
            order_by="modified desc",
            start=offset,
            page_length=page_size
        )
        
        # Add additional info
        for item in items:
            # Lấy số lượng tồn kho
            stock = frappe.db.sql("""
                SELECT SUM(actual_qty) as qty, SUM(stock_value) as value
                FROM `tabBin` WHERE item_code = %s
            """, item.item_code, as_dict=True)
            item["total_qty"] = stock[0].qty or 0 if stock else 0
            item["total_value"] = stock[0].value or 0 if stock else 0
            
            # Kiểm tra có BOM không
            item["has_bom"] = frappe.db.exists("BOM", {"item": item.item_code, "docstatus": 1, "is_active": 1})
        
        return {
            "data": items,
            "total": total,
            "page": page,
            "page_size": page_size,
            "total_pages": (total + page_size - 1) // page_size if total > 0 else 1
        }
    except Exception as e:
        frappe.log_error(frappe.get_traceback(), "get_item_list Error")
        return {"data": [], "total": 0, "page": 1, "page_size": page_size, "total_pages": 1}


@frappe.whitelist()
def get_item_detail(item_code):
    """
    Lấy chi tiết Item
    
    Args:
        item_code: Mã item
    
    Returns:
        dict: Chi tiết item
    """
    try:
        if not frappe.db.exists("Item", item_code):
            return {"success": False, "message": _("Item không tồn tại")}
        
        doc = frappe.get_doc("Item", item_code)
        
        # Lấy stock info
        stock_info = frappe.db.sql("""
            SELECT 
                b.warehouse,
                w.warehouse_name,
                b.actual_qty,
                b.stock_value,
                b.valuation_rate
            FROM `tabBin` b
            LEFT JOIN `tabWarehouse` w ON b.warehouse = w.name
            WHERE b.item_code = %s AND b.actual_qty != 0
            ORDER BY b.actual_qty DESC
        """, item_code, as_dict=True)
        
        # Lấy BOM
        boms = frappe.get_all(
            "BOM",
            filters={"item": item_code, "docstatus": 1},
            fields=["name", "is_active", "is_default", "total_cost", "quantity"]
        )
        
        return {
            "success": True,
            "item_code": doc.item_code,
            "item_name": doc.item_name,
            "item_group": doc.item_group,
            "stock_uom": doc.stock_uom,
            "description": doc.description,
            "is_stock_item": doc.is_stock_item,
            "is_purchase_item": doc.is_purchase_item,
            "is_sales_item": doc.is_sales_item,
            "disabled": doc.disabled,
            "standard_rate": doc.standard_rate,
            "valuation_rate": doc.valuation_rate,
            "image": doc.image,
            "stock_info": stock_info,
            "boms": boms
        }
    except Exception as e:
        frappe.log_error(frappe.get_traceback(), "get_item_detail Error")
        return {"success": False, "message": str(e)}


@frappe.whitelist()
def create_item(item_code, item_name, item_group, stock_uom="Nos", is_stock_item=1, 
                is_purchase_item=1, is_sales_item=0, standard_rate=0, description=None):
    """
    Tạo Item mới
    
    Args:
        item_code: Mã item
        item_name: Tên item
        item_group: Nhóm hàng
        stock_uom: Đơn vị tính (mặc định: Nos)
        is_stock_item: Là hàng tồn kho (1/0)
        is_purchase_item: Có thể mua (1/0)
        is_sales_item: Có thể bán (1/0)
        standard_rate: Giá tiêu chuẩn
        description: Mô tả
    
    Returns:
        dict: {success, name, message}
    """
    try:
        if frappe.db.exists("Item", item_code):
            return {"success": False, "message": _("Mã item {0} đã tồn tại").format(item_code)}
        
        doc = frappe.new_doc("Item")
        doc.item_code = item_code
        doc.item_name = item_name
        doc.item_group = item_group
        doc.stock_uom = stock_uom
        doc.is_stock_item = int(is_stock_item)
        doc.is_purchase_item = int(is_purchase_item)
        doc.is_sales_item = int(is_sales_item)
        doc.standard_rate = float(standard_rate) if standard_rate else 0
        
        if description:
            doc.description = description
        
        doc.insert()
        
        return {
            "success": True,
            "name": doc.name,
            "message": _("Đã tạo item {0}").format(item_code)
        }
    except Exception as e:
        frappe.log_error(frappe.get_traceback(), "create_item Error")
        return {"success": False, "message": str(e)}


@frappe.whitelist()
def update_item(item_code, item_name=None, item_group=None, stock_uom=None,
                is_purchase_item=None, is_sales_item=None, standard_rate=None, 
                description=None, disabled=None):
    """
    Cập nhật Item
    
    Args:
        item_code: Mã item
        ... các fields cần update
    
    Returns:
        dict: {success, message}
    """
    try:
        if not frappe.db.exists("Item", item_code):
            return {"success": False, "message": _("Item không tồn tại")}
        
        doc = frappe.get_doc("Item", item_code)
        
        if item_name is not None:
            doc.item_name = item_name
        if item_group is not None:
            doc.item_group = item_group
        if stock_uom is not None:
            doc.stock_uom = stock_uom
        if is_purchase_item is not None:
            doc.is_purchase_item = int(is_purchase_item)
        if is_sales_item is not None:
            doc.is_sales_item = int(is_sales_item)
        if standard_rate is not None:
            doc.standard_rate = float(standard_rate)
        if description is not None:
            doc.description = description
        if disabled is not None:
            doc.disabled = int(disabled)
        
        doc.save()
        
        return {
            "success": True,
            "message": _("Đã cập nhật item {0}").format(item_code)
        }
    except Exception as e:
        frappe.log_error(frappe.get_traceback(), "update_item Error")
        return {"success": False, "message": str(e)}


@frappe.whitelist()
def toggle_item_status(item_code):
    """
    Bật/tắt trạng thái Item
    """
    try:
        doc = frappe.get_doc("Item", item_code)
        doc.disabled = 0 if doc.disabled else 1
        doc.save()
        
        status = "vô hiệu hóa" if doc.disabled else "kích hoạt"
        return {
            "success": True,
            "disabled": doc.disabled,
            "message": _("Đã {0} item {1}").format(status, item_code)
        }
    except Exception as e:
        frappe.log_error(frappe.get_traceback(), "toggle_item_status Error")
        return {"success": False, "message": str(e)}


# ============================================
# ITEM GROUP MANAGEMENT APIs
# ============================================

@frappe.whitelist()
def get_item_group_list(search=None, parent=None):
    """
    Lấy danh sách Item Group
    
    Args:
        search: Tìm kiếm theo tên
        parent: Lọc theo parent group
    
    Returns:
        list: Danh sách item groups
    """
    try:
        filters = {}
        
        if parent:
            filters["parent_item_group"] = parent
        
        or_filters = None
        if search:
            or_filters = [
                ["item_group_name", "like", f"%{search}%"],
                ["name", "like", f"%{search}%"]
            ]
        
        groups = frappe.get_all(
            "Item Group",
            filters=filters,
            or_filters=or_filters,
            fields=["name", "item_group_name", "parent_item_group", "is_group", "image", "lft", "rgt"],
            order_by="lft"
        )
        
        # Đếm số item trong mỗi group (bao gồm cả sub-groups)
        for group in groups:
            # Sử dụng lft/rgt để đếm items trong group và tất cả sub-groups
            group["item_count"] = frappe.db.count("Item", {
                "item_group": ["in", frappe.get_all(
                    "Item Group",
                    filters={"lft": [">=", group.lft], "rgt": ["<=", group.rgt]},
                    pluck="name"
                )],
                "disabled": 0
            }) if group.lft and group.rgt else frappe.db.count("Item", {"item_group": group.name, "disabled": 0})
            # Đếm số subgroup trực tiếp
            group["subgroup_count"] = frappe.db.count("Item Group", {"parent_item_group": group.name})
        
        return groups
    except Exception as e:
        frappe.log_error(frappe.get_traceback(), "get_item_group_list Error")
        return []


@frappe.whitelist()
def get_item_group_tree():
    """
    Lấy cây Item Group (hierarchical)
    
    Returns:
        list: Cây item groups
    """
    try:
        # Lấy tất cả groups với lft/rgt để đếm items trong sub-groups
        groups = frappe.get_all(
            "Item Group",
            fields=["name", "item_group_name", "parent_item_group", "is_group", "lft", "rgt"],
            order_by="lft"
        )
        
        # Đếm items cho mỗi group (bao gồm cả sub-groups)
        for group in groups:
            # Lấy tất cả sub-groups dựa trên lft/rgt
            sub_groups = [g.name for g in groups if g.lft >= group.lft and g.rgt <= group.rgt]
            group["item_count"] = frappe.db.count("Item", {"item_group": ["in", sub_groups], "disabled": 0}) if sub_groups else 0
        
        # Build tree
        def build_tree(parent=None):
            children = []
            for group in groups:
                if group.parent_item_group == parent:
                    node = {
                        "name": group.name,
                        "item_group_name": group.item_group_name,
                        "is_group": group.is_group,
                        "item_count": group.item_count,
                        "children": build_tree(group.name)
                    }
                    children.append(node)
            return children
        
        return build_tree("All Item Groups")
    except Exception as e:
        frappe.log_error(frappe.get_traceback(), "get_item_group_tree Error")
        return []


@frappe.whitelist()
def create_item_group(item_group_name, parent_item_group="All Item Groups", is_group=0):
    """
    Tạo Item Group mới
    
    Args:
        item_group_name: Tên nhóm
        parent_item_group: Nhóm cha
        is_group: Có phải là nhóm chứa (1/0)
    
    Returns:
        dict: {success, name, message}
    """
    try:
        if frappe.db.exists("Item Group", item_group_name):
            return {"success": False, "message": _("Nhóm hàng {0} đã tồn tại").format(item_group_name)}
        
        doc = frappe.new_doc("Item Group")
        doc.item_group_name = item_group_name
        doc.parent_item_group = parent_item_group
        doc.is_group = int(is_group)
        
        doc.insert()
        
        return {
            "success": True,
            "name": doc.name,
            "message": _("Đã tạo nhóm hàng {0}").format(item_group_name)
        }
    except Exception as e:
        frappe.log_error(frappe.get_traceback(), "create_item_group Error")
        return {"success": False, "message": str(e)}


@frappe.whitelist()
def update_item_group(name, item_group_name=None, parent_item_group=None):
    """
    Cập nhật Item Group
    """
    try:
        if not frappe.db.exists("Item Group", name):
            return {"success": False, "message": _("Nhóm hàng không tồn tại")}
        
        new_name = name
        
        # Nếu đổi tên, phải rename document vì name = item_group_name trong Item Group
        if item_group_name and item_group_name != name:
            # Rename document (sẽ tự động cập nhật các liên kết)
            frappe.rename_doc("Item Group", name, item_group_name, merge=False)
            new_name = item_group_name
            frappe.db.commit()
        
        # Cập nhật parent nếu cần
        if parent_item_group:
            doc = frappe.get_doc("Item Group", new_name)
            doc.parent_item_group = parent_item_group
            doc.save()
            frappe.db.commit()
        
        return {
            "success": True,
            "new_name": new_name,
            "message": _("Đã cập nhật nhóm hàng {0}").format(new_name)
        }
    except Exception as e:
        frappe.log_error(frappe.get_traceback(), "update_item_group Error")
        return {"success": False, "message": str(e)}


@frappe.whitelist()
def delete_item_group(name):
    """
    Xóa Item Group (chỉ khi không có item nào)
    """
    try:
        if not frappe.db.exists("Item Group", name):
            return {"success": False, "message": _("Nhóm hàng không tồn tại")}
        
        # Kiểm tra có item không
        item_count = frappe.db.count("Item", {"item_group": name})
        if item_count > 0:
            return {
                "success": False, 
                "message": _("Không thể xóa nhóm hàng {0} vì còn {1} sản phẩm").format(name, item_count)
            }
        
        # Kiểm tra có subgroup không
        subgroup_count = frappe.db.count("Item Group", {"parent_item_group": name})
        if subgroup_count > 0:
            return {
                "success": False,
                "message": _("Không thể xóa nhóm hàng {0} vì còn {1} nhóm con").format(name, subgroup_count)
            }
        
        frappe.delete_doc("Item Group", name)
        
        return {
            "success": True,
            "message": _("Đã xóa nhóm hàng {0}").format(name)
        }
    except Exception as e:
        frappe.log_error(frappe.get_traceback(), "delete_item_group Error")
        return {"success": False, "message": str(e)}


@frappe.whitelist()
def get_uom_list():
    """
    Lấy danh sách đơn vị tính
    """
    try:
        uoms = frappe.get_all(
            "UOM",
            filters={"enabled": 1},
            fields=["name", "uom_name"],
            order_by="name"
        )
        return uoms
    except Exception as e:
        return []


# ============================================
# DASHBOARD STATISTICS APIs
# ============================================

@frappe.whitelist()
def get_stock_dashboard():
    """
    Lấy thống kê tổng quan cho Stock Dashboard
    
    Returns:
        dict: Dữ liệu thống kê kho hàng
    """
    try:
        from datetime import datetime, timedelta
        today = datetime.now().date()
        week_ago = today - timedelta(days=7)
        month_ago = today - timedelta(days=30)
        
        # Tổng giá trị tồn kho
        stock_value = frappe.db.sql("""
            SELECT IFNULL(SUM(stock_value), 0) as total_value
            FROM `tabBin`
            WHERE actual_qty > 0
        """, as_dict=1)[0].total_value or 0
        
        # Số lượng sản phẩm đang tồn
        total_items = frappe.db.count("Bin", {"actual_qty": (">", 0)})
        
        # Sản phẩm sắp hết (dưới reorder level)
        low_stock_items = frappe.db.sql("""
            SELECT COUNT(*) as count
            FROM `tabBin` b
            INNER JOIN `tabItem Reorder` ir ON b.item_code = ir.parent
            WHERE b.actual_qty > 0 
            AND b.actual_qty <= ir.warehouse_reorder_level
            AND b.warehouse = ir.warehouse
        """, as_dict=1)[0].count or 0
        
        # Phiếu nhập kho tháng này
        receipts_month = frappe.db.count("Stock Entry", {
            "purpose": "Material Receipt",
            "docstatus": 1,
            "posting_date": (">=", month_ago)
        })
        
        # Phiếu xuất kho tháng này
        issues_month = frappe.db.count("Stock Entry", {
            "purpose": "Material Issue",
            "docstatus": 1,
            "posting_date": (">=", month_ago)
        })
        
        # Top 5 sản phẩm tồn kho nhiều nhất theo giá trị
        top_items_by_value = frappe.db.sql("""
            SELECT 
                b.item_code,
                i.item_name,
                SUM(b.actual_qty) as total_qty,
                i.stock_uom as uom,
                SUM(b.stock_value) as total_value
            FROM `tabBin` b
            INNER JOIN `tabItem` i ON b.item_code = i.name
            WHERE b.actual_qty > 0
            GROUP BY b.item_code, i.item_name, i.stock_uom
            ORDER BY total_value DESC
            LIMIT 5
        """, as_dict=1)
        
        # Biến động kho 6 tháng gần đây
        from dateutil.relativedelta import relativedelta
        stock_movement = []
        
        # Lấy 6 tháng gần nhất
        for i in range(6):
            month_date = today - relativedelta(months=i)
            month_start = month_date.replace(day=1)
            # Ngày cuối tháng
            next_month = month_start + relativedelta(months=1)
            month_end = next_month - timedelta(days=1)
            
            receipts = frappe.db.count("Stock Entry", {
                "purpose": "Material Receipt",
                "docstatus": 1,
                "posting_date": ("between", [month_start, month_end])
            })
            
            issues = frappe.db.count("Stock Entry", {
                "purpose": "Material Issue",
                "docstatus": 1,
                "posting_date": ("between", [month_start, month_end])
            })
            
            month_label = f"T{month_date.month}/{month_date.year}"
            stock_movement.insert(0, {
                "day": month_label,
                "date": str(month_end),
                "receipts": receipts,
                "issues": issues
            })
        
        # Kho có nhiều giao dịch nhất (tháng này)
        top_warehouses = frappe.db.sql("""
            SELECT 
                warehouse,
                COUNT(*) as transaction_count
            FROM (
                SELECT DISTINCT sed.t_warehouse as warehouse, se.name
                FROM `tabStock Entry` se
                INNER JOIN `tabStock Entry Detail` sed ON se.name = sed.parent
                WHERE se.docstatus = 1
                AND se.posting_date >= %s
                AND sed.t_warehouse IS NOT NULL
                UNION ALL
                SELECT DISTINCT sed.s_warehouse as warehouse, se.name
                FROM `tabStock Entry` se
                INNER JOIN `tabStock Entry Detail` sed ON se.name = sed.parent
                WHERE se.docstatus = 1
                AND se.posting_date >= %s
                AND sed.s_warehouse IS NOT NULL
            ) as warehouse_transactions
            GROUP BY warehouse
            ORDER BY transaction_count DESC
            LIMIT 5
        """, (month_ago, month_ago), as_dict=1)
        
        return {
            "stock_value": stock_value,
            "total_items": total_items,
            "low_stock_items": low_stock_items,
            "receipts_month": receipts_month,
            "issues_month": issues_month,
            "top_items": top_items_by_value,
            "stock_movement": stock_movement,
            "top_warehouses": top_warehouses
        }
    except Exception as e:
        frappe.log_error(frappe.get_traceback(), "get_stock_dashboard Error")
        return {}


@frappe.whitelist()
def get_production_dashboard():
    """
    Lấy thống kê tổng quan cho Production Dashboard
    
    Returns:
        dict: Dữ liệu thống kê sản xuất
    """
    try:
        from datetime import datetime, timedelta
        today = datetime.now().date()
        week_ago = today - timedelta(days=7)
        month_ago = today - timedelta(days=30)
        
        # Tổng số lệnh sản xuất
        total_work_orders = frappe.db.count("Work Order")
        
        # Lệnh theo trạng thái
        wo_not_started = frappe.db.count("Work Order", {"status": "Not Started"})
        wo_in_progress = frappe.db.count("Work Order", {"status": "In Process"})
        wo_completed = frappe.db.count("Work Order", {"status": "Completed"})
        wo_stopped = frappe.db.count("Work Order", {"status": "Stopped"})
        
        # Lệnh tạo trong tuần
        wo_this_week = frappe.db.count("Work Order", {
            "creation": (">=", week_ago)
        })
        
        # Lệnh hoàn thành tuần này
        wo_completed_week = frappe.db.count("Work Order", {
            "status": "Completed",
            "modified": (">=", week_ago)
        })
        
        # Tổng số lượng sản phẩm đã sản xuất tháng này
        qty_produced_month = frappe.db.sql("""
            SELECT IFNULL(SUM(produced_qty), 0) as total
            FROM `tabWork Order`
            WHERE modified >= %s
        """, (month_ago,), as_dict=1)[0].total or 0
        
        # Top 5 sản phẩm sản xuất nhiều nhất
        top_products = frappe.db.sql("""
            SELECT 
                wo.production_item,
                i.item_name,
                COUNT(*) as order_count,
                SUM(wo.qty) as total_qty,
                SUM(wo.produced_qty) as produced_qty,
                i.stock_uom as uom
            FROM `tabWork Order` wo
            INNER JOIN `tabItem` i ON wo.production_item = i.name
            GROUP BY wo.production_item, i.item_name, i.stock_uom
            ORDER BY produced_qty DESC
            LIMIT 5
        """, as_dict=1)
        
        # Hiệu suất sản xuất 6 tháng gần đây
        from dateutil.relativedelta import relativedelta
        production_trend = []
        for i in range(6):
            month_date = today - relativedelta(months=i)
            month_start = month_date.replace(day=1)
            next_month = month_start + relativedelta(months=1)
            month_end = next_month - timedelta(days=1)
            
            created = frappe.db.count("Work Order", {
                "creation": ("between", [month_start, month_end])
            })
            
            completed = frappe.db.count("Work Order", {
                "status": "Completed",
                "modified": ("between", [month_start, month_end])
            })
            
            month_label = f"T{month_date.month}/{month_date.year}"
            production_trend.insert(0, {
                "day": month_label,
                "date": str(month_end),
                "created": created,
                "completed": completed
            })
        
        # Lệnh sắp hết hạn (planned_end_date trong 3 ngày tới)
        upcoming_deadline = today + timedelta(days=3)
        urgent_orders = frappe.db.sql("""
            SELECT 
                name,
                production_item,
                qty,
                produced_qty,
                status,
                planned_end_date
            FROM `tabWork Order`
            WHERE status IN ('Not Started', 'In Process')
            AND planned_end_date BETWEEN %s AND %s
            ORDER BY planned_end_date ASC
            LIMIT 5
        """, (today, upcoming_deadline), as_dict=1)
        
        return {
            "total_work_orders": total_work_orders,
            "wo_not_started": wo_not_started,
            "wo_in_progress": wo_in_progress,
            "wo_completed": wo_completed,
            "wo_stopped": wo_stopped,
            "wo_this_week": wo_this_week,
            "wo_completed_week": wo_completed_week,
            "qty_produced_month": qty_produced_month,
            "top_products": top_products,
            "production_trend": production_trend,
            "urgent_orders": urgent_orders
        }
    except Exception as e:
        frappe.log_error(frappe.get_traceback(), "get_production_dashboard Error")
        return {}


@frappe.whitelist()
def get_inventory_dashboard():
    """
    Lấy thống kê chi tiết hàng tồn kho theo warehouse
    
    Returns:
        dict: Dữ liệu tồn kho chi tiết
    """
    try:
        # Tồn kho theo warehouse
        warehouse_stock = frappe.db.sql("""
            SELECT 
                b.warehouse,
                COUNT(DISTINCT b.item_code) as item_count,
                SUM(b.actual_qty) as total_qty,
                SUM(b.stock_value) as total_value
            FROM `tabBin` b
            WHERE b.actual_qty > 0
            GROUP BY b.warehouse
            ORDER BY total_value DESC
        """, as_dict=1)
        
        # Phân loại theo Item Group
        items_by_group = frappe.db.sql("""
            SELECT 
                i.item_group,
                COUNT(DISTINCT b.item_code) as item_count,
                SUM(b.actual_qty) as total_qty,
                SUM(b.stock_value) as total_value
            FROM `tabBin` b
            INNER JOIN `tabItem` i ON b.item_code = i.name
            WHERE b.actual_qty > 0
            GROUP BY i.item_group
            ORDER BY total_value DESC
            LIMIT 10
        """, as_dict=1)
        
        return {
            "warehouse_stock": warehouse_stock,
            "items_by_group": items_by_group
        }
    except Exception as e:
        frappe.log_error(frappe.get_traceback(), "get_inventory_dashboard Error")
        return {}


@frappe.whitelist()
def get_sales_purchase_dashboard():
    """
    Lấy thống kê tổng quan cho mua bán (Purchase & Sales)
    
    Returns:
        dict: Dữ liệu thống kê mua bán
    """
    try:
        from datetime import datetime, timedelta
        today = datetime.now().date()
        month_ago = today - timedelta(days=30)
        this_month_start = today.replace(day=1)
        
        # Thống kê hóa đơn mua
        total_purchase = frappe.db.count("Purchase Invoice")
        purchase_pending = frappe.db.count("Purchase Invoice", {"docstatus": 0})
        purchase_submitted = frappe.db.count("Purchase Invoice", {"docstatus": 1})
        purchase_cancelled = frappe.db.count("Purchase Invoice", {"docstatus": 2})
        
        # Tổng giá trị mua tháng này
        purchase_value_month = frappe.db.sql("""
            SELECT IFNULL(SUM(grand_total), 0) as total
            FROM `tabPurchase Invoice`
            WHERE docstatus = 1
            AND posting_date >= %s
        """, (this_month_start,), as_dict=1)[0].total or 0
        
        # Thống kê hóa đơn bán
        total_sales = frappe.db.count("Sales Invoice")
        sales_pending = frappe.db.count("Sales Invoice", {"docstatus": 0})
        sales_submitted = frappe.db.count("Sales Invoice", {"docstatus": 1})
        sales_cancelled = frappe.db.count("Sales Invoice", {"docstatus": 2})
        
        # Tổng giá trị bán tháng này
        sales_value_month = frappe.db.sql("""
            SELECT IFNULL(SUM(grand_total), 0) as total
            FROM `tabSales Invoice`
            WHERE docstatus = 1
            AND posting_date >= %s
        """, (this_month_start,), as_dict=1)[0].total or 0
        
        # Xu hướng mua bán 6 tháng
        from dateutil.relativedelta import relativedelta
        purchase_sales_trend = []
        for i in range(6):
            month_date = today - relativedelta(months=i)
            month_start = month_date.replace(day=1)
            next_month = month_start + relativedelta(months=1)
            month_end = next_month - timedelta(days=1)
            
            purchase_count = frappe.db.count("Purchase Invoice", {
                "docstatus": 1,
                "posting_date": ("between", [month_start, month_end])
            })
            
            purchase_value = frappe.db.sql("""
                SELECT IFNULL(SUM(grand_total), 0) as total
                FROM `tabPurchase Invoice`
                WHERE docstatus = 1
                AND posting_date BETWEEN %s AND %s
            """, (month_start, month_end), as_dict=1)[0].total or 0
            
            sales_count = frappe.db.count("Sales Invoice", {
                "docstatus": 1,
                "posting_date": ("between", [month_start, month_end])
            })
            
            sales_value = frappe.db.sql("""
                SELECT IFNULL(SUM(grand_total), 0) as total
                FROM `tabSales Invoice`
                WHERE docstatus = 1
                AND posting_date BETWEEN %s AND %s
            """, (month_start, month_end), as_dict=1)[0].total or 0
            
            month_label = f"T{month_date.month}/{month_date.year}"
            purchase_sales_trend.insert(0, {
                "week": month_label,
                "date": str(month_end),
                "purchase_count": purchase_count,
                "purchase_value": purchase_value,
                "sales_count": sales_count,
                "sales_value": sales_value
            })
        
        # Top 5 nhà cung cấp (theo giá trị mua)
        top_suppliers = frappe.db.sql("""
            SELECT 
                supplier,
                COUNT(*) as invoice_count,
                SUM(grand_total) as total_value
            FROM `tabPurchase Invoice`
            WHERE docstatus = 1
            AND posting_date >= %s
            GROUP BY supplier
            ORDER BY total_value DESC
            LIMIT 5
        """, (month_ago,), as_dict=1)
        
        # Top 5 khách hàng (theo giá trị bán)
        top_customers = frappe.db.sql("""
            SELECT 
                customer,
                COUNT(*) as invoice_count,
                SUM(grand_total) as total_value
            FROM `tabSales Invoice`
            WHERE docstatus = 1
            AND posting_date >= %s
            GROUP BY customer
            ORDER BY total_value DESC
            LIMIT 5
        """, (month_ago,), as_dict=1)
        
        # Top sản phẩm mua nhiều nhất
        top_purchased_items = frappe.db.sql("""
            SELECT 
                pii.item_code,
                pii.item_name,
                SUM(pii.qty) as total_qty,
                pii.uom,
                SUM(pii.amount) as total_amount
            FROM `tabPurchase Invoice Item` pii
            INNER JOIN `tabPurchase Invoice` pi ON pii.parent = pi.name
            WHERE pi.docstatus = 1
            AND pi.posting_date >= %s
            GROUP BY pii.item_code, pii.item_name, pii.uom
            ORDER BY total_amount DESC
            LIMIT 5
        """, (month_ago,), as_dict=1)
        
        # Top sản phẩm bán nhiều nhất
        top_sold_items = frappe.db.sql("""
            SELECT 
                sii.item_code,
                sii.item_name,
                SUM(sii.qty) as total_qty,
                sii.uom,
                SUM(sii.amount) as total_amount
            FROM `tabSales Invoice Item` sii
            INNER JOIN `tabSales Invoice` si ON sii.parent = si.name
            WHERE si.docstatus = 1
            AND si.posting_date >= %s
            GROUP BY sii.item_code, sii.item_name, sii.uom
            ORDER BY total_amount DESC
            LIMIT 5
        """, (month_ago,), as_dict=1)
        
        # Lợi nhuận gộp (chỉ ước tính đơn giản)
        gross_profit = sales_value_month - purchase_value_month
        profit_margin = (gross_profit / sales_value_month * 100) if sales_value_month > 0 else 0
        
        return {
            "total_purchase": total_purchase,
            "purchase_pending": purchase_pending,
            "purchase_submitted": purchase_submitted,
            "purchase_cancelled": purchase_cancelled,
            "purchase_value_month": purchase_value_month,
            "total_sales": total_sales,
            "sales_pending": sales_pending,
            "sales_submitted": sales_submitted,
            "sales_cancelled": sales_cancelled,
            "sales_value_month": sales_value_month,
            "gross_profit": gross_profit,
            "profit_margin": profit_margin,
            "purchase_sales_trend": purchase_sales_trend,
            "top_suppliers": top_suppliers,
            "top_customers": top_customers,
            "top_purchased_items": top_purchased_items,
            "top_sold_items": top_sold_items
        }
    except Exception as e:
        frappe.log_error(frappe.get_traceback(), "get_sales_purchase_dashboard Error")
        return {}

