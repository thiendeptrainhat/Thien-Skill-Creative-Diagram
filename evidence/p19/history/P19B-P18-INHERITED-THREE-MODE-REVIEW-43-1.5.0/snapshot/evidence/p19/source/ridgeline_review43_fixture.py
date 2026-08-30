"""Original D-123 twelve-service shared-domain ridgeline fixture."""
import copy

from semantic_fixtures import annotation, axis, distribution_datum, finalize, series


def ridgeline_fixture():
    distribution = {
        "method": "kde-gaussian",
        "domain_min": 0,
        "domain_max": 120,
        "bin_count": 20,
        "bin_edges": list(range(0, 121, 6)),
        "bandwidth": 7,
        "amplitude_normalization": "global-max",
        "shared_domain": True,
        "shared_bins": True,
    }
    offsets = (-31, -25, -20, -16, -13, -10, -8, -6, -4, -2, -1, 0,
               1, 2, 4, 6, 8, 10, 13, 16, 20, 24, 29, 35)
    definitions = (
        ("platform", "Nền tảng", 38, 0.82),
        ("payments", "Thanh toán", 54, 0.94),
        ("identity", "Nhận diện", 47, 0.72),
        ("search", "Tìm kiếm", 31, 0.66),
        ("data", "Dữ liệu", 63, 1.08),
        ("mobile", "Di động", 43, 0.78),
        ("partners", "Đối tác", 69, 1.12),
        ("retail", "Bán lẻ", 58, 0.88),
        ("content", "Nội dung", 36, 0.70),
        ("analytics", "Phân tích", 74, 1.16),
        ("support", "Hỗ trợ", 51, 1.02),
        ("archive", "Lưu trữ", 81, 1.20),
    )
    series_items = []
    for slug, label, center, spread in definitions:
        samples = [max(0, min(120, center + round(offset * spread))) for offset in offsets]
        series_items.append(
            series(
                f"series-{slug}", label,
                [distribution_datum(f"samples-{slug}", samples)],
                "ms", distribution=copy.deepcopy(distribution),
            )
        )
    ir = finalize(
        "line-chart",
        series=series_items,
        axes=[
            axis("axis-ridge-domain", "x", "linear", "Độ trễ phản hồi", domain_min=0, domain_max=120, unit="ms"),
            axis("axis-ridge-amplitude", "y", "linear", "Mật độ chuẩn hóa", domain_min=0, domain_max=1, unit=None),
        ],
        annotations=[
            annotation(
                "annotation-ridgeline-focal",
                "Nền tảng là phân phối trọng tâm; mọi hàng dùng chung miền và cùng chuẩn biên độ",
                ["series-platform"],
            )
        ],
    )
    ir["diagram"].update({
        "variant_ids": ["CAP-V19"],
        "title": "Phân bố độ trễ phản hồi theo dịch vụ",
        "detail": "faithful",
        "audience": "mixed",
    })
    ir["accessibility"].update({
        "name": "Phân bố độ trễ phản hồi theo dịch vụ",
        "description": (
            "Ridgeline chart gồm mười hai phân phối độ trễ trên cùng miền 0–120 mili giây và cùng chuẩn biên độ. "
            "Mỗi hàng có đường mật độ, ba dải phân vị 50, 80 và 95 phần trăm cùng điểm trung vị; "
            "đường dọc cho biết trung vị chung. Nền tảng là chuỗi trọng tâm."
        ),
        "reading_order": [
            *(f"series-{slug}" for slug, *_ in definitions),
            "axis-ridge-domain", "axis-ridge-amplitude", "annotation-ridgeline-focal",
        ],
    })
    for item in ir["source_items"]:
        item["locator"] = item["locator"].replace("fixture:", "D-123-original-illustrative:")
    return ir
