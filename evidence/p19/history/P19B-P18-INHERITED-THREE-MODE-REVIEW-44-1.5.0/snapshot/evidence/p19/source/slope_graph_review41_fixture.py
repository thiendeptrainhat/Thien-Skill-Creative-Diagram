"""Original D-121 seven-series, two-state slope-graph fixture."""
from semantic_fixtures import annotation, axis, datum, finalize, series


def slope_graph_fixture():
    observations = (
        ("platform", "Nền tảng", 52, 80),
        ("data", "Dữ liệu", 68, 72),
        ("mobile", "Di động", 60, 58),
        ("partner", "Đối tác", 78, 34),
        ("enterprise", "Doanh nghiệp", 44, 62),
        ("retail", "Bán lẻ", 36, 46),
        ("labs", "Thử nghiệm", 28, 40),
    )
    series_items = []
    for slug, label, before, after in observations:
        series_items.append(
            series(
                f"series-{slug}",
                label,
                [
                    datum(f"{slug}-baseline", "Ban đầu", before),
                    datum(f"{slug}-current", "Hiện tại", after),
                ],
                "%",
            )
        )
    ir = finalize(
        "line-chart",
        series=series_items,
        axes=[
            axis("axis-slope-state", "x", "ordinal", "Kỳ đánh giá"),
            axis("axis-slope-value", "y", "linear", "Tỷ lệ hoàn thành", domain_min=0, domain_max=100, unit="%"),
        ],
        annotations=[annotation("annotation-slope-focal", "Nền tảng cải thiện mạnh nhất và dẫn đầu ở kỳ hiện tại", ["series-platform"])],
    )
    ir["diagram"].update({
        "variant_ids": ["CAP-V18"],
        "title": "Dịch chuyển hiệu suất giữa hai kỳ",
        "detail": "faithful",
        "audience": "mixed",
    })
    ir["accessibility"].update({
        "name": "Dịch chuyển hiệu suất giữa hai kỳ",
        "description": (
            "Slope graph so sánh bảy nhóm giữa đúng hai kỳ trên cùng thang 0–100 phần trăm. "
            "Nhãn trực tiếp ở hai đầu cho biết giá trị chính xác; độ dốc thể hiện tăng hoặc giảm, "
            "và các giao cắt thể hiện thay đổi thứ hạng. Nền tảng là chuỗi trọng tâm."
        ),
        "reading_order": [
            *(f"series-{slug}" for slug, *_ in observations),
            "axis-slope-state", "axis-slope-value", "annotation-slope-focal",
        ],
    })
    for item in ir["source_items"]:
        item["locator"] = item["locator"].replace("fixture:", "D-121-original-illustrative:")
    return ir
