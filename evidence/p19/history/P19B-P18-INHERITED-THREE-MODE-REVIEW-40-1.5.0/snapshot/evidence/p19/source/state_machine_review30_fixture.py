"""D-110 detailed state-machine fixture independently derived from the owner rubric."""
from semantic_fixtures import e, finalize, n


def state_machine_fixture():
    nodes = [
        n("state-entry", "initial", "Bắt đầu"),
        n("state-working", "state", "Đang soạn | Nội dung đang hoàn thiện", state="draft"),
        n("state-quality", "state", "Kiểm định | Chờ xác nhận chất lượng", state="review"),
        n("state-live", "state", "Đang hiệu lực | Sẵn sàng cho người dùng", state="live"),
        n("state-retired", "state", "Ngừng hiệu lực | Chỉ đọc · giữ lịch sử", state="retired"),
        n("state-closed", "terminal", "Đóng"),
    ]
    edges = [
        e("transition-entry", "state-entry", "state-working", "transition", label="KHỞI TẠO", order=0),
        e("transition-submit", "state-working", "state-quality", "transition", label="GỬI KIỂM", order=1),
        e("transition-confirm", "state-quality", "state-live", "transition", label="XÁC NHẬN", guard="Đạt", order=2),
        e("transition-revise", "state-quality", "state-working", "transition", label="TRẢ LẠI · CHỈNH SỬA", guard="Cần sửa", order=3),
        e("transition-retire", "state-live", "state-retired", "transition", label="THAY THẾ", order=4),
        e("transition-close", "state-retired", "state-closed", "transition", label="ĐÓNG", order=5),
    ]
    ir = finalize("state-machine", nodes=nodes, edges=edges)
    ir["diagram"].update({
        "title": "Vòng đời nội dung tri thức",
        "detail": "faithful",
        "audience": "mixed",
    })
    ir["accessibility"].update({
        "name": "State machine vòng đời nội dung tri thức",
        "description": (
            "Nội dung đi từ khởi tạo qua Đang soạn, Kiểm định và Đang hiệu lực; có thể được trả lại để chỉnh sửa, "
            "sau đó chuyển sang Ngừng hiệu lực và đóng."
        ),
        "reading_order": [item["id"] for item in nodes] + [item["id"] for item in edges],
    })
    for item in ir["source_items"]:
        item["locator"] = item["locator"].replace("fixture:", "D-110-owner-reference-structural-rubric:")
    return ir
