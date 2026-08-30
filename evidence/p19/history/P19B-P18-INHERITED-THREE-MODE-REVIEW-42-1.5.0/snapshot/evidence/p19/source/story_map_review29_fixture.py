"""D-109 detailed story-map fixture derived independently from the owner rubric."""
from semantic_fixtures import finalize, g, n


def _story(item_id, label, backbone_order, story_order, release_slice, cut_status):
    return n(
        item_id,
        "story",
        label,
        story={
            "backbone_order": backbone_order,
            "story_order": story_order,
            "release_slice": release_slice,
            "cut_status": cut_status,
        },
    )


def story_map_fixture():
    nodes = [
        _story("story-keyword", "Tìm kiếm theo từ khóa | RPT-201 · 3đ", 0, 0, "MVP", "above"),
        _story("story-saved-filters", "Bộ lọc đã lưu | RPT-210 · 3đ", 0, 1, "R2", "below"),
        _story("story-natural-query", "Truy vấn ngôn ngữ tự nhiên | RPT-220 · 8đ", 0, 2, "LATER", "below"),
        _story("story-table-chart", "Bảng và một biểu đồ | RPT-202 · 5đ", 1, 0, "MVP", "above"),
        _story("story-internal-link", "Liên kết nội bộ | RPT-203 · 2đ", 2, 0, "MVP", "above"),
        _story("story-scheduled-email", "Email theo lịch | RPT-212 · 5đ", 2, 1, "R2", "below"),
        _story("story-freshness-stamp", "Dấu thời gian cập nhật | RPT-204 · 1đ", 3, 0, "MVP", "above"),
        _story("story-unit-permission", "Phân quyền theo đơn vị | RPT-214 · 3đ", 3, 1, "R2", "below"),
        _story("story-anomaly-alert", "Cảnh báo bất thường | RPT-221 · 5đ", 3, 2, "LATER", "below"),
    ]
    by_release = {
        release: [item["id"] for item in nodes if item["story"]["release_slice"] == release]
        for release in ("MVP", "R2", "LATER")
    }
    ir = finalize(
        "story-map",
        nodes=nodes,
        groups=[
            g("release-mvp", "MVP", by_release["MVP"], release_slice="MVP"),
            g("release-r2", "PHÁT HÀNH 2", by_release["R2"], release_slice="R2"),
            g("release-later", "SAU NÀY", by_release["LATER"], release_slice="LATER"),
        ],
    )
    ir["diagram"].update({
        "title": "Bản đồ câu chuyện báo cáo vận hành",
        "detail": "faithful",
        "audience": "mixed",
    })
    ir["accessibility"].update({
        "name": "Story map báo cáo vận hành theo ba lát phát hành",
        "description": (
            "Bốn hoạt động từ tìm dữ liệu đến kiểm chứng, chín story được xếp theo MVP, Phát hành 2 và Sau này. "
            "Đường cắt màu cam kết thúc MVP; story Phân quyền theo đơn vị là rủi ro cao nhất."
        ),
        "reading_order": [item["id"] for item in nodes] + ["release-mvp", "release-r2", "release-later"],
    })
    for item in ir["source_items"]:
        item["locator"] = item["locator"].replace("fixture:", "D-109-owner-reference-structural-rubric:")
    return ir
