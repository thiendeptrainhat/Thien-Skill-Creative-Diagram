"""Original D-114 five-axis, four-profile radar fixture."""
from semantic_fixtures import annotation, axis, datum, finalize, series


CRITERIA = (
    ("small-files", "Xử lý tệp nhỏ"),
    ("large-reads", "Đọc đối tượng lớn"),
    ("write-throughput", "Thông lượng ghi"),
    ("operations", "Vận hành đơn giản"),
    ("open-tables", "Tích hợp bảng mở"),
)


def _profile(prefix, values):
    return [datum(f"{prefix}-{criterion_id}", label, value) for (criterion_id, label), value in zip(CRITERIA, values)]


def radar_fixture():
    focal_id = "series-internal-platform"
    ir = finalize(
        "radar",
        series=[
            series(focal_id, "Nền tảng nội bộ", _profile("internal", (9, 8, 9, 9, 8)), "điểm"),
            series("series-managed-service", "Dịch vụ quản lý", _profile("managed", (6, 9, 8, 6, 8)), "điểm"),
            series("series-open-stack", "Ngăn xếp mở", _profile("open", (7, 7, 6, 5, 6)), "điểm"),
            series("series-cloud-suite", "Bộ công cụ đám mây", _profile("cloud", (6, 8, 7, 6, 7)), "điểm"),
        ],
        axes=[
            axis(f"axis-{criterion_id}", "radial", "linear", label, domain_min=0, domain_max=10, unit="điểm")
            for criterion_id, label in CRITERIA
        ],
        annotations=[annotation("annotation-recommended", "Phương án được khuyến nghị", [focal_id])],
    )
    ir["diagram"].update({
        "title": "So sánh năng lực nền tảng dữ liệu",
        "detail": "faithful",
        "audience": "mixed",
    })
    ir["accessibility"].update({
        "name": "So sánh năng lực nền tảng dữ liệu",
        "description": (
            "Biểu đồ radar so sánh bốn phương án trên năm tiêu chí dùng chung thang điểm tuyến tính 0–10; "
            "nền tảng nội bộ là phương án trọng tâm và được phân biệt đồng thời bằng màu san hô, nét liền và marker tròn."
        ),
        "reading_order": [
            focal_id, "series-managed-service", "series-open-stack", "series-cloud-suite",
            *(f"axis-{criterion_id}" for criterion_id, _ in CRITERIA), "annotation-recommended",
        ],
    })
    for item in ir["source_items"]:
        item["locator"] = item["locator"].replace("fixture:", "D-114-original-illustrative:")
    return ir
