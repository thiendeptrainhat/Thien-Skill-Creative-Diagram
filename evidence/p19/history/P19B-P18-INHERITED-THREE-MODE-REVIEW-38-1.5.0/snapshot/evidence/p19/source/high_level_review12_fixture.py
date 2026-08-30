"""Original D-092 detailed high-level data-platform overview fixture."""
from semantic_fixtures import annotation, e, finalize, g, n


def high_level_fixture():
    stage_nodes = [
        n("source-portal", "capability", "Cổng trực tuyến | Biểu mẫu · khảo sát"),
        n("source-files", "capability", "Tệp định kỳ | CSV · đối soát"),
        n("source-operational", "capability", "CSDL vận hành | CDC · giao dịch"),
        n("source-legacy", "capability", "Hệ thống cũ | Dữ liệu chuyên ngành"),
        n("stage-collect", "stage", "Cổng thu nhận | Batch · stream · kiểm tra"),
        n("stage-query", "stage", "Lớp truy vấn | SQL · data virtualization"),
        n("stage-store", "stage", "Kho đối tượng | Phiên bản · open format"),
        n("stage-model", "stage", "Mô hình dữ liệu | Notebook · Python · R"),
        n("stage-serve", "stage", "Không gian BI | Dashboard · báo cáo"),
        n("control-orchestration", "cross-cutting-control", "Điều phối quy trình | Lịch chạy · retry · lineage"),
        n("control-identity", "cross-cutting-control", "Quản lý định danh | SSO · service identity · policy"),
    ]
    edges = [
        e("flow-portal-collect", "source-portal", "stage-collect", "progression", order=1),
        e("flow-files-collect", "source-files", "stage-collect", "progression", order=2),
        e("flow-operational-collect", "source-operational", "stage-collect", "progression", order=3),
        e("flow-legacy-collect", "source-legacy", "stage-collect", "progression", order=4),
        e("flow-collect-query", "stage-collect", "stage-query", "progression", order=5),
        e("flow-collect-store", "stage-collect", "stage-store", "progression", order=6),
        e("flow-store-query", "stage-store", "stage-query", "progression", order=7),
        e("flow-query-model", "stage-query", "stage-model", "progression", order=8),
        e("flow-store-model", "stage-store", "stage-model", "progression", order=9),
        e("flow-model-serve", "stage-model", "stage-serve", "progression", order=10),
        e("trigger-query", "control-orchestration", "stage-query", "control", order=11),
        e("trigger-model", "control-orchestration", "stage-model", "control", order=12),
        e("trigger-serve", "control-orchestration", "stage-serve", "control", order=13),
    ]
    ir = finalize(
        "high-level", nodes=stage_nodes, edges=edges,
        groups=[
            g("boundary-sources", "NGUỒN DỮ LIỆU", ["source-portal", "source-files", "source-operational", "source-legacy"]),
            g("boundary-platform", "NỀN TẢNG DỮ LIỆU", ["stage-collect", "stage-query", "stage-store", "stage-model", "stage-serve", "control-orchestration"]),
        ],
        annotations=[
            annotation("annotation-orchestration", "Điều phối xuyên suốt", ["stage-query", "stage-model", "stage-serve"]),
            annotation("annotation-identity", "Định danh áp dụng toàn nền tảng", ["stage-collect", "stage-query", "stage-store", "stage-model", "stage-serve"]),
        ],
    )
    ir["diagram"].update({"title":"Tổng quan nền tảng dữ liệu", "detail":"faithful", "audience":"mixed"})
    ir["accessibility"].update({
        "name":"Tổng quan nền tảng dữ liệu",
        "description":"Bốn nguồn đi qua cổng thu nhận, kho đối tượng, lớp truy vấn và mô hình dữ liệu tới BI; điều phối và định danh là kiểm soát xuyên suốt.",
        "reading_order":[item["id"] for item in stage_nodes] + [item["id"] for item in edges] + ["boundary-sources", "boundary-platform", "annotation-orchestration", "annotation-identity"],
    })
    for item in ir["source_items"]: item["locator"] = item["locator"].replace("fixture:", "D-092-original-illustrative:")
    return ir
