"""
Stock Entry Hooks - Tự động set naming series cho từng loại phiếu kho

Naming conventions:
- NK-YYYY-XXXXX: Phiếu nhập kho (Material Receipt)
- XK-YYYY-XXXXX: Phiếu xuất kho (Material Issue)  
- CK-YYYY-XXXXX: Phiếu chuyển kho (Material Transfer)
- CP-YYYY-XXXXX: Phiếu cấp phát NVL (Material Transfer for Manufacture)
- SX-YYYY-XXXXX: Phiếu sản xuất (Manufacture)
- DG-YYYY-XXXXX: Phiếu đóng gói (Repack)
- TG-YYYY-XXXXX: Phiếu tháo gỡ (Disassemble)
"""

import frappe
from frappe.utils import nowdate


# Mapping từ stock_entry_type/purpose sang naming_series prefix
NAMING_SERIES_MAP = {
    "Material Receipt": "NK-.YYYY.-",
    "Material Issue": "XK-.YYYY.-",
    "Material Transfer": "CK-.YYYY.-",
    "Material Transfer for Manufacture": "CP-.YYYY.-",
    "Manufacture": "SX-.YYYY.-",
    "Repack": "DG-.YYYY.-",
    "Disassemble": "TG-.YYYY.-",
    "Send to Subcontractor": "GC-.YYYY.-",
    "Material Consumption for Manufacture": "TH-.YYYY.-",
}

# Default naming series
DEFAULT_NAMING_SERIES = "KHO-.YYYY.-"


def set_naming_series(doc, method=None):
    """
    Hook chạy trước khi insert Stock Entry
    Tự động set naming_series dựa trên stock_entry_type hoặc purpose
    """
    # Xác định loại phiếu
    entry_type = doc.stock_entry_type or doc.purpose
    
    # Lấy naming_series phù hợp
    naming_series = NAMING_SERIES_MAP.get(entry_type, DEFAULT_NAMING_SERIES)
    
    # Set naming_series
    doc.naming_series = naming_series


def get_vietnamese_entry_type(entry_type):
    """
    Trả về tên tiếng Việt cho loại phiếu kho
    """
    TYPE_LABELS = {
        "Material Receipt": "Phiếu nhập kho",
        "Material Issue": "Phiếu xuất kho",
        "Material Transfer": "Phiếu chuyển kho",
        "Material Transfer for Manufacture": "Phiếu cấp phát NVL",
        "Manufacture": "Phiếu sản xuất",
        "Repack": "Phiếu đóng gói",
        "Disassemble": "Phiếu tháo gỡ",
        "Send to Subcontractor": "Phiếu gửi gia công",
        "Material Consumption for Manufacture": "Phiếu tiêu hao NVL",
    }
    return TYPE_LABELS.get(entry_type, entry_type)
