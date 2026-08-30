"""Original D-097 five-stage medallion lifecycle fixture."""

from semantic_fixtures import annotation, e, finalize, lane, n


def medallion_fixture():
    ir = finalize(
        "medallion",
        nodes=[
            n(
                "dataset-raw", "dataset",
                "Dữ liệu tiếp nhận | landing-commerce | Bộ thu nhận luồng | JSON · Parquet | Kỹ sư tích hợp | sự kiện nhấp chuột | đơn hàng nguyên bản",
            ),
            n(
                "dataset-anonymized", "dataset",
                "Dữ liệu ẩn danh | privacy-commerce | SQL chính sách | Iceberg · phân vùng | Kỹ sư dữ liệu | mã phiên thay thế | định danh được che",
            ),
            n(
                "dataset-staging", "dataset",
                "Dữ liệu chuẩn hóa | staging-commerce | SQL · sổ tay | Iceberg · kiểm định | Chuyên viên dữ liệu | đơn hàng đã nối | sự kiện hợp lệ",
            ),
            n(
                "dataset-aggregated", "dataset",
                "Dữ liệu tổng hợp | mart-commerce | SQL tổng hợp | Iceberg · chỉ số | Nhóm phân tích | tỷ lệ chuyển đổi | doanh thu theo kênh",
                state="focal",
            ),
            n(
                "dataset-archive", "dataset",
                "Kho lưu trữ | archive-commerce | Chính sách vòng đời | Lạnh · bất biến | Vận hành dữ liệu | sự kiện lưu giữ | ảnh chụp kỳ đã khóa",
                state="archive",
            ),
        ],
        edges=[
            e("promotion-mask", "dataset-raw", "dataset-anonymized", "promotion", label="ẨN ĐỊNH DANH"),
            e("promotion-clean", "dataset-anonymized", "dataset-staging", "promotion", label="LÀM SẠCH + LIÊN KẾT"),
            e("promotion-aggregate", "dataset-staging", "dataset-aggregated", "promotion", label="TỔNG HỢP"),
            e("promotion-lifecycle", "dataset-aggregated", "dataset-archive", "promotion", label="LƯU TRỮ VÒNG ĐỜI"),
        ],
        lanes=[
            lane("tier-raw", "T1 · TIẾP NHẬN", ["dataset-raw"], 0),
            lane("tier-anonymized", "T2 · RIÊNG TƯ", ["dataset-anonymized"], 1),
            lane("tier-staging", "T3 · CHUẨN HÓA", ["dataset-staging"], 2),
            lane("tier-aggregated", "T4 · PHỤC VỤ", ["dataset-aggregated"], 3),
            lane("tier-archive", "T5 · LƯU TRỮ", ["dataset-archive"], 4),
        ],
        annotations=[
            annotation(
                "path-sql",
                "SQL PATH | Lọc · liên kết · tổng hợp · chạy lặp lại",
                ["dataset-raw", "dataset-anonymized", "dataset-staging", "dataset-aggregated"],
            ),
            annotation(
                "path-notebook",
                "NOTEBOOK PATH | Khám phá · kiểm định · mô hình · phân tích tương tác",
                ["dataset-staging", "dataset-aggregated"],
            ),
        ],
    )
    ir["request_id"] = "request-medallion-review17"
    ir["diagram"]["title"] = "Vòng đời dữ liệu thương mại"
    ir["selection"]["evidence"] = ["request:owner-directed detailed five-stage medallion lifecycle"]
    ir["accessibility"] = {
        "name": "Vòng đời dữ liệu thương mại",
        "description": "Năm tầng dữ liệu từ tiếp nhận đến lưu trữ, với tầng tổng hợp là bề mặt phục vụ trọng tâm và hai đường xử lý có thể kiểm chứng.",
        "reading_order": [
            "tier-raw", "dataset-raw", "promotion-mask",
            "tier-anonymized", "dataset-anonymized", "promotion-clean",
            "tier-staging", "dataset-staging", "promotion-aggregate",
            "tier-aggregated", "dataset-aggregated", "promotion-lifecycle",
            "tier-archive", "dataset-archive", "path-sql", "path-notebook",
        ],
        "data_representation_required": False,
    }
    for source in ir["source_items"]:
        source["locator"] = source["locator"].replace("fixture:", "D-097-original-illustrative:")
    return ir
