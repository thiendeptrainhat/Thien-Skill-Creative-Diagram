# P-18R5 evidence — Master visual kernel + Swimlane anchor

**Ngày:** 2026-08-24  
**Authority:** D-051, D-052, D-054, D-055, D-056, D-057, D-058  
**Trạng thái:** `passed / owner-approved`  
**Gate:** `G-03@1.5.0 NOT-EVALUATED`

## Kết quả

P-18R5 đã remediate hairline gap tại hai straight-to-hop join trên canonical visual kernel QA-only và tái sinh đúng một Swimlane `neutral-light` anchor. Exact review-04 được đóng băng theo D-057, sau đó được chủ sở hữu phê duyệt theo D-058; P-18R5 `passed` nhưng P-18 tổng thể vẫn `in-progress`. Kết quả này khóa anchor/visual direction của P-18R5, không tự làm `G-03@1.5.0` `PASS`, không cấp quyền P-18R6/P-19 và không thay đổi package hay release.

Review-01/review-02/review-03 được bảo toàn bất biến dưới `evidence/p18/r5/history/`; original manifest SHA-256 lần lượt là `519aad808b0123a6f809403f0d6678f44e9633c99ce3ceed1397be9f69efe6e1`, `3d4caf5336e1ab7b087d7c03074f645c47aad197b50b2a4ebddca6c820035bf0` và `0e4c047c0254228a9e43ce98f87901b4d6e7a4e1bf845bd6d3906684cfae031e`. Ba lineage record đều ghi finding của owner và trạng thái historical-superseded-for-owner-approval.

Exact frozen binding:

- manifest: `evidence/p18/r5/P-18R5-MANIFEST.json`;
- manifest ID: `P18R5-MASTER-KERNEL-SWIMLANE-ANCHOR-REVIEW-04-1.5.0`;
- manifest SHA-256: `7725a03c82c370f6d9bb984b0d6e50c585efb07529a47f2c3dfad45877c1cca8`;
- source bundle SHA-256: `45da46ef6fc80982c83cb63b7212f11c06973d093f4a317b236e782df738e10b`;
- artifact bundle SHA-256: `0113f957e24776fd5b70e08873a791c722993a0c00bd015aa6612a5b5089f004`;
- lineage bundle SHA-256: `1956483c362072ade76e9fde85da3cf38061b7f3d9ac06f9f3007b612b1ba36f`;
- anchor HTML SHA-256: `8ef26083752d829017abca9e162261ed4a1579cc7e8a604dc6e11cc77b96421f`;
- anchor SVG SHA-256: `a0d3949d177daebca0c84070b18d8366a025025261d03a7e03896550beb8253c`;
- review PNG SHA-256: `f16d30a070f34e9a6e3601b0ef06dd070e8fc3995ec58b6c94537ecd7c4c6e54`.

## Owner approval hậu-freeze

Ngày 2026-08-24, chủ sở hữu Tran Ngoc Thien phê duyệt đúng manifest ID `P18R5-MASTER-KERNEL-SWIMLANE-ANCHOR-REVIEW-04-1.5.0` với manifest SHA-256 `7725a03c82c370f6d9bb984b0d6e50c585efb07529a47f2c3dfad45877c1cca8` theo D-058. Phê duyệt bao gồm visual result sau remediation crossing/hop và straight-to-hop continuity, đồng thời đóng P-18R5 ở trạng thái `passed`.

Manifest đã được freeze trước quyết định nên các trường owner approval bên trong manifest vẫn ghi trạng thái pre-approval `PENDING`. Giữ nguyên các byte này là chủ ý để bảo toàn exact candidate; D-058, record này và `PLAN.md` là hồ sơ phê duyệt hậu-freeze có thẩm quyền. Không sửa candidate để tự ghi approval vào manifest.

## Foundation được chứng minh

- Font resolver khóa thứ tự: explicit user font trước; default stack chỉ dùng khi người dùng không chọn font. Missing explicit user font fail-closed nếu không có fallback được chấp thuận.
- Default preferred stack là Instrument Serif / Geist / Geist Mono. Máy QA không có các font preferred nên receipt công khai fallback thực tế: Georgia / Avenir Next / Menlo. Không tải, cài, nhúng hoặc đóng gói font.
- Layout dùng đo glyph thực tế, measured title ideal width và local stage-width budget trước khi wrap; balanced wrapping chặn short-word orphan có thể tránh được. Hai title bị owner chỉ ra hiện đều single-line, không giảm cỡ chữ.
- Swimlane dùng engine `lane-interaction`, stage rail, lane chrome, card anatomy, content-fit artboard, rounded orthogonal routes, boundary-port allocation và label clearance. Ba crossing bất khả tránh có true hop tích hợp trực tiếp vào connector path; route/repaint dùng exact shared cubic geometry; 11px underlay chỉ che central crown và cách join gần nhất `16.26px`. Không còn shoulder hairline, straight chord dưới hop, compound wave, bubble/junction hay source-port dot.
- Locked semantic IR `P18-C02-SWIM` được chiếu đủ 12/12 semantic node và 10/10 semantic edge, mỗi phần tử đúng một lần.
- Visible SVG không có duplicate page title hay evidence rail; semantic field cùng legend chiếm `0.8824257` artboard.

## Verification

| Lớp kiểm tra | Kết quả |
|---|---|
| Focused semantic/font/contrast/geometry/routing/security/determinism | `16/16 PASS` |
| Browser QA ở canonical, desktop và mobile | `3/3 PASS` |
| Full canonical regression | `148/148 PASS` |
| Implementer engineering visual precheck | `95.5/100`; mọi dimension `>=4/5` |
| Independent visual-craft gate | `PENDING` |
| Owner visual approval | `PASS` theo D-058 |

Implementer precheck không độc lập và không thay thế independent visual-craft gate. Owner approval theo D-058 chỉ đóng P-18R5; `G-03@1.5.0` vẫn `NOT-EVALUATED`.

Các finding của review-01/review-02/review-03 và lỗi kỹ thuật phát hiện trong vòng kiểm tra được sửa tại kernel/validator rồi sinh lại candidate; không vá tay output. Focused QA kiểm tra path-integrated hop, route/repaint identity, crown-only underlay, corridor/pitch rule và adaptive node width; browser QA kiểm tra minimum join clearance `16.26px`, zero gap-mask, absence of port dot và targeted single-line titles.

## Provenance và scope

- Mô hình: **clean-room-oriented independent reimplementation**.
- Chỉ tái sử dụng locked semantic IR từ P-18R4 theo phạm vi được duyệt.
- Không tái sử dụng visual source của candidate P-18R3 đã bị từ chối.
- Không sao chép code, CSS, SVG, template, asset hoặc font upstream; so sánh upstream chỉ bằng rubric trừu tượng.
- Không sửa canonical runtime, gallery cũ, package, `dist/`, publication mirror, Git, tag hoặc Release.
- P-18R6 và P-19 vẫn chưa được phép.

## Điểm dừng bắt buộc

P-18R5 đã đóng theo D-058. Bước khả dĩ tiếp theo chỉ là P-18R6 nếu và khi chủ sở hữu cấp authorization riêng; nếu chưa có authorization đó thì dừng.
