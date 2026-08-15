# Ghi chú bàn giao

- Artifact: `chart.html` — biểu đồ cột tiếng Việt, khung 16:9 (1600 × 900), chế độ `editorial`, tự chứa và không dùng tài nguyên mạng.
- SHA-256 HTML: `1161b61a71abb52da30a416133bb41c564b64eae10cbbcd471a603eedf16d4aa`.
- Dữ liệu được giữ nguyên: Quý 1 = 12 / 24; Quý 2 = 0 / 20; Quý 3 = -3 / thiếu; Quý 4 = 16 / 22; đơn vị `sự cố`.
- Ô Tiêu chuẩn của Quý 3 được biểu diễn là dữ liệu thiếu (`null`, `missing=true`), không được tự điền thành 0.
- QA đạt: semantic grammar, fidelity, carrier equivalence, SVG contract, quantitative integrity, HTML static fallback và 27 cặp tương phản của visual system.
- PNG: không bàn giao. Rasterizer Google Chrome cài sẵn đã thất bại khi pipeline thử tạo PNG; không cài thêm dependency. HTML là fallback minh bạch theo hợp đồng output của skill.
- Trạng thái browser/PNG: `blocked / not executable`; không tuyên bố browser pass hay PNG pass.
