"""Original D-099 Wardley-map fixture for a mapped assistant value chain."""
from semantic_fixtures import annotation, axis, e, finalize, n


COMPONENTS = (
    ("component-answer", "Trả lời trong luồng công việc", 0.34, 0.90),
    ("component-chat", "Giao diện hội thoại", 0.62, 0.78),
    ("component-orchestrator", "Điều phối tác vụ", 0.34, 0.68),
    ("component-evaluation", "Bộ kiểm thử", 0.13, 0.55),
    ("component-knowledge", "Kho tri thức", 0.63, 0.43),
    ("component-model-api", "API mô hình", 0.76, 0.32),
    ("component-compute", "Cụm tính toán", 0.89, 0.18),
    ("component-object-store", "Kho đối tượng", 0.89, 0.07),
)

DEPENDENCIES = (
    ("dependency-answer-chat", "component-answer", "component-chat"),
    ("dependency-orchestrator-chat", "component-orchestrator", "component-chat"),
    ("dependency-evaluation-chat", "component-evaluation", "component-chat"),
    ("dependency-evaluation-model", "component-evaluation", "component-model-api"),
    ("dependency-orchestrator-knowledge", "component-orchestrator", "component-knowledge"),
    ("dependency-orchestrator-model", "component-orchestrator", "component-model-api"),
    ("dependency-knowledge-model", "component-knowledge", "component-model-api"),
    ("dependency-model-compute", "component-model-api", "component-compute"),
    ("dependency-model-store", "component-model-api", "component-object-store"),
)


def wardley_map_fixture():
    ir = finalize(
        "wardley-map",
        nodes=[
            n(
                item_id,
                "component",
                label,
                strategy={"evolution": evolution, "value_chain_position": visibility},
            )
            for item_id, label, evolution, visibility in COMPONENTS
        ],
        edges=[e(item_id, source, target, "dependency") for item_id, source, target in DEPENDENCIES],
        axes=[
            axis("wardley-evolution", "x", "linear", "Mức độ tiến hóa", domain_min=0, domain_max=1),
            axis("wardley-value", "y", "linear", "Mức độ nhìn thấy", domain_min=0, domain_max=1),
        ],
        annotations=[
            annotation(
                "annotation-evolving-orchestrator",
                "Điều phối tác vụ đang tiến hóa về phía sản phẩm",
                ["component-orchestrator"],
            )
        ],
    )
    ir["diagram"].update({
        "title": "Bản đồ tiến hóa của trợ lý công việc",
        "detail": "faithful",
        "audience": "mixed",
    })
    ir["accessibility"].update({
        "name": "Bản đồ tiến hóa của trợ lý công việc",
        "description": (
            "Wardley map gồm tám thành phần đặt theo mức độ nhìn thấy và tiến hóa; "
            "điều phối tác vụ là thành phần duy nhất đang dịch chuyển về phía sản phẩm."
        ),
        "reading_order": [
            *(item_id for item_id, *_ in COMPONENTS),
            *(item_id for item_id, *_ in DEPENDENCIES),
            "wardley-value",
            "wardley-evolution",
            "annotation-evolving-orchestrator",
        ],
    })
    for item in ir["source_items"]:
        item["locator"] = item["locator"].replace("fixture:", "D-099-original-illustrative:")
    return ir
