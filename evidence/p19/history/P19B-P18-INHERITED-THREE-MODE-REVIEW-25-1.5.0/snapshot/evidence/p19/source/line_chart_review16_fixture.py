"""Original D-096 three-series, eight-week line-chart fixture."""
from semantic_fixtures import annotation, axis, datum, finalize, series


def _weekly(prefix, values):
    return [datum(f"{prefix}-w{index:02d}", f"Tuần {index}", value) for index, value in enumerate(values, 1)]


def line_chart_fixture():
    focal = _weekly("organic", [116, 132, 145, 157, 151, 176, 191, 207])
    direct = _weekly("direct", [78, 80, 86, 89, 85, 91, 94, 98])
    referral = _weekly("referral", [42, 48, 45, 56, 51, 64, 59, 72])
    ir = finalize(
        "line-chart",
        series=[
            series("series-organic-growth", "Tăng trưởng tự nhiên", focal, "lượt"),
            series("series-direct-growth", "Truy cập trực tiếp", direct, "lượt"),
            series("series-referral-growth", "Nguồn giới thiệu", referral, "lượt"),
        ],
        axes=[
            axis("axis-week", "x", "ordinal", "Tuần"),
            axis("axis-signups", "y", "linear", "Đăng ký mỗi tuần", domain_min=0, domain_max=240, unit="lượt"),
        ],
        annotations=[annotation("annotation-organic-focal", "Chuỗi tăng trưởng trọng tâm", ["series-organic-growth"])],
    )
    ir["diagram"].update({
        "title": "Xu hướng đăng ký theo tuần",
        "detail": "faithful",
        "audience": "mixed",
    })
    ir["accessibility"].update({
        "name": "Xu hướng đăng ký theo tuần",
        "description": "Biểu đồ đường so sánh ba nguồn đăng ký qua tám tuần trên cùng thang tuyến tính từ 0 đến 240 lượt; chuỗi tăng trưởng tự nhiên là trọng tâm.",
        "reading_order": [
            "series-organic-growth", "series-direct-growth", "series-referral-growth",
            "axis-week", "axis-signups", "annotation-organic-focal",
        ],
    })
    for item in ir["source_items"]:
        item["locator"] = item["locator"].replace("fixture:", "D-096-original-illustrative:")
    return ir
