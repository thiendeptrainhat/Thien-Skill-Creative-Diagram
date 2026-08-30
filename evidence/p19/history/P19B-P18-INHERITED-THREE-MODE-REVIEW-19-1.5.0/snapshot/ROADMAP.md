# Roadmap — Thien-Skill-Creative-Diagram v1.0.0 baseline / v1.5.0 source-gallery target

File này chỉ mô tả **thứ tự milestone và kết quả cấp cao**. Trạng thái có thẩm quyền và checklist nằm duy nhất trong `PLAN.md`; điều kiện pass/fail nằm trong `PHASE-GATES.md`.

## Luồng milestone

```mermaid
flowchart LR
    M0["M0 · Governance lock"] --> M1["M1 · Evidence & contract"]
    M1 --> M2["M2 · Canonical core"]
    M2 --> M3["M3 · Semantic core & visual pilot"]
    M3 --> M4["M4 · Full coverage, import, export & motion"]
    M4 --> M6["M6 · Independent QA & goldens"]
    M1 --> M5["M5 · Brand, legal & provenance"]
    M3 --> M5
    M5 --> M7["M7 · Three packages"]
    M6 --> M7
    M7 --> M8["M8 · Private v1.0.0 release"]
    M8 --> M9["M9 · Controlled maintenance"]
    M9 --> M10["M10 · v1.5 upstream delta & contract"]
    M10 --> M11["M11 · 39-type semantic source"]
    M11 --> M12["M12 · Visual vNext pilot gallery"]
    M12 --> M13["M13 · Full 39-type source/gallery"]
```

## Milestone map

| Milestone | Phase trong `PLAN.md` | Kết quả cấp cao | Gate chính |
|---|---|---|---|
| M0 — Governance lock | P-00 | Nguồn sự thật, kế hoạch và quy tắc vận hành được khóa; chưa triển khai. | G-00 |
| M1 — Evidence & contract | P-01 đến P-02 | Snapshot, provenance, taxonomy, product contract, design contract và test contract được duyệt. | G-01, G-02 |
| M2 — Canonical core | P-03 đến P-04 | Một skill core provider-neutral có router và IR rõ ràng. | Đóng góp G-03 |
| M3 — Semantic core & visual pilot | P-05 đến P-06 | Đủ semantic contract/grammar; visual system nguyên bản được chứng minh bằng pilot và golden direction. | G-03 |
| M4 — Full coverage, import, export & motion | P-07 đến P-08 | Visual coverage đạt toàn bộ inventory; input pipeline, safe import, portable output và static-first motion hoàn chỉnh. | G-04 |
| M5 — Brand, legal & provenance | P-09 đến P-10 | Logo derivative được duyệt; license/provenance candidate sẵn sàng cho luật sư. | G-06 |
| M6 — Independent QA & goldens | P-11 đến P-12 | Benchmark E2, hard checks, goldens và forward tests đạt yêu cầu. | G-04 |
| M7 — Three packages | P-13 | Claude, OpenAI/ChatGPT và Universal được build xác định từ cùng source. | G-05 |
| M8 — Private v1.0.0 release | P-14 | Chủ sở hữu xác nhận đủ approval/evidence, duyệt release candidate và ra lệnh push private repo. | G-07 |
| M9 — Controlled maintenance | P-15 | Ngoài completion scope v1.0.0; mỗi update lặp các gate bị ảnh hưởng. | Lặp G-01–G-07 theo release |
| M10 — v1.5 upstream delta & contract | P-16 | Exact upstream snapshot, delta 27→39, bốn capability và source/gallery contract đã được owner duyệt; P-16 đóng theo D-047. | G-01@1.5.0, G-02@1.5.0 PASS |
| M11 — 39-type semantic source | P-17 | Canonical source/router/IR/grammar/test đã triển khai contract G-02 cho 39 type và bốn capability mới; P-17 đã đóng theo D-048. | Đóng góp G-04@1.5.0 |
| M12 — Visual vNext foundation & pilot | P-18R4→P-18R6 | Relock contract/foundation, chứng minh canonical kernel bằng Swimlane anchor rồi một `neutral-light` anchor cho đủ 14 layout engine; owner duyệt exact candidate trước khi nhân rộng. | G-03@1.5.0 |
| M13 — Full 39-type source/gallery | P-19A→P-19C | Type adapters cho 39+4; gallery theo D-085/D-095–D-099 giữ 14 P-18 anchor và 90 P-19 HTML (gồm Layers variant, detailed line-chart, five-stage medallion, eight-window polar-chart và detailed Wardley map), sau đó full QA/freeze/owner review. | G-04@1.5.0 |

## Nguyên tắc tiến tuyến

- Không đi tiếp chỉ vì phase trước “gần xong”; phải có evidence và gate record.
- Có thể làm song song các workstream độc lập khi `PLAN.md` cho phép, nhưng không vượt gate phụ thuộc.
- Không rút ngắn QA, provenance hoặc legal gate để đạt mốc release.
- Mọi thay đổi phạm vi phải quay lại `PROJECT-CONTRACT.md` trước khi cập nhật roadmap.
- M10/P-16 và M11/P-17 đã hoàn tất. M12/P-18R0→P-18R3 chỉ còn historical evidence vì owner từ chối replacement direction theo D-051; P-18R4 contract/foundation relock và P-18R5 master kernel đã hoàn tất. Exact P-18R6 review-17 manifest SHA-256 `7925c1ab0515a59057851bb3888ff4d9974e5f5701b873b1f11468a5fd64a03a` đạt static `366/366`, browser `42/42`, regression `148/148`, masked recognition/five-second `14/14` và independent visual-craft `93/100`, minimum dimension `4/5`. Owner phê duyệt exact review-17, `G-03@1.5.0 PASS` và đóng P-18/M12 theo D-077. M13/P-19A→P-19C vẫn chưa được phép theo cùng quyết định.
- Roadmap v1.5.0 hiện dừng tại M13/source-gallery; không có milestone package, commit, push, tag hoặc release được phép.

**Current authoritative status:** xem `PLAN.md`.
