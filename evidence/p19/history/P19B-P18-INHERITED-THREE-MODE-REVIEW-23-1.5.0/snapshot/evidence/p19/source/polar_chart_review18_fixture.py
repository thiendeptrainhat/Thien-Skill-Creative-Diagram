"""Original D-098 eight-window radial-spoke polar-chart fixture."""
from semantic_fixtures import annotation, axis, datum, finalize, series


WINDOWS = (
    ("request-00-03", "00–03", 28),
    ("request-03-06", "03–06", 16),
    ("request-06-09", "06–09", 34),
    ("request-09-12", "09–12", 61),
    ("request-12-15", "12–15", 100),
    ("request-15-18", "15–18", 84),
    ("request-18-21", "18–21", 72),
    ("request-21-24", "21–24", 47),
)


def polar_chart_fixture():
    values = [datum(item_id, window, value) for item_id, window, value in WINDOWS]
    ir = finalize(
        "polar-chart",
        series=[series("series-request-intensity", "Cường độ truy cập", values, "%")],
        axes=[
            axis("axis-utc-window", "angular", "categorical", "Cửa sổ UTC"),
            axis(
                "axis-normalized-demand", "radial", "linear",
                "Tỷ lệ so với đỉnh ngày", domain_min=0, domain_max=100, unit="%",
            ),
        ],
        annotations=[
            annotation("annotation-peak-window", "Cửa sổ đạt đỉnh ngày", ["request-12-15"]),
        ],
    )
    ir["diagram"].update({
        "title": "Cường độ truy cập theo cửa sổ UTC",
        "detail": "faithful",
        "audience": "mixed",
    })
    ir["accessibility"].update({
        "name": "Cường độ truy cập theo cửa sổ UTC",
        "description": (
            "Biểu đồ cực dùng tám tia chung tâm để biểu diễn cường độ truy cập theo tám cửa sổ UTC, "
            "chuẩn hóa từ 0 đến 100 phần trăm; cửa sổ 12–15 là đỉnh duy nhất."
        ),
        "reading_order": [
            "series-request-intensity", "axis-utc-window", "axis-normalized-demand",
            "annotation-peak-window",
        ],
    })
    for item in ir["source_items"]:
        item["locator"] = item["locator"].replace("fixture:", "D-098-original-illustrative:")
    return ir
