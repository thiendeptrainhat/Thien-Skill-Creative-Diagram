"""Original D-094 detailed Kanban fixture."""
from semantic_fixtures import annotation, finalize, g, n


def _item(item_id, label, column_order, item_order, state="default"):
    return n(
        item_id, "work-item", label, state=state,
        work={
            "column_order": column_order,
            "item_order": item_order,
            "blocked": state == "blocked",
        },
    )


def kanban_fixture():
    nodes = [
        _item("work-api-limit", "Tối ưu hạn mức API | DEV-214 · An", 0, 0),
        _item("work-infra-module", "Chuẩn hóa module hạ tầng | DEV-219 · Bình", 0, 1),
        _item("work-onboarding-docs", "Cập nhật tài liệu tiếp nhận | DEV-226 · Chi", 0, 2),
        _item("work-data-cluster", "Nâng cấp cụm dữ liệu | OPS-138 · Dũng", 1, 0, "blocked"),
        _item("work-node-migration", "Di chuyển nhóm máy chủ | OPS-144 · An", 1, 1),
        _item("work-key-rotation", "Xoay vòng khóa truy cập | SEC-153 · Bình", 1, 2),
        _item("work-observability", "Bổ sung dashboard giám sát | OBS-167 · Hà", 1, 3),
        _item("work-flag-cleanup", "Dọn dẹp cờ tính năng | APP-181 · Chi", 2, 0),
        _item("work-partner-login", "Tích hợp đăng nhập đối tác | IAM-190 · Dũng", 2, 1, "waiting-external"),
        _item("work-log-policy", "Chính sách lưu log | GOV-096 · Hà", 3, 0, "done"),
        _item("work-ci-cache", "Tối ưu bộ nhớ đệm CI | DEV-102 · Lan", 3, 1, "done"),
    ]
    ir = finalize(
        "kanban",
        nodes=nodes,
        groups=[
            g("column-backlog", "TỒN ĐỌNG", [item["id"] for item in nodes[:3]]),
            g("column-progress", "ĐANG THỰC HIỆN", [item["id"] for item in nodes[3:7]]),
            g("column-review", "RÀ SOÁT", [item["id"] for item in nodes[7:9]], wip_limit=3),
            g("column-done", "HOÀN TẤT", [item["id"] for item in nodes[9:]]),
        ],
        annotations=[annotation("annotation-progress-wip", "Giới hạn WIP: 3", ["column-progress"])],
    )
    ir["diagram"].update({"title": "Bảng công việc vận hành", "detail": "faithful", "audience": "mixed"})
    ir["accessibility"].update({
        "name": "Bảng Kanban công việc vận hành",
        "description": "Bốn cột gồm Tồn đọng, Đang thực hiện, Rà soát và Hoàn tất. Cột Đang thực hiện có bốn việc trên giới hạn ba; một việc bị chặn và một việc đang chờ bên ngoài.",
        "reading_order": [item["id"] for item in nodes] + [
            "column-backlog", "column-progress", "column-review", "column-done",
            "annotation-progress-wip",
        ],
    })
    for item in ir["source_items"]:
        item["locator"] = item["locator"].replace("fixture:", "D-094-original-illustrative:")
    return ir
