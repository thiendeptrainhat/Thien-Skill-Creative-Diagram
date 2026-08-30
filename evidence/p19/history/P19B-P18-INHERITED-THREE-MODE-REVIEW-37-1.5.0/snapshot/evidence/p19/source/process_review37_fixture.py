"""D-117 detailed process fixture with the approved P-18-derived visual grammar."""
from semantic_fixtures import e, finalize, n


def process_fixture():
    nodes = [
        n("process-start", "start", "Tiếp nhận yêu cầu"),
        n("process-check", "activity", "Kiểm tra thông tin"),
        n("decision-complete", "decision", "Hồ sơ đầy đủ?"),
        n("document-supplement", "artifact", "Phiếu yêu cầu bổ sung"),
        n("process-return", "terminal", "Trả lại người gửi"),
        n("decision-sensitive", "decision", "Dữ liệu nhạy cảm?"),
        n("process-standard", "activity", "Duyệt quyền chuẩn"),
        n("process-control", "activity", "Đánh giá kiểm soát"),
        n("document-approval-pack", "artifact", "Bộ hồ sơ phê duyệt", state="focal"),
        n("process-log", "activity", "Ghi nhận và cấp quyền"),
        n("process-complete", "terminal", "Hoàn tất"),
    ]
    edges = [
        e("flow-start-check", "process-start", "process-check", "flow", order=1),
        e("flow-check-complete", "process-check", "decision-complete", "flow", order=2),
        e("flow-incomplete-document", "decision-complete", "document-supplement", "flow", order=3, guard="CHƯA ĐỦ"),
        e("flow-document-return", "document-supplement", "process-return", "flow", order=4),
        e("flow-complete-sensitive", "decision-complete", "decision-sensitive", "flow", order=5, guard="ĐẦY ĐỦ"),
        e("flow-standard-review", "decision-sensitive", "process-standard", "flow", order=6, guard="KHÔNG"),
        e("flow-sensitive-control", "decision-sensitive", "process-control", "flow", order=7, guard="CÓ"),
        e("flow-standard-pack", "process-standard", "document-approval-pack", "flow", order=8),
        e("flow-control-pack", "process-control", "document-approval-pack", "flow", order=9),
        e("flow-pack-log", "document-approval-pack", "process-log", "flow", order=10),
        e("flow-log-complete", "process-log", "process-complete", "flow", order=11),
    ]
    ir = finalize("process", nodes=nodes, edges=edges)
    ir["diagram"].update({
        "title": "Quy trình phê duyệt quyền truy cập dữ liệu",
        "detail": "faithful",
        "audience": "mixed",
    })
    ir["accessibility"].update({
        "name": "Quy trình phê duyệt quyền truy cập dữ liệu",
        "description": (
            "Quy trình độc lập gồm ba terminator, bốn bước xử lý, hai quyết định, "
            "một tài liệu đơn và một bộ nhiều tài liệu; các nhánh được gắn nhãn trực tiếp."
        ),
        "reading_order": [item["id"] for item in nodes] + [item["id"] for item in edges],
    })
    for item in ir["source_items"]:
        item["locator"] = item["locator"].replace("fixture:", "D-117-original-illustrative:")
    return ir
