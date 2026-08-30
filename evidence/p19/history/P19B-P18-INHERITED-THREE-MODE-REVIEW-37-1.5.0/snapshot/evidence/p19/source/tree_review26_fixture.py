"""D-106 detailed three-tier tree fixture with centered parent spans."""
from semantic_fixtures import e, finalize, n


def tree_fixture():
    nodes = [
        n("capability-product", "root", "Năng lực sản phẩm"),
        n("branch-experience", "branch", "Trải nghiệm"),
        n("branch-operations", "branch", "Vận hành"),
        n("branch-insight", "branch", "Khám phá"),
        n("leaf-interface", "leaf", "Giao diện"),
        n("leaf-content", "leaf", "Nội dung"),
        n("leaf-data", "leaf", "Dữ liệu"),
        n("leaf-platform", "leaf", "Nền tảng"),
        n("leaf-research", "leaf", "Nghiên cứu"),
    ]
    edges = [
        e("parent-product-experience", "capability-product", "branch-experience", "parent", directed=False),
        e("parent-product-operations", "capability-product", "branch-operations", "parent", directed=False),
        e("parent-product-insight", "capability-product", "branch-insight", "parent", directed=False),
        e("parent-experience-interface", "branch-experience", "leaf-interface", "parent", directed=False),
        e("parent-experience-content", "branch-experience", "leaf-content", "parent", directed=False),
        e("parent-operations-data", "branch-operations", "leaf-data", "parent", directed=False),
        e("parent-operations-platform", "branch-operations", "leaf-platform", "parent", directed=False),
        e("parent-insight-research", "branch-insight", "leaf-research", "parent", directed=False),
    ]
    ir = finalize("tree", nodes=nodes, edges=edges)
    ir["diagram"].update({
        "title": "Cây năng lực sản phẩm",
        "detail": "faithful",
        "audience": "mixed",
    })
    ir["accessibility"].update({
        "name": "Cây năng lực sản phẩm ba tầng",
        "description": (
            "Một root ở giữa phân nhánh thành ba nhóm năng lực; mỗi parent được đặt đúng giữa span của các child, "
            "với hai leaf cân đối dưới Trải nghiệm, hai leaf cân đối dưới Vận hành và một leaf thẳng tâm dưới Khám phá."
        ),
        "reading_order": [item["id"] for item in nodes] + [item["id"] for item in edges],
    })
    for item in ir["source_items"]:
        item["locator"] = item["locator"].replace("fixture:", "D-106-owner-reference-structural-rubric:")
    return ir
