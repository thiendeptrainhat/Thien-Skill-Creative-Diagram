"""Original D-093 detailed IT current-state fixture."""
from semantic_fixtures import e, finalize, g, n


def it_current_state_fixture():
    nodes = [
        n("source-pos", "system", "Xuất dữ liệu điểm bán | hàng đêm · CSV", state="manual-export"),
        n("source-commerce", "system", "Xuất dữ liệu trực tuyến | đơn hàng · tệp phẳng", state="manual-export"),
        n("source-supplier", "system", "Bảng giá nhà cung cấp | nguồn ngoài · XLSX", state="external-source"),
        n("processing-shared-drive", "data-store", "Ổ đĩa dùng chung | không phiên bản · thư mục phòng ban", state="bottleneck"),
        n("processing-spreadsheet", "system", "Bàn giao bảng tính | workbook cục bộ · macro · đối soát tay", state="manual-handoff"),
        n("processing-rdbms", "data-store", "CSDL tại chỗ | tồn kho · tài chính", state="active"),
        n("delivery-portal", "system", "Cổng báo cáo | làm mới thủ công", state="bottleneck"),
        n("delivery-email", "system", "Bộ báo cáo qua email | hàng tuần · PDF", state="manual-output"),
        n("delivery-regional", "owner", "Quản lý vùng | 12 khu vực cửa hàng", state="external-recipient"),
    ]
    edges = [
        e("handoff-pos-drive", "source-pos", "processing-shared-drive", "handoff", label="CSV", order=1),
        e("handoff-commerce-drive", "source-commerce", "processing-shared-drive", "handoff", label="EXPORT", order=2),
        e("handoff-supplier-drive", "source-supplier", "processing-shared-drive", "handoff", label="XLSX", order=3),
        e("handoff-drive-spreadsheet", "processing-shared-drive", "processing-spreadsheet", "handoff", label="COPY", order=4),
        e("integration-spreadsheet-rdbms", "processing-spreadsheet", "processing-rdbms", "integration", label="LOAD", order=5),
        e("handoff-spreadsheet-portal", "processing-spreadsheet", "delivery-portal", "handoff", label="XLSX", order=6),
        e("handoff-portal-email", "delivery-portal", "delivery-email", "handoff", label="PDF", order=7),
        e("handoff-email-regional", "delivery-email", "delivery-regional", "handoff", label="EMAIL", order=8),
    ]
    ir = finalize(
        "it-current-state",
        nodes=nodes,
        edges=edges,
        groups=[
            g("group-collection", "THU THẬP", ["source-pos", "source-commerce", "source-supplier"]),
            g("group-processing", "XỬ LÝ", ["processing-shared-drive", "processing-spreadsheet", "processing-rdbms"]),
            g("group-dissemination", "PHÂN PHỐI", ["delivery-portal", "delivery-email", "delivery-regional"]),
        ],
    )
    ir["diagram"].update({"title": "Hiện trạng luồng báo cáo", "detail": "faithful", "audience": "mixed"})
    ir["accessibility"].update({
        "name": "Hiện trạng luồng báo cáo",
        "description": "Ba nguồn dữ liệu được gom qua ổ đĩa dùng chung và bảng tính thủ công trước khi vào cơ sở dữ liệu, cổng báo cáo, email và quản lý vùng; ổ đĩa dùng chung cùng cổng báo cáo là hai nút nghẽn.",
        "reading_order": [item["id"] for item in nodes] + [item["id"] for item in edges] + ["group-collection", "group-processing", "group-dissemination"],
    })
    for item in ir["source_items"]:
        item["locator"] = item["locator"].replace("fixture:", "D-093-original-illustrative:")
    return ir
