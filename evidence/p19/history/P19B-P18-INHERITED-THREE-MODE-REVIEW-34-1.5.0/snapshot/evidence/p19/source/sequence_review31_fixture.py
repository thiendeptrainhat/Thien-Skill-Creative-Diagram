"""D-111 detailed sequence fixture independently derived from the owner rubric."""
from semantic_fixtures import e, finalize, n


def sequence_fixture():
    nodes = [
        n("participant-editor", "actor", "Biên tập viên | Trình duyệt", state="external"),
        n("participant-edge", "system", "Cổng phân phối | cache · định tuyến", state="edge"),
        n("participant-origin", "system", "Kho tri thức | dựng trang · truy xuất", state="focal"),
        n("participant-metrics", "participant", "Đo lường | sự kiện · bất đồng bộ", state="async"),
    ]
    edges = [
        e("message-open", "participant-editor", "participant-edge", "request", label="MỞ / NỘI-DUNG/:ID", order=0),
        e("message-origin", "participant-edge", "participant-origin", "request", label="CHƯA CÓ CACHE · TRUY XUẤT", order=1),
        e("message-render", "participant-origin", "participant-origin", "message", label="DỰNG TRANG", order=2),
        e("message-html", "participant-origin", "participant-edge", "return", label="200 · HTML + TTL", order=3),
        e("message-cached", "participant-edge", "participant-editor", "response", label="200 · PHẢN HỒI ĐÃ CACHE", order=4),
        e("message-view", "participant-editor", "participant-metrics", "async", label="GHI NHẬN LƯỢT XEM", order=5),
    ]
    ir = finalize("sequence", nodes=nodes, edges=edges)
    ir["diagram"].update({
        "title": "Luồng phân phối nội dung",
        "detail": "faithful",
        "audience": "mixed",
    })
    ir["accessibility"].update({
        "name": "Sequence luồng phân phối nội dung",
        "description": (
            "Biên tập viên gọi cổng phân phối; khi cache chưa có, cổng gọi kho tri thức, kho tự dựng trang rồi trả HTML. "
            "Cổng trả phản hồi đã cache và trình duyệt gửi sự kiện lượt xem bất đồng bộ sang hệ đo lường."
        ),
        "reading_order": [item["id"] for item in nodes] + [item["id"] for item in edges],
    })
    for item in ir["source_items"]:
        item["locator"] = item["locator"].replace("fixture:", "D-111-owner-reference-structural-rubric:")
    return ir
