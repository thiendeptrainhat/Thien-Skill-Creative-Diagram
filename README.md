# Thiện’s Skill — Creative Diagram

<p align="center">
  <img src="evidence/p09/candidates/full-crest-plate-light-400.png" alt="TDTN crest with sword, lion, letterforms and open book in navy and gold" width="180">
</p>

## Giới thiệu skill

**Thiện’s Skill — Creative Diagram** hỗ trợ chuyển yêu cầu bằng ngôn ngữ tự nhiên, dữ liệu và quan hệ nghiệp vụ thành diagram có cấu trúc, dễ đọc và kiểm tra được. Skill phù hợp với sơ đồ kiến trúc, quy trình, mô hình dữ liệu, biểu đồ định lượng, kế hoạch và hành trình người dùng; chú trọng giữ đúng ngữ nghĩa, số liệu, khả năng tiếp cận và tiếng Việt.

**Bản phát hành hiện hành: [v2.5.0](https://github.com/thiendeptrainhat/Thien-Skill-Creative-Diagram/releases/tag/v2.5.0)** — private, non-draft, non-prerelease. Tên kỹ thuật, folder và ID của skill vẫn là `thien-skill-creative-diagram`; tên hiển thị là `Thiện’s Skill — Creative Diagram`.

### Nền tảng từ bản 2.0.0

- Một lõi dùng chung cho 39 loại diagram chuẩn và bốn biến thể chuyên biệt: Dumbbell, Slopegraph, Ridgeline và Bubble.
- Thư viện 45 mẫu tham chiếu, mỗi mẫu có ba phong cách ngang cấp `neutral-light`, `neutral-dark`, `editorial`: tổng cộng 135 mẫu.
- Quy trình chọn loại diagram, bảo toàn dữ liệu, xử lý đầu vào không tin cậy và kiểm tra khả năng đọc; ba cách đóng gói Claude, OpenAI và Universal từ cùng một nguồn.

### Cải tiến trong bản 2.5.0

- Hoàn thiện **45 structural profile trên 14 layout engine** — quy tắc bố cục tương ứng với cấu trúc của từng diagram. 45 profile gồm 39 loại chuẩn, bốn biến thể và hai profile trình bày, không phải 45 loại ngữ nghĩa hoàn toàn độc lập.
- Luồng tạo chuẩn xuất `diagram.svg` cùng `diagram.ledger.json`, lưu dữ liệu ngữ nghĩa, profile, hash và kết quả kiểm tra hình học để đối chiếu.
- Cải thiện đường nối và hướng mũi tên, thành viên nhóm/lane, bố cục theo canvas, cùng cấu trúc deployment và database schema.
- Sửa các vấn đề về nhãn/số liệu định lượng, cảm xúc dạng phân loại trong user journey, va chạm tiêu đề ridgeline và cách nhận diện series của bubble không chỉ dựa vào màu.
- Ba gói đã qua kiểm tra package/parity và smoke trên runtime được giải nén; bản phát hành có đúng năm artifact tại `dist/2.5.0/`. Khả năng tích hợp trên từng host vẫn có điều kiện, xem [Hướng dẫn cài đặt](#hướng-dẫn-cài-đặt).

Các cải tiến trên dựa vào evidence đã chốt cho bản phát hành; không phải cam kết mọi diagram mới tự động đạt QA. Xem [Release body v2.5.0](https://github.com/thiendeptrainhat/Thien-Skill-Creative-Diagram/releases/tag/v2.5.0) để đối chiếu thay đổi, giới hạn và artifact.

## Các hình diagram của skill

Dưới đây là **45 ảnh `neutral-light` đã duyệt**, giữ nguyên từ gallery tham chiếu. Đây là tài liệu minh họa và lịch sử QA, không phải ảnh được tạo lại bằng runtime `2.5.0`, template cố định hoặc giới hạn nội dung đầu ra.

Bấm ảnh để mở tệp HTML tương ứng. Để xem bản render và chuyển giữa cả ba phong cách, tải repository rồi mở [thư viện đầy đủ — assets/index.html](assets/index.html) bằng trình duyệt. GitHub có thể hiển thị mã nguồn HTML thay vì chạy trực tiếp trang.

Người dùng có thể thay nội dung, số lượng thành phần, nhãn, kích thước, màu sắc và cách nhấn mạnh khi an toàn, phù hợp ngữ nghĩa. Nếu yêu cầu thay đổi cấu trúc vượt profile chuẩn, skill phải nêu rõ khả năng xử lý, không âm thầm dùng một loại diagram khác.

<table>
  <tr>
    <td align="center"><a href="assets/diagrams/118-cap-cap-v17-dumbbell--neutral-light.html"><img src="screenshots/diagrams/118-cap-cap-v17-dumbbell--neutral-light.png" alt="Khoảng cách tự động hóa theo nhóm sản phẩm" width="300"></a><br><sub>01 · Khoảng cách tự động hóa theo nhóm sản phẩm</sub></td>
    <td align="center"><a href="assets/diagrams/121-cap-cap-v18-slope-graph--neutral-light.html"><img src="screenshots/diagrams/121-cap-cap-v18-slope-graph--neutral-light.png" alt="Dịch chuyển hiệu suất giữa hai kỳ" width="300"></a><br><sub>02 · Dịch chuyển hiệu suất giữa hai kỳ</sub></td>
    <td align="center"><a href="assets/diagrams/124-cap-cap-v19-ridgeline--neutral-light.html"><img src="screenshots/diagrams/124-cap-cap-v19-ridgeline--neutral-light.png" alt="Phân bố độ trễ phản hồi theo dịch vụ" width="300"></a><br><sub>03 · Phân bố độ trễ phản hồi theo dịch vụ</sub></td>
  </tr>
  <tr>
    <td align="center"><a href="assets/diagrams/127-cap-cap-v20-bubble--neutral-light.html"><img src="screenshots/diagrams/127-cap-cap-v20-bubble--neutral-light.png" alt="Quy mô và tăng trưởng danh mục sản phẩm" width="300"></a><br><sub>04 · Quy mô và tăng trưởng danh mục sản phẩm</sub></td>
    <td align="center"><a href="assets/diagrams/11-compartment-model--neutral-light.html"><img src="screenshots/diagrams/11-compartment-model--neutral-light.png" alt="Compartment anchor" width="300"></a><br><sub>05 · Compartment anchor</sub></td>
    <td align="center"><a href="assets/diagrams/10-containment-stack--neutral-light.html"><img src="screenshots/diagrams/10-containment-stack--neutral-light.png" alt="Containment anchor" width="300"></a><br><sub>06 · Containment anchor</sub></td>
  </tr>
  <tr>
    <td align="center"><a href="assets/diagrams/04-dependency-dag--neutral-light.html"><img src="screenshots/diagrams/04-dependency-dag--neutral-light.png" alt="Dependency anchor" width="300"></a><br><sub>07 · Dependency anchor</sub></td>
    <td align="center"><a href="assets/diagrams/05-directed-flow-state--neutral-light.html"><img src="screenshots/diagrams/05-directed-flow-state--neutral-light.png" alt="Directed flow anchor" width="300"></a><br><sub>08 · Directed flow anchor</sub></td>
    <td align="center"><a href="assets/diagrams/09-hierarchy--neutral-light.html"><img src="screenshots/diagrams/09-hierarchy--neutral-light.png" alt="Hierarchy anchor" width="300"></a><br><sub>09 · Hierarchy anchor</sub></td>
  </tr>
  <tr>
    <td align="center"><a href="assets/diagrams/02-integration-pipeline--neutral-light.html"><img src="screenshots/diagrams/02-integration-pipeline--neutral-light.png" alt="Integration anchor" width="300"></a><br><sub>10 · Integration anchor</sub></td>
    <td align="center"><a href="assets/diagrams/06-lane-interaction--neutral-light.html"><img src="screenshots/diagrams/06-lane-interaction--neutral-light.png" alt="Lane interaction anchor" width="300"></a><br><sub>11 · Lane interaction anchor</sub></td>
    <td align="center"><a href="assets/diagrams/13-quantitative--neutral-light.html"><img src="screenshots/diagrams/13-quantitative--neutral-light.png" alt="Quantitative anchor" width="300"></a><br><sub>12 · Quantitative anchor</sub></td>
  </tr>
  <tr>
    <td align="center"><a href="assets/diagrams/03-runtime-deployment--neutral-light.html"><img src="screenshots/diagrams/03-runtime-deployment--neutral-light.png" alt="Deployment anchor" width="300"></a><br><sub>13 · Deployment anchor</sub></td>
    <td align="center"><a href="assets/diagrams/12-spatial-matrix--neutral-light.html"><img src="screenshots/diagrams/12-spatial-matrix--neutral-light.png" alt="Spatial matrix anchor" width="300"></a><br><sub>14 · Spatial matrix anchor</sub></td>
    <td align="center"><a href="assets/diagrams/14-special-geometry--neutral-light.html"><img src="screenshots/diagrams/14-special-geometry--neutral-light.png" alt="Special geometry anchor" width="300"></a><br><sub>15 · Special geometry anchor</sub></td>
  </tr>
  <tr>
    <td align="center"><a href="assets/diagrams/07-time-planning--neutral-light.html"><img src="screenshots/diagrams/07-time-planning--neutral-light.png" alt="Timeline anchor" width="300"></a><br><sub>16 · Timeline anchor</sub></td>
    <td align="center"><a href="assets/diagrams/01-topology-and-zones--neutral-light.html"><img src="screenshots/diagrams/01-topology-and-zones--neutral-light.png" alt="Architecture anchor" width="300"></a><br><sub>17 · Architecture anchor</sub></td>
    <td align="center"><a href="assets/diagrams/055-type-bar-chart--neutral-light.html"><img src="screenshots/diagrams/055-type-bar-chart--neutral-light.png" alt="Điểm hoàn thành theo sprint" width="300"></a><br><sub>18 · Điểm hoàn thành theo sprint</sub></td>
  </tr>
  <tr>
    <td align="center"><a href="assets/diagrams/082-type-dp-integration--neutral-light.html"><img src="screenshots/diagrams/082-type-dp-integration--neutral-light.png" alt="Nền tảng tích hợp dữ liệu" width="300"></a><br><sub>19 · Nền tảng tích hợp dữ liệu</sub></td>
    <td align="center"><a href="assets/diagrams/085-type-dp-security-matrix--neutral-light.html"><img src="screenshots/diagrams/085-type-dp-security-matrix--neutral-light.png" alt="Ma trận quyền truy cập nền tảng dữ liệu" width="300"></a><br><sub>20 · Ma trận quyền truy cập nền tảng dữ liệu</sub></td>
    <td align="center"><a href="assets/diagrams/016-type-er-data-model--neutral-light.html"><img src="screenshots/diagrams/016-type-er-data-model--neutral-light.png" alt="Mô hình dữ liệu nội dung" width="300"></a><br><sub>21 · Mô hình dữ liệu nội dung</sub></td>
  </tr>
  <tr>
    <td align="center"><a href="assets/diagrams/091-type-fishbone--neutral-light.html"><img src="screenshots/diagrams/091-type-fishbone--neutral-light.png" alt="Phân tích nguyên nhân hồ sơ xử lý trễ" width="300"></a><br><sub>22 · Phân tích nguyên nhân hồ sơ xử lý trễ</sub></td>
    <td align="center"><a href="assets/diagrams/064-type-gantt--neutral-light.html"><img src="screenshots/diagrams/064-type-gantt--neutral-light.png" alt="Triển khai cổng tri thức nội bộ" width="300"></a><br><sub>23 · Triển khai cổng tri thức nội bộ</sub></td>
    <td align="center"><a href="assets/diagrams/070-type-high-level--neutral-light.html"><img src="screenshots/diagrams/070-type-high-level--neutral-light.png" alt="Tổng quan nền tảng dữ liệu" width="300"></a><br><sub>24 · Tổng quan nền tảng dữ liệu</sub></td>
  </tr>
  <tr>
    <td align="center"><a href="assets/diagrams/004-type-it-current-state--neutral-light.html"><img src="screenshots/diagrams/004-type-it-current-state--neutral-light.png" alt="Hiện trạng luồng báo cáo" width="300"></a><br><sub>25 · Hiện trạng luồng báo cáo</sub></td>
    <td align="center"><a href="assets/diagrams/097-type-kanban--neutral-light.html"><img src="screenshots/diagrams/097-type-kanban--neutral-light.png" alt="Bảng công việc vận hành" width="300"></a><br><sub>26 · Bảng công việc vận hành</sub></td>
    <td align="center"><a href="assets/diagrams/046-type-layer-stack--neutral-light.html"><img src="screenshots/diagrams/046-type-layer-stack--neutral-light.png" alt="Kiến trúc nền tảng AI doanh nghiệp" width="300"></a><br><sub>27 · Kiến trúc nền tảng AI doanh nghiệp</sub></td>
  </tr>
  <tr>
    <td align="center"><a href="assets/diagrams/130-type-layers--neutral-light.html"><img src="screenshots/diagrams/130-type-layers--neutral-light.png" alt="Các lớp của nền tảng nghiệp vụ" width="300"></a><br><sub>28 · Các lớp của nền tảng nghiệp vụ</sub></td>
    <td align="center"><a href="assets/diagrams/061-type-line-chart--neutral-light.html"><img src="screenshots/diagrams/061-type-line-chart--neutral-light.png" alt="Xu hướng đăng ký theo tuần" width="300"></a><br><sub>29 · Xu hướng đăng ký theo tuần</sub></td>
    <td align="center"><a href="assets/diagrams/034-type-loop-flywheel--neutral-light.html"><img src="screenshots/diagrams/034-type-loop-flywheel--neutral-light.png" alt="Vòng cải tiến từ phản hồi" width="300"></a><br><sub>30 · Vòng cải tiến từ phản hồi</sub></td>
  </tr>
  <tr>
    <td align="center"><a href="assets/diagrams/076-type-medallion--neutral-light.html"><img src="screenshots/diagrams/076-type-medallion--neutral-light.png" alt="Vòng đời dữ liệu thương mại" width="300"></a><br><sub>31 · Vòng đời dữ liệu thương mại</sub></td>
    <td align="center"><a href="assets/diagrams/037-type-nested--neutral-light.html"><img src="screenshots/diagrams/037-type-nested--neutral-light.png" alt="Phạm vi cấu hình kế thừa" width="300"></a><br><sub>32 · Phạm vi cấu hình kế thừa</sub></td>
    <td align="center"><a href="assets/diagrams/031-type-polar-chart--neutral-light.html"><img src="screenshots/diagrams/031-type-polar-chart--neutral-light.png" alt="Cường độ truy cập theo cửa sổ UTC" width="300"></a><br><sub>33 · Cường độ truy cập theo cửa sổ UTC</sub></td>
  </tr>
  <tr>
    <td align="center"><a href="assets/diagrams/073-type-process--neutral-light.html"><img src="screenshots/diagrams/073-type-process--neutral-light.png" alt="Quy trình phê duyệt quyền truy cập dữ liệu" width="300"></a><br><sub>34 · Quy trình phê duyệt quyền truy cập dữ liệu</sub></td>
    <td align="center"><a href="assets/diagrams/028-type-radar--neutral-light.html"><img src="screenshots/diagrams/028-type-radar--neutral-light.png" alt="So sánh năng lực nền tảng dữ liệu" width="300"></a><br><sub>35 · So sánh năng lực nền tảng dữ liệu</sub></td>
    <td align="center"><a href="assets/diagrams/133-type-scatter-chart--neutral-light.html"><img src="screenshots/diagrams/133-type-scatter-chart--neutral-light.png" alt="Tần suất triển khai và lead time theo nhóm" width="300"></a><br><sub>36 · Tần suất triển khai và lead time theo nhóm</sub></td>
  </tr>
  <tr>
    <td align="center"><a href="assets/diagrams/010-type-sequence--neutral-light.html"><img src="screenshots/diagrams/010-type-sequence--neutral-light.png" alt="Luồng phân phối nội dung" width="300"></a><br><sub>37 · Luồng phân phối nội dung</sub></td>
    <td align="center"><a href="assets/diagrams/013-type-state-machine--neutral-light.html"><img src="screenshots/diagrams/013-type-state-machine--neutral-light.png" alt="Vòng đời nội dung tri thức" width="300"></a><br><sub>38 · Vòng đời nội dung tri thức</sub></td>
    <td align="center"><a href="assets/diagrams/112-type-story-map--neutral-light.html"><img src="screenshots/diagrams/112-type-story-map--neutral-light.png" alt="Bản đồ câu chuyện báo cáo vận hành" width="300"></a><br><sub>39 · Bản đồ câu chuyện báo cáo vận hành</sub></td>
  </tr>
  <tr>
    <td align="center"><a href="assets/diagrams/040-type-tree--neutral-light.html"><img src="screenshots/diagrams/040-type-tree--neutral-light.png" alt="Cây năng lực sản phẩm" width="300"></a><br><sub>40 · Cây năng lực sản phẩm</sub></td>
    <td align="center"><a href="assets/diagrams/058-type-treemap--neutral-light.html"><img src="screenshots/diagrams/058-type-treemap--neutral-light.png" alt="Tỷ trọng dân số theo châu lục" width="300"></a><br><sub>41 · Tỷ trọng dân số theo châu lục</sub></td>
    <td align="center"><a href="assets/diagrams/109-type-uml-class--neutral-light.html"><img src="screenshots/diagrams/109-type-uml-class--neutral-light.png" alt="Mô hình lớp thanh toán và hóa đơn" width="300"></a><br><sub>42 · Mô hình lớp thanh toán và hóa đơn</sub></td>
  </tr>
  <tr>
    <td align="center"><a href="assets/diagrams/049-type-venn--neutral-light.html"><img src="screenshots/diagrams/049-type-venn--neutral-light.png" alt="Điểm cân bằng để triển khai" width="300"></a><br><sub>43 · Điểm cân bằng để triển khai</sub></td>
    <td align="center"><a href="assets/diagrams/094-type-wardley-map--neutral-light.html"><img src="screenshots/diagrams/094-type-wardley-map--neutral-light.png" alt="Bản đồ tiến hóa của trợ lý công việc" width="300"></a><br><sub>44 · Bản đồ tiến hóa của trợ lý công việc</sub></td>
    <td align="center"><a href="assets/diagrams/08-work-experience--neutral-light.html"><img src="screenshots/diagrams/08-work-experience--neutral-light.png" alt="Experience anchor" width="300"></a><br><sub>45 · Experience anchor</sub></td>
  </tr>
</table>

## Lợi ích và vai trò của skill

### Lợi ích

- **Làm rõ thông tin:** thể hiện quan hệ, luồng xử lý, phụ thuộc và số liệu để người đọc hiểu câu chuyện chính.
- **Giảm công việc bố cục thủ công:** hỗ trợ chọn diagram, tổ chức luồng đọc, phân cấp nội dung và phân bổ khoảng cách.
- **Dễ đối chiếu và chỉnh sửa:** giữ SVG cùng ledger của luồng chuẩn để xem lại dữ liệu, quan hệ và kết quả kiểm tra.
- **Trình bày nhất quán:** dùng ba phong cách sáng, tối và biên tập mà vẫn giữ cùng ý nghĩa.
- **Dễ tiếp cận hơn:** chú trọng nhãn, thứ tự đọc và nhận diện không chỉ dựa vào màu; yêu cầu text/table bổ trợ khi cần.

### Vai trò

Skill là lớp hỗ trợ **thiết kế diagram và QA trực quan**, nằm giữa dữ liệu nguồn và artifact cuối:

- Với BA, product và vận hành: mô tả quy trình, swimlane, hành trình, backlog hoặc roadmap.
- Với kiến trúc sư, kỹ sư và nhóm dữ liệu: mô tả hệ thống, deployment, luồng dữ liệu, ER và phụ thuộc.
- Với người phân tích và người ra quyết định: trình bày so sánh, phân bố, xu hướng hoặc các đánh đổi.
- Với người viết tài liệu và đào tạo: biến nội dung đã xác nhận thành sơ đồ để giải thích.

Skill không tự xác minh sự thật của dữ liệu nguồn và không thay thế chuyên gia pháp lý, thuế, kiểm toán, an toàn, kiến trúc hoặc chuyên môn khác. Người dùng vẫn cần xác nhận nội dung nghiệp vụ trước khi sử dụng kết quả.

## Hướng dẫn sử dụng skill

### Gọi skill

Sau khi cài, có thể yêu cầu bằng ngôn ngữ tự nhiên hoặc chọn skill trong giao diện host. Trong Codex CLI/IDE, dùng `/skills` hoặc gõ `$` để chọn `thien-skill-creative-diagram`; trong ChatGPT có hỗ trợ skill, dùng bộ chọn `@`. Cách gọi có thể khác theo surface và gói cài. [Tài liệu OpenAI về skills](https://learn.chatgpt.com/docs/build-skills).

Ví dụ prompt trong Codex:

```text
$thien-skill-creative-diagram

Tạo swimlane diagram bằng tiếng Việt cho quy trình duyệt đề nghị mua hàng.
Người đề nghị: tạo đề nghị → gửi trưởng bộ phận.
Trưởng bộ phận: duyệt → chuyển kế toán.
Kế toán: kiểm tra ngân sách → xác nhận cho người đề nghị.
Giữ đúng các bên tham gia, thứ tự và chiều chuyển giao đã nêu;
không tự thêm bước, nhánh từ chối hoặc số liệu.
Dùng neutral-light, xuất SVG tĩnh cùng ledger.
Nếu dữ liệu chưa đủ, hỏi trước khi bổ sung.
```

Đây là prompt minh họa cách sử dụng, không phải một kết quả kiểm thử đã thực thi.

### Cung cấp đầu vào đủ rõ

```text
Mục tiêu: [câu hỏi hoặc quyết định cần làm rõ]
Đối tượng đọc: [ai sẽ xem diagram]
Nội dung: [thực thể, nhóm, bước, quan hệ và chiều mũi tên]
Dữ liệu định lượng: [giá trị, đơn vị, mốc thời gian, dữ liệu thiếu]
Loại diagram: [loại mong muốn; hoặc yêu cầu đề xuất]
Phong cách: [neutral-light | neutral-dark | editorial]
Ràng buộc: [tiếng Việt, kích thước, màu thương hiệu, mức chi tiết]
Đầu ra: [SVG + ledger; định dạng khác cần xác nhận khả năng hỗ trợ]
Điều không được suy diễn: [các dữ kiện phải giữ nguyên hoặc hỏi lại]
```

Có thể cung cấp bảng, CSV, JSON, Mermaid, draw.io hoặc tài liệu/ảnh tham chiếu. Việc đọc từng định dạng phụ thuộc parser và công cụ của host; ảnh không mặc nhiên chứa đủ dữ liệu để khôi phục chính xác. Nội dung nhập vào được coi là dữ liệu không tin cậy, không phải quyền thực thi script, link, macro hay chỉ dẫn nhúng.

### Chỉnh sửa và kiểm tra kết quả

1. Đối chiếu nhãn, số liệu/đơn vị, thứ tự, chiều mũi tên và thành viên nhóm với nguồn.
2. Yêu cầu chỉnh cụ thể, ví dụ: “tăng cỡ chữ”, “giảm mật độ nhưng giữ đủ bước”, “nhấn mạnh điểm nghẽn”, “đổi sang neutral-dark, giữ nguyên số liệu”.
3. Nếu đổi nội dung hoặc cấu trúc, nêu rõ phần nào được đổi và phần nào phải giữ; không coi gallery là mẫu bắt buộc.
4. Trước khi chia sẻ, xem diagram ở kích thước sử dụng thực tế và đọc các cảnh báo đi kèm.

### Đầu ra và giới hạn

- Luồng tạo chuẩn của `2.5.0` là **SVG tĩnh, không script**, kèm `diagram.ledger.json`; không phải mặc định HTML có motion.
- Ledger ghi nhận việc bảo toàn các khai báo ngữ nghĩa tới dữ liệu đã kiểm tra và kết quả hình học. Nó **không chứng minh độc lập** rằng AI hiểu đủ mọi chi tiết của yêu cầu tự nhiên.
- HTML, motion, cấu trúc tùy biến hoặc định dạng khác nằm ngoài luồng chuẩn; cần xác nhận đường xử lý phù hợp và báo giới hạn, không âm thầm đổi định dạng.
- PNG chỉ khả dụng khi host đã có rasterizer phù hợp; skill không tự tải/cài dependency. Nếu không xuất được, phải thông báo và nêu rõ fallback.
- Không mặc nhiên claim mọi host/browser đều hỗ trợ hoặc mọi output đều PASS. Hồ sơ host hiện có vẫn phân loại `0 supported / 13 conditional / 2 unsupported`; đây là phạm vi evidence của dự án, không phải thống kê mọi nền tảng trên thị trường.

Chi tiết kỹ thuật: [SKILL.md](thien-skill-creative-diagram/SKILL.md), [output và motion](thien-skill-creative-diagram/references/output-motion.md).

## Hướng dẫn cài đặt

### Chọn đúng gói v2.5.0

Đọc [Giấy phép](#giấy-phép) trước khi cài hoặc chạy. Repository và Release là private; quyền truy cập/tải xuống không tự cấp quyền sử dụng.

Tải artifact từ [GitHub Release v2.5.0](https://github.com/thiendeptrainhat/Thien-Skill-Creative-Diagram/releases/tag/v2.5.0), hoặc dùng đúng file trong [dist/2.5.0](dist/2.5.0/):

| Gói / tệp | Dùng cho | SHA-256 |
| --- | --- | --- |
| [Thien-Skill-Creative-Diagram-v2.5.0-Claude.zip](dist/2.5.0/Thien-Skill-Creative-Diagram-v2.5.0-Claude.zip) | Claude Code plugin | `b986fa524aa35d903f7686af58e3241e05f2cc047fc1773049b682c617d0c8e2` |
| [Thien-Skill-Creative-Diagram-v2.5.0-ChatGPT.zip](dist/2.5.0/Thien-Skill-Creative-Diagram-v2.5.0-ChatGPT.zip) | OpenAI plugin cho host hỗ trợ | `d3a2c9d1f3a36fe8ceb6cb8e2d842839961440156065a9d43bdfa3039d1d57a2` |
| [Thien-Skill-Creative-Diagram-v2.5.0-Universal.zip](dist/2.5.0/Thien-Skill-Creative-Diagram-v2.5.0-Universal.zip) | Raw skill cho Codex và host đọc Agent Skills | `c0e1f954c6c5b9a308a27fc37ce2aa3dd4b1dcf6544ee22d7828b40224ff6ffb` |
| [SHA256SUMS](dist/2.5.0/SHA256SUMS) | Checksum của ba ZIP | `578d844d1ad77162b83b9b9e199f54b7042dc7b0be813cfc6b92ec744b1835e2` |
| [packaging-report.json](dist/2.5.0/packaging-report.json) | Báo cáo đóng gói/parity | `1d16f994ee9acc3b5a024edf3d7d02d9cf25c2e47dae4352b9734cf4f48cfe1a` |

Ba ZIP có cùng lõi runtime nhưng lớp đóng gói khác nhau. Tên `ChatGPT` là tên archive của OpenAI plugin, **không bảo đảm upload ZIP trực tiếp vào mọi tài khoản ChatGPT**. Không đổi đuôi/tên một gói để dùng thay gói khác, không cài trùng nhiều bản cùng ID vào một host.

### Xác minh checksum

Đặt `SHA256SUMS` và ba ZIP cùng thư mục rồi chạy một trong hai lệnh:

```bash
# macOS
shasum -a 256 -c SHA256SUMS
```

```bash
# Linux có GNU coreutils
sha256sum -c SHA256SUMS
```

Trên Windows PowerShell, lấy hash từng ZIP và so với bảng:

```powershell
Get-FileHash .\Thien-Skill-Creative-Diagram-v2.5.0-Claude.zip -Algorithm SHA256
Get-FileHash .\Thien-Skill-Creative-Diagram-v2.5.0-ChatGPT.zip -Algorithm SHA256
Get-FileHash .\Thien-Skill-Creative-Diagram-v2.5.0-Universal.zip -Algorithm SHA256
```

`SHA256SUMS` chỉ liệt kê ba ZIP. Đối chiếu hash của chính `SHA256SUMS` và `packaging-report.json` với bảng trên hoặc Release body. Nếu chỉ tải một ZIP, tính SHA-256 riêng của file đó; không coi lỗi thiếu các ZIP còn lại là xác minh thành công. Dừng nếu có mismatch.

### Claude Code — gói Claude

Từ thư mục tải artifact, giải nén vào **thư mục mới chưa tồn tại**. Ví dụ bash; dừng nếu bước này không thành công:

```bash
test ! -e ./tcd-claude-v2.5.0 && test ! -L ./tcd-claude-v2.5.0 && unzip -n ./Thien-Skill-Creative-Diagram-v2.5.0-Claude.zip -d ./tcd-claude-v2.5.0
```

Sau khi giải nén thành công, validate và nạp đúng plugin root:

```bash
claude plugin validate ./tcd-claude-v2.5.0/thien-skill-creative-diagram &&
  claude --plugin-dir ./tcd-claude-v2.5.0/thien-skill-creative-diagram
```

Chỉ nạp nếu validation thành công. `--plugin-dir` nạp cho phiên hiện tại; không đồng nghĩa đã cài cố định qua marketplace. Trong phiên đó, gọi:

```text
/thien-skill-creative-diagram:thien-skill-creative-diagram
```

Nếu skill không xuất hiện, xem `/help` và log nạp plugin. Cấu trúc Claude có `.claude-plugin/plugin.json` tại plugin root; không dùng gói ChatGPT thay thế. [Claude Code plugins](https://code.claude.com/docs/en/plugins), [plugin reference](https://code.claude.com/docs/en/plugins-reference).

### Codex — gói Universal

Đây là đường cài raw skill cho host đọc `.agents/skills`. Chọn **một** phạm vi: repository hoặc người dùng. Đích phải chưa có folder/symlink `thien-skill-creative-diagram`; nếu đã có bản cũ, dừng để bảo toàn và xử lý nâng cấp riêng, không giải nén chồng.

**Cho một repository:** chạy tại repository đích, thay `/path/to/` bằng thư mục chứa ZIP:

```bash
mkdir -p ./.agents/skills
test ! -e ./.agents/skills/thien-skill-creative-diagram && test ! -L ./.agents/skills/thien-skill-creative-diagram && unzip -n "/path/to/Thien-Skill-Creative-Diagram-v2.5.0-Universal.zip" -d ./.agents/skills
```

**Cho người dùng hiện tại:** dùng đích `$HOME/.agents/skills` thay vì repository:

```bash
mkdir -p "$HOME/.agents/skills"
test ! -e "$HOME/.agents/skills/thien-skill-creative-diagram" && test ! -L "$HOME/.agents/skills/thien-skill-creative-diagram" && unzip -n "/path/to/Thien-Skill-Creative-Diagram-v2.5.0-Universal.zip" -d "$HOME/.agents/skills"
```

Kết quả phải có `.agents/skills/thien-skill-creative-diagram/SKILL.md` cùng các thư mục `scripts/`, `references/`, `agents/` và tài liệu license. Giữ nguyên technical ID/folder. Nếu skill chưa xuất hiện, khởi động lại Codex. Vị trí discovery và cách gọi được đối chiếu với [OpenAI — Build skills](https://learn.chatgpt.com/docs/build-skills).

### ChatGPT Desktop/Codex — gói ChatGPT (OpenAI plugin)

Archive chứa `.codex-plugin/plugin.json` và `skills/thien-skill-creative-diagram/SKILL.md` dưới root `thien-skill-creative-diagram/`. Route này phụ thuộc phiên bản ứng dụng, tài khoản và workspace policy; không thay thế quyền cấp phép của skill.

Với **local repository marketplace** trên desktop có hỗ trợ:

1. Tại repository đích, giải nén vào `plugins/` khi folder plugin chưa tồn tại:

```bash
mkdir -p ./plugins
test ! -e ./plugins/thien-skill-creative-diagram && test ! -L ./plugins/thien-skill-creative-diagram && unzip -n "/path/to/Thien-Skill-Creative-Diagram-v2.5.0-ChatGPT.zip" -d ./plugins
```

2. Sau khi giải nén thành công, thêm entry vào `.agents/plugins/marketplace.json` theo mẫu. Nếu file đã tồn tại, hợp nhất entry, không ghi đè marketplace khác.

```json
{
  "name": "thien-private-plugins",
  "interface": {
    "displayName": "Thien Private Plugins"
  },
  "plugins": [
    {
      "name": "thien-skill-creative-diagram",
      "source": {
        "source": "local",
        "path": "./plugins/thien-skill-creative-diagram"
      },
      "policy": {
        "installation": "AVAILABLE",
        "authentication": "ON_INSTALL"
      },
      "category": "Productivity"
    }
  ]
}
```

3. Khởi động lại ứng dụng, chọn marketplace `Thien Private Plugins` trong Plugins Directory, cài plugin rồi mở chat mới.

`source.path` tính từ repository root, không từ thư mục chứa JSON. Xem [OpenAI — Package your plugin](https://developers.openai.com/plugins/build/plugins). Nếu host không có route marketplace phù hợp, không giả định upload ZIP vào chat sẽ cài plugin.

Codex CLI dùng `/plugins` cho marketplace đã cấu hình; IDE extension không hỗ trợ plugin, nên dùng gói Universal. Các bề mặt và chính sách có thể thay đổi, xem [OpenAI — Plugins](https://learn.chatgpt.com/docs/plugins). Repository audit này không tự trở thành public marketplace.

### Sau khi cài

Kiểm tra skill xuất hiện đúng ID/tên hiển thị và chỉ có một bản đang được chọn. Nếu bạn muốn kiểm tra sử dụng, chạy prompt minh họa ở mục [Gọi skill](#gọi-skill) rồi đối chiếu [Đầu ra và giới hạn](#đầu-ra-và-giới-hạn).

Các lệnh ở README là hướng dẫn cho người cài, không phải bằng chứng chúng đã được thực thi trên host của bạn. Build-time package verification không thay cho xác minh tích hợp ở môi trường thực tế.

### Giấy phép

Phiên bản này chịu sự điều chỉnh của **Tran Ngoc Thien's Skill Commercial Source-Available License 2.0**:

- đây là giấy phép thương mại nguồn có thể xem, **không phải giấy phép nguồn mở**;
- bản tiếng Việt được ưu tiên áp dụng;
- quyền truy cập, clone, tải xuống hoặc nhận bản sao không tự cấp quyền cài đặt, thực thi, sửa đổi, phân phối hay cung cấp dịch vụ;
- quyền sử dụng chỉ phát sinh theo Paid Order, Written Permission/email hoặc Commercial Agreement hợp lệ;
- logo, crest, tên, nhãn hiệu và goodwill TDTN bị loại khỏi quyền cấp chung và cần văn bản cho phép riêng;
- liên hệ cấp quyền: `thien.8888@gmail.com`.

Đọc đầy đủ trước khi sử dụng:

- [`LICENSE.md`](LICENSE.md) — bản license 2.0 ở root repository, byte-identical với bản trong skill
- [`thien-skill-creative-diagram/LICENSE-APPLICATION.md`](thien-skill-creative-diagram/LICENSE-APPLICATION.md)
- [`thien-skill-creative-diagram/NOTICE`](thien-skill-creative-diagram/NOTICE)
- [`thien-skill-creative-diagram/THIRD_PARTY_NOTICES.md`](thien-skill-creative-diagram/THIRD_PARTY_NOTICES.md)
- [`thien-skill-creative-diagram/SOURCE_MANIFEST.json`](thien-skill-creative-diagram/SOURCE_MANIFEST.json)
- [`thien-skill-creative-diagram/ASSET_MANIFEST.json`](thien-skill-creative-diagram/ASSET_MANIFEST.json)

Release `2.5.0` đã có owner legal/brand/provenance approval theo D-202 trên exact legal/provenance aggregate SHA-256 `96f611803df589e7dadd75287237dfc6eb3a98380ef78f4fcfb68ea731356227`, bằng explicit owner risk-accepted waiver. Chưa có independent Vietnamese counsel review; không tuyên bố lawyer-reviewed. Approval này dành riêng cho bytes đã phát hành, không phải kế thừa tự động từ `2.0.0` hoặc cho phép sửa license/brand.

### Provenance

`diagram-design` là nguồn chức năng chủ đạo ở mức taxonomy, hành vi và yêu cầu trừu tượng. Repository này là **clean-room-oriented independent reimplementation**: không sao chép code, prose, CSS, template, script, specimen hoặc asset upstream. `Thien-UI-UX-Ultra` chỉ được dùng ở mức nguyên tắc và workflow.

Chi tiết nằm trong [SOURCE_MANIFEST.json](thien-skill-creative-diagram/SOURCE_MANIFEST.json), [THIRD_PARTY_NOTICES.md](thien-skill-creative-diagram/THIRD_PARTY_NOTICES.md) và evidence đã chốt trong [PROJECT.md](PROJECT.md).

### Tính toàn vẹn bản phát hành và phiên bản cũ

- Tag `v2.5.0` trỏ release commit `99c179155c8bccc5f0da3e29fea81a72a660439d`; năm artifact trong bảng là exact bytes đã được phê duyệt và phát hành.
- `packaging-report.json` giữ provenance tại lúc build: `release_notes_sha256` trỏ source notes khi còn là candidate và trạng thái G-06 trong report là trạng thái khi đó. Owner approval G-06 đã hoàn tất sau đó; xem Release body và PROJECT, không sửa report để viết lại lịch sử.
- README này được cập nhật **sau phát hành** để hướng dẫn sử dụng `2.5.0`. Nó không thay README tại tag, ZIP, checksum hoặc Release body đã khóa.
- [Release v2.0.0](https://github.com/thiendeptrainhat/Thien-Skill-Creative-Diagram/releases/tag/v2.0.0) và [Release v1.0.0](https://github.com/thiendeptrainhat/Thien-Skill-Creative-Diagram/releases/tag/v1.0.0) vẫn là các bản lịch sử. Các artifact trong repository được xếp theo thư mục phiên bản như bảng dưới; tám file cũ chỉ đổi thư mục chứa, giữ nguyên tên, nội dung và SHA-256. Tag và GitHub Release cũ không thay đổi.

| Thư mục phiên bản | Bộ cài | File kiểm tra |
|---|---|---|
| [`dist/1.0.0/`](dist/1.0.0/) | [Claude](dist/1.0.0/thien-skill-creative-diagram-1.0.0-claude-plugin.zip) · [OpenAI](dist/1.0.0/thien-skill-creative-diagram-1.0.0-openai-plugin.zip) · [Universal](dist/1.0.0/thien-skill-creative-diagram-1.0.0-universal-raw-skill.zip) | [SHA256SUMS.txt](dist/1.0.0/SHA256SUMS.txt) |
| [`dist/2.0.0/`](dist/2.0.0/) | [Claude](dist/2.0.0/thien-skill-creative-diagram-2.0.0-claude-plugin.zip) · [OpenAI](dist/2.0.0/thien-skill-creative-diagram-2.0.0-openai-plugin.zip) · [Universal](dist/2.0.0/thien-skill-creative-diagram-2.0.0-universal-raw-skill.zip) | [SHA256SUMS-2.0.0.txt](dist/2.0.0/SHA256SUMS-2.0.0.txt) |
| [`dist/2.5.0/`](dist/2.5.0/) | [Claude](dist/2.5.0/Thien-Skill-Creative-Diagram-v2.5.0-Claude.zip) · [ChatGPT](dist/2.5.0/Thien-Skill-Creative-Diagram-v2.5.0-ChatGPT.zip) · [Universal](dist/2.5.0/Thien-Skill-Creative-Diagram-v2.5.0-Universal.zip) | [SHA256SUMS](dist/2.5.0/SHA256SUMS) · [packaging-report.json](dist/2.5.0/packaging-report.json) |

Chạy kiểm tra checksum từ bên trong thư mục phiên bản tương ứng. Hai bản cũ giữ tên ZIP/checksum lịch sử và không có `packaging-report.json`; không tạo lại artifact chỉ để đồng nhất tên. Không dùng checksum của phiên bản khác cho ZIP `2.5.0`.
