# P-19B Review 44 — `layer-stack`

## Phạm vi

Review 44 chỉ thay ba specimen theo mode của canonical diagram `layer-stack` và một preview tổng hợp. Biến thể trình bày `layers`, 90 HTML không thuộc mục tiêu, 30 preview không thuộc mục tiêu, 14 anchor P-18 và toàn bộ phạm vi P-17/P-19A được giữ nguyên.

## Phân tích tham chiếu và ranh giới độc lập

Hai ảnh do chủ sở hữu cung cấp chỉ được dùng như rubric thị giác. Các đặc điểm trừu tượng được tiếp nhận là: kiến trúc nhiều tầng có thứ tự, module nằm trong từng tầng, một tầng có thể chia miền con, và quan hệ phụ thuộc giữa tầng trên với tầng dưới. Tên công ty, nhãn, hình trụ giả 3D, màu cầu vồng, phong cách sketch, bố cục và nội dung cụ thể trong ảnh không được sao chép.

Thiết kế được triển khai độc lập cho bối cảnh “Kiến trúc nền tảng AI doanh nghiệp” bằng tiếng Việt, trong đúng grammar P-18 đã duyệt: nền dot-field, token màu hiện hành, typography hiện hành, coral chỉ cho trọng tâm, viền mảnh, canvas cố định và cùng một hình học ở ba mode.

## Hợp đồng hình học D-124

- 5 tầng theo thứ tự L5 → L1: Trải nghiệm, Tác nhân & điều phối, Năng lực thông minh, Nền tảng ML, Hạ tầng vận hành.
- 23 module với phân phối chính xác `4 / 5 / 6 / 4 / 4`.
- L3 được chia thành 2 miền con cân bằng: Mô hình (3 module) và Dữ liệu & tri thức (3 module).
- L4 là tầng trọng tâm duy nhất; module “Điều phối công cụ” là module focal duy nhất.
- 4 mũi tên thẳng, căn giữa, nối liền bốn cặp tầng kề nhau.
- 1 trục trừu tượng ở trái, đọc từ “Gần người dùng” xuống “Gần hạ tầng”.
- Viền theo hệ mảnh `1.0 / 1.2 / 1.6`; không dùng token màu mới.
- Bảng thay thế truy cập được chứa đúng 23 hàng module và semantic ID tương ứng.

## Quy tắc template được giữ nguyên

- Không thay khung trang, header, metadata, legend, dot-field, token, ba mode hay typography P-18.
- Không đổi taxonomy hoặc identity của `layer-stack`.
- Không hợp nhất hoặc thay đổi presentation variant `layers`.
- Không thay đổi specimen ngoài `type-layer-stack`.

## Kiểm chứng

- Kiểm chứng tĩnh: 5 tầng, 23 module, 2 miền, 4 dependency, 1 tầng focal, 1 trục.
- Kiểm chứng hình học: ba mode có cùng tập phần tử hình học; dependency đều thẳng và cùng tâm x.
- Kiểm chứng hồi quy: 90 HTML không mục tiêu giống review 43 sau khi chuẩn hóa candidate ID; 30 preview không mục tiêu byte-identical.
- Kiểm chứng thị giác: render neutral-light cục bộ, xác nhận phân cấp, khoảng cách, màu, viền và khả năng đọc.

## Ranh giới phase

Đây chỉ là P-19B remediation theo D-124. Không thực hiện P-19C, package, dist, publication, commit, push hoặc release.
