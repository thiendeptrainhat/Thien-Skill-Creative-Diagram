"""Original D-113 twelve-team deployment-performance scatter fixture."""
from semantic_fixtures import annotation, axis, datum, finalize, series


def scatter_chart_fixture():
    values = (
        ("team-01", 2, 20),
        ("team-02", 4, 18),
        ("team-03", 4, 16),
        ("team-04", 6, 14),
        ("team-05", 8, 12),
        ("team-06", 8, 10),
        ("team-07", 10, 8),
        ("team-08", 12, 10),
        ("team-09", 12, 6),
        ("team-10", 16, 4),
        ("team-platform", 18, 3),
        ("team-11", 20, 2),
    )
    points = [datum(identifier, deploys, lead_time) for identifier, deploys, lead_time in values]
    ir = finalize(
        "scatter-plot",
        series=[series("series-team-performance", "Nhóm kỹ thuật", points, "ngày")],
        axes=[
            axis("axis-deploys", "x", "linear", "Số lần triển khai mỗi tuần", domain_min=0, domain_max=20, unit="lần/tuần"),
            axis("axis-lead-time", "y", "linear", "Lead time", domain_min=0, domain_max=24, unit="ngày"),
        ],
        annotations=[annotation("annotation-platform-focal", "Nhóm nền tảng · hiệu suất tốt nhất", ["team-platform"])],
    )
    ir["diagram"].update({
        "title": "Tần suất triển khai và lead time theo nhóm",
        "detail": "faithful",
        "audience": "mixed",
    })
    ir["accessibility"].update({
        "name": "Tần suất triển khai và lead time theo nhóm",
        "description": "Biểu đồ phân tán của mười hai nhóm kỹ thuật trên trục triển khai mỗi tuần từ 0 đến 20 và lead time từ 0 đến 24 ngày; nhóm nền tảng ở 18 lần và 3 ngày là điểm nhấn, kèm đường xu hướng tuyến tính giảm.",
        "reading_order": ["series-team-performance", "axis-deploys", "axis-lead-time", "annotation-platform-focal"],
    })
    for item in ir["source_items"]:
        item["locator"] = item["locator"].replace("fixture:", "D-113-original-illustrative:")
    return ir
