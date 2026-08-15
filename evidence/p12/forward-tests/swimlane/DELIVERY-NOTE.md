# Ghi chú bàn giao

- Đã giao `swimlane-thu-tien.html` và `swimlane-thu-tien.svg`: swimlane ngang, sáu đơn vị, giữ đủ 10 bàn giao và các nhãn tiếng Việt từ ngữ nghĩa nguồn.
- Thiết kế độc lập: bố cục lane ngang theo năm pha, vector/hình dạng/tokens nguyên bản; ảnh tham khảo chỉ là dữ liệu QA, không được nhúng, trace hoặc đóng gói.
- PNG: không có rasterizer cài sẵn thuộc danh sách được phép của skill; không cài thêm. SVG độc lập là fallback minh bạch và có thể rasterize về sau.
- QA tĩnh: semantic, SVG, HTML/no-JS/print/reduced-motion, contrast, fidelity, Unicode và determinism đều `PASS`. Browser live bị chặn bởi chính sách URL `file://` của browser cục bộ.
- Chi tiết hash và trạng thái nằm trong `artifact-ledger.json`.
