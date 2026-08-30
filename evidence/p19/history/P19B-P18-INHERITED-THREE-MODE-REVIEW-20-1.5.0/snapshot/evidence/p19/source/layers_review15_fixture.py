"""Original D-095 five-layer abstraction fixture."""

from semantic_fixtures import e, finalize, lane, n


def layers_fixture():
    ir = finalize(
        "layer-stack",
        nodes=[
            n("layer-experience", "layer-item", "Trải nghiệm người dùng | cổng nghiệp vụ · ứng dụng nội bộ · báo cáo"),
            n("layer-orchestration", "control", "Điều phối quy trình | quy tắc · phê duyệt · nhật ký", state="focal"),
            n("layer-services", "layer-item", "Dịch vụ nghiệp vụ | hồ sơ · tác vụ · thông báo"),
            n("layer-data-platform", "layer-item", "Nền tảng dữ liệu | API · đồng bộ · phân quyền"),
            n("layer-infrastructure", "layer-item", "Hạ tầng vận hành | compute · mạng · lưu trữ"),
        ],
        edges=[
            e("enforce-experience", "layer-orchestration", "layer-experience", "enforcement"),
            e("enforce-services", "layer-orchestration", "layer-services", "enforcement"),
            e("depend-data", "layer-services", "layer-data-platform", "dependency"),
            e("depend-infrastructure", "layer-data-platform", "layer-infrastructure", "dependency"),
        ],
        lanes=[
            lane("level-5", "L5", ["layer-experience"], 0),
            lane("level-4", "L4", ["layer-orchestration"], 1),
            lane("level-3", "L3", ["layer-services"], 2),
            lane("level-2", "L2", ["layer-data-platform"], 3),
            lane("level-1", "L1", ["layer-infrastructure"], 4),
        ],
    )
    ir["request_id"] = "request-layers-review15"
    ir["diagram"]["title"] = "Các lớp của nền tảng nghiệp vụ"
    ir["selection"]["evidence"] = ["request:owner-directed layers presentation variant"]
    ir["accessibility"] = {
        "name": "Các lớp của nền tảng nghiệp vụ",
        "description": "Năm lớp từ hạ tầng vận hành đến trải nghiệm người dùng; lớp điều phối quy trình là trọng tâm.",
        "reading_order": [
            "level-5", "layer-experience", "level-4", "layer-orchestration",
            "level-3", "layer-services", "level-2", "layer-data-platform",
            "level-1", "layer-infrastructure", "enforce-experience",
            "enforce-services", "depend-data", "depend-infrastructure",
        ],
        "data_representation_required": False,
    }
    for source in ir["source_items"]:
        source["locator"] = source["locator"].replace("fixture:", "D-095-original-illustrative:")
    return ir

