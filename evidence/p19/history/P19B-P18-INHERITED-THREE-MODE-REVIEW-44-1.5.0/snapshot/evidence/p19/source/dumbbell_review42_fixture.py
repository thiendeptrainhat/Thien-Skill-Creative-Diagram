"""Original D-122 twelve-category shared-scale dumbbell fixture."""
from semantic_fixtures import annotation, axis, datum, finalize, series


def dumbbell_fixture():
    observations = (
        ("platform", "Nền tảng", 48, 84),
        ("payments", "Thanh toán", 62, 80),
        ("data", "Dữ liệu", 54, 78),
        ("mobile", "Di động", 69, 82),
        ("partners", "Đối tác", 44, 71),
        ("retail", "Bán lẻ", 58, 74),
        ("search", "Tìm kiếm", 52, 68),
        ("support", "Hỗ trợ", 73, 86),
        ("identity", "Nhận diện", 64, 91),
        ("operations", "Vận hành", 47, 66),
        ("content", "Nội dung", 56, 76),
        ("analytics", "Phân tích", 67, 88),
    )
    before = [datum(f"before-{slug}", label, first) for slug, label, first, _ in observations]
    after = [datum(f"after-{slug}", label, second) for slug, label, _, second in observations]
    ir = finalize(
        "bar-chart",
        series=[
            series("series-before", "Trước tối ưu", before, "%"),
            series("series-after", "Sau tối ưu", after, "%"),
        ],
        axes=[
            axis("axis-dumbbell-category", "x", "categorical", "Nhóm sản phẩm"),
            axis("axis-dumbbell-value", "y", "linear", "Tỷ lệ tự động hóa", domain_min=0, domain_max=100, unit="%"),
        ],
        annotations=[
            annotation(
                "annotation-dumbbell-focal",
                "Nền tảng là nhóm trọng tâm với mức cải thiện lớn nhất",
                ["series-before", "series-after"],
            )
        ],
    )
    ir["diagram"].update({
        "variant_ids": ["CAP-V17"],
        "title": "Khoảng cách tự động hóa theo nhóm sản phẩm",
        "detail": "faithful",
        "audience": "mixed",
    })
    ir["accessibility"].update({
        "name": "Khoảng cách tự động hóa theo nhóm sản phẩm",
        "description": (
            "Dumbbell chart so sánh tỷ lệ tự động hóa trước và sau tối ưu cho mười hai nhóm "
            "trên cùng thang 0–100 phần trăm. Mỗi hàng có hai endpoint, một đường nối và nhãn "
            "chênh lệch trực tiếp; các dải dọc biểu diễn trung bình cộng hoặc trừ một độ lệch chuẩn."
        ),
        "reading_order": [
            "series-before", "series-after", "axis-dumbbell-category",
            "axis-dumbbell-value", "annotation-dumbbell-focal",
        ],
    })
    for item in ir["source_items"]:
        item["locator"] = item["locator"].replace("fixture:", "D-122-original-illustrative:")
    return ir
