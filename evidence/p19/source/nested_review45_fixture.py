"""Original D-125 five-depth enterprise configuration containment fixture."""

from semantic_fixtures import finalize, g, n


def nested_fixture():
    nodes = [
        n("artifact-enterprise-policy", "artifact", "Chính sách nền"),
        n("artifact-data-standard", "artifact", "Chuẩn dữ liệu"),
        n("artifact-metric-dictionary", "artifact", "Từ điển chỉ số"),
        n("artifact-deployment-rule", "artifact", "Quy tắc triển khai"),
        n("artifact-project-config", "artifact", "Cấu hình dự án", state="focal"),
    ]
    groups = [
        g("scope-enterprise", "CẤP 0 · TOÀN DOANH NGHIỆP", ["artifact-enterprise-policy", "scope-data"]),
        g("scope-data", "CẤP 1 · KHỐI DỮ LIỆU", ["artifact-data-standard", "scope-analytics"], parent_group_id="scope-enterprise"),
        g("scope-analytics", "CẤP 2 · MIỀN PHÂN TÍCH", ["artifact-metric-dictionary", "scope-operations"], parent_group_id="scope-data"),
        g("scope-operations", "CẤP 3 · NHÓM VẬN HÀNH", ["artifact-deployment-rule", "scope-project"], parent_group_id="scope-analytics"),
        g("scope-project", "CẤP 4 · DỰ ÁN DỰ BÁO", ["artifact-project-config"], parent_group_id="scope-operations"),
    ]
    ir = finalize("nested", nodes=nodes, groups=groups)
    ir["request_id"] = "request-nested-review45"
    ir["diagram"]["title"] = "Phạm vi cấu hình kế thừa"
    ir["selection"]["evidence"] = ["request:owner-directed detailed nested containment"]
    ir["accessibility"] = {
        "name": "Phạm vi cấu hình kế thừa",
        "description": "Năm phạm vi lồng nhau từ toàn doanh nghiệp đến dự án dự báo; cấu hình dự án kế thừa chính sách, chuẩn, chỉ số và quy tắc triển khai của bốn cấp cha.",
        "reading_order": [
            "scope-enterprise", "artifact-enterprise-policy",
            "scope-data", "artifact-data-standard",
            "scope-analytics", "artifact-metric-dictionary",
            "scope-operations", "artifact-deployment-rule",
            "scope-project", "artifact-project-config",
        ],
        "data_representation_required": False,
    }
    for source in ir["source_items"]:
        source["locator"] = source["locator"].replace("fixture:", "D-125-original-illustrative:")
    return ir
