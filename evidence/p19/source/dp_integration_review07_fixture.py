"""Original D-087 detailed integration-topology fixture."""
from semantic_fixtures import finalize, n, e, g


def dp_integration_fixture():
    ir = finalize(
        "dp-integration",
        nodes=[
            n("source-crm", "source", "CRM | Hồ sơ khách hàng"),
            n("source-pos", "source", "POS batch | Lô giao dịch hằng ngày"),
            n("source-events", "source", "Event bus | Sự kiện gần thời gian thực"),
            n("platform-orchestrator", "platform-service", "Điều phối | Lịch chạy · retry · lineage"),
            n("platform-object-store", "store", "Kho đối tượng | Dữ liệu phiên bản"),
            n("platform-query", "platform-service", "Dịch vụ truy vấn | Truy vấn dữ liệu liên hợp"),
            n("consumer-bi", "consumer", "BI workspace | Dashboard · báo cáo"),
            n("consumer-notebook", "consumer", "Notebook | Python · khám phá"),
            n("consumer-partner", "consumer", "Partner API | Sản phẩm dữ liệu chọn lọc"),
            n("service-identity", "platform-service", "Dịch vụ định danh | SSO · service identity · policy"),
            n("service-observability", "platform-service", "Quan sát tập trung | Sự kiện · audit · retention"),
        ],
        edges=[
            e("flow-crm-store", "source-crm", "platform-object-store", "integration", label="REST", order=1),
            e("flow-pos-store", "source-pos", "platform-object-store", "integration", label="CSV", order=2),
            e("flow-events-store", "source-events", "platform-object-store", "integration", label="EVENTS", order=3),
            e("control-orchestrator-store", "platform-orchestrator", "platform-object-store", "integration", label="SCHEDULE", order=4),
            e("control-orchestrator-query", "platform-orchestrator", "platform-query", "integration", label="LINEAGE", order=5),
            e("flow-store-query", "platform-object-store", "platform-query", "integration", label="READ", order=6),
            e("flow-query-bi", "platform-query", "consumer-bi", "integration", label="JDBC", order=7),
            e("flow-query-notebook", "platform-query", "consumer-notebook", "integration", label="KERNEL", order=8),
            e("flow-query-partner", "platform-query", "consumer-partner", "integration", label="HTTPS", order=9),
            e("service-identity-store", "service-identity", "platform-object-store", "integration", label="AUTH", order=10),
            e("service-identity-query", "service-identity", "platform-query", "integration", label="AUTH", order=11),
        ],
        groups=[g("boundary-data-platform", "NỀN TẢNG DỮ LIỆU", ["platform-orchestrator", "platform-object-store", "platform-query"])],
    )
    ir["diagram"].update({
        "title": "Nền tảng tích hợp dữ liệu",
        "detail": "faithful",
        "audience": "mixed",
    })
    ir["accessibility"].update({
        "name": "Nền tảng tích hợp dữ liệu",
        "description": "Ba nguồn dữ liệu đi qua một nền tảng gồm điều phối, kho đối tượng và dịch vụ truy vấn tới ba nhóm tiêu thụ; định danh và quan sát là dịch vụ dùng chung.",
        "reading_order": [
            "source-crm", "source-pos", "source-events", "boundary-data-platform",
            "platform-orchestrator", "platform-object-store", "platform-query",
            "consumer-bi", "consumer-notebook", "consumer-partner",
            "service-identity", "service-observability",
        ] + [edge_id for edge_id in (
            "flow-crm-store", "flow-pos-store", "flow-events-store",
            "control-orchestrator-store", "control-orchestrator-query", "flow-store-query",
            "flow-query-bi", "flow-query-notebook", "flow-query-partner",
            "service-identity-store", "service-identity-query",
        )],
    })
    for item in ir["source_items"]:
        item["locator"] = item["locator"].replace("fixture:", "D-087-original-illustrative:")
    return ir
