"""Original D-120 seven-point product-portfolio Bubble fixture."""
from semantic_fixtures import annotation, axis, finalize, series, xy_datum


def bubble_fixture():
    focal_id = "bubble-platform"
    ir = finalize(
        "scatter-plot",
        series=[
            series(
                "series-core",
                "Sản phẩm lõi",
                [
                    xy_datum(focal_id, 1200, 132, 75, "% thị phần"),
                    xy_datum("bubble-mobile", 100, 52, 45, "% thị phần"),
                    xy_datum("bubble-enterprise", 600, 96, 35, "% thị phần"),
                ],
                "%",
            ),
            series(
                "series-growth",
                "Động lực tăng trưởng",
                [
                    xy_datum("bubble-data", 400, 82, 30, "% thị phần"),
                    xy_datum("bubble-partner", 250, 61, 15, "% thị phần"),
                ],
                "%",
            ),
            series(
                "series-mature",
                "Danh mục ổn định",
                [
                    xy_datum("bubble-retail", 900, 66, 60, "% thị phần"),
                    xy_datum("bubble-labs", 300, 31, 25, "% thị phần"),
                ],
                "%",
            ),
        ],
        axes=[
            axis("axis-bubble-revenue", "x", "linear", "Doanh thu", domain_min=0, domain_max=1400, unit="tỷ đồng"),
            axis("axis-bubble-growth", "y", "linear", "Tăng trưởng lợi nhuận", domain_min=0, domain_max=160, unit="%"),
            axis("axis-bubble-share", "size", "linear", "Thị phần tương đối", domain_min=0, domain_max=80, unit="% thị phần"),
        ],
        annotations=[annotation("annotation-bubble-focal", "Nền tảng · quy mô và tăng trưởng dẫn đầu", [focal_id])],
    )
    ir["diagram"].update({
        "variant_ids": ["CAP-V20"],
        "title": "Quy mô và tăng trưởng danh mục sản phẩm",
        "detail": "faithful",
        "audience": "mixed",
    })
    ir["accessibility"].update({
        "name": "Quy mô và tăng trưởng danh mục sản phẩm",
        "description": (
            "Bubble chart gồm bảy sản phẩm trên cùng trục doanh thu 0–1.400 tỷ đồng và tăng trưởng lợi nhuận 0–160%; "
            "diện tích mỗi bong bóng, không phải bán kính, biểu diễn thị phần tương đối. Nền tảng là điểm trọng tâm."
        ),
        "reading_order": [
            "series-core", "series-growth", "series-mature",
            "axis-bubble-revenue", "axis-bubble-growth", "axis-bubble-share", "annotation-bubble-focal",
        ],
    })
    for item in ir["source_items"]:
        item["locator"] = item["locator"].replace("fixture:", "D-120-original-illustrative:")
    return ir
