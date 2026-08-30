"""Original D-088 eight-sprint bar-chart fixture."""
from semantic_fixtures import annotation, axis, datum, finalize, series


def bar_chart_fixture():
    points = [
        datum("sprint-01", "Sprint 1", 68),
        datum("sprint-02", "Sprint 2", 84),
        datum("sprint-03", "Sprint 3", 92),
        datum("sprint-04", "Sprint 4", 75),
        datum("sprint-05", "Sprint 5", 108),
        datum("sprint-06", "Sprint 6", 99),
        datum("sprint-07", "Sprint 7", 82),
        datum("sprint-08", "Sprint 8", 90),
    ]
    ir = finalize(
        "bar-chart",
        series=[series("series-sprint-points", "Điểm hoàn thành", points, "điểm")],
        axes=[
            axis("axis-sprint", "x", "categorical", "Sprint"),
            axis("axis-story-points", "y", "linear", "Điểm hoàn thành", domain_min=0, domain_max=120, unit="điểm"),
        ],
        annotations=[annotation("annotation-record-high", "Kỷ lục cao nhất", ["sprint-05"])],
    )
    ir["diagram"].update({
        "title": "Điểm hoàn thành theo sprint",
        "detail": "faithful",
        "audience": "mixed",
    })
    ir["accessibility"].update({
        "name": "Điểm hoàn thành theo sprint",
        "description": "Biểu đồ cột so sánh điểm hoàn thành của tám sprint trên cùng thang đo từ 0 đến 120; Sprint 5 đạt kỷ lục 108 điểm.",
        "reading_order": ["series-sprint-points", "axis-sprint", "axis-story-points", "annotation-record-high"],
    })
    for item in ir["source_items"]:
        item["locator"] = item["locator"].replace("fixture:", "D-088-original-illustrative:")
    return ir
