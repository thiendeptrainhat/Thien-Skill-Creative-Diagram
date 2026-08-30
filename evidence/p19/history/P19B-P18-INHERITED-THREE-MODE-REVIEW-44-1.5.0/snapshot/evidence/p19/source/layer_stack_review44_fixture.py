"""Original D-124 detailed enterprise AI layer-stack fixture."""

from semantic_fixtures import e, finalize, g, lane, n


def layer_stack_fixture():
    experience = [
        n("module-copilot", "layer-item", "Trợ lý nghiệp vụ"),
        n("module-analysis", "layer-item", "Không gian phân tích"),
        n("module-operations", "layer-item", "Cổng vận hành"),
        n("module-reporting", "layer-item", "Báo cáo điều hành"),
    ]
    orchestration = [
        n("module-memory", "control", "Bộ nhớ ngữ cảnh"),
        n("module-planning", "control", "Lập kế hoạch"),
        n("module-tools", "control", "Điều phối công cụ", state="focal"),
        n("module-approval", "control", "Luồng phê duyệt"),
        n("module-observability", "control", "Giám sát tác vụ"),
    ]
    intelligence = [
        n("module-language", "layer-item", "Mô hình ngôn ngữ"),
        n("module-vision", "layer-item", "Thị giác"),
        n("module-forecast", "layer-item", "Dự báo"),
        n("module-vector", "layer-item", "Kho vector"),
        n("module-knowledge-graph", "layer-item", "Đồ thị tri thức"),
        n("module-retrieval", "layer-item", "Truy xuất ngữ nghĩa"),
    ]
    ml_platform = [
        n("module-training", "layer-item", "Huấn luyện"),
        n("module-evaluation", "layer-item", "Đánh giá"),
        n("module-serving", "layer-item", "Phục vụ mô hình"),
        n("module-quality", "layer-item", "Quan sát chất lượng"),
    ]
    infrastructure = [
        n("module-compute", "layer-item", "Tính toán tăng tốc"),
        n("module-storage", "layer-item", "Lưu trữ"),
        n("module-network", "layer-item", "Mạng riêng"),
        n("module-identity", "layer-item", "Quản lý định danh"),
    ]
    nodes = experience + orchestration + intelligence + ml_platform + infrastructure
    ir = finalize(
        "layer-stack",
        nodes=nodes,
        edges=[
            e("dependency-experience-agent", "module-copilot", "module-tools", "dependency"),
            e("dependency-agent-intelligence", "module-tools", "module-language", "dependency"),
            e("dependency-intelligence-ml", "module-language", "module-serving", "dependency"),
            e("dependency-ml-infrastructure", "module-serving", "module-compute", "dependency"),
        ],
        groups=[
            g("domain-models", "Mô hình", ["module-language", "module-vision", "module-forecast"]),
            g("domain-knowledge", "Dữ liệu & tri thức", ["module-vector", "module-knowledge-graph", "module-retrieval"]),
        ],
        lanes=[
            lane("stack-level-5", "L5 | Trải nghiệm | giao diện và quyết định nghiệp vụ", [item["id"] for item in experience], 0),
            lane("stack-level-4", "L4 | Tác nhân & điều phối | công cụ · bộ nhớ · kiểm soát", [item["id"] for item in orchestration], 1),
            lane("stack-level-3", "L3 | Năng lực thông minh | mô hình kết hợp tri thức", [item["id"] for item in intelligence], 2),
            lane("stack-level-2", "L2 | Nền tảng ML | vòng đời mô hình có kiểm chứng", [item["id"] for item in ml_platform], 3),
            lane("stack-level-1", "L1 | Hạ tầng vận hành | compute · storage · network · identity", [item["id"] for item in infrastructure], 4),
        ],
    )
    ir["request_id"] = "request-layer-stack-review44"
    ir["diagram"]["title"] = "Kiến trúc nền tảng AI doanh nghiệp"
    ir["selection"]["evidence"] = ["request:owner-directed detailed layer-stack"]
    ir["accessibility"] = {
        "name": "Kiến trúc nền tảng AI doanh nghiệp",
        "description": "Năm tầng từ trải nghiệm đến hạ tầng; tầng tác nhân và điều phối là trọng tâm, tầng năng lực thông minh chia thành miền mô hình và dữ liệu tri thức.",
        "reading_order": [
            "stack-level-5", *[item["id"] for item in experience],
            "stack-level-4", *[item["id"] for item in orchestration],
            "stack-level-3", "domain-models", "domain-knowledge", *[item["id"] for item in intelligence],
            "stack-level-2", *[item["id"] for item in ml_platform],
            "stack-level-1", *[item["id"] for item in infrastructure],
            "dependency-experience-agent", "dependency-agent-intelligence",
            "dependency-intelligence-ml", "dependency-ml-infrastructure",
        ],
        "data_representation_required": False,
    }
    for source in ir["source_items"]:
        source["locator"] = source["locator"].replace("fixture:", "D-124-original-illustrative:")
    return ir
