# Thien-Skill-Creative-Diagram — trạng thái và quản trị

**Chủ sở hữu:** Tran Ngoc Thien  
**Cập nhật:** 2026-08-31  
**Phiên bản hiện hành:** `2.0.0`  
**Trạng thái:** released/private; D-139 đã commit/push lên `main`; không có phase mutation đang được phép

File này là nguồn sự thật duy nhất cho phạm vi, trạng thái, gate và quyết định còn hiệu lực. Lịch sử chi tiết nằm trong Git và evidence đã khóa; không tái tạo thêm plan, roadmap, handoff hoặc decision file ở root.

## 1. Mục tiêu sản phẩm

Tạo một skill provider-neutral có khả năng thiết kế diagram chuyên nghiệp, chính xác về ngữ nghĩa, hỗ trợ tiếng Việt và phát hành dưới ba envelope Claude, OpenAI và Universal từ một canonical source.

- Tên hiển thị: `Thien-Skill-Creative-Diagram`.
- Technical ID/folder/plugin ID: `thien-skill-creative-diagram`.
- Nguồn chức năng chủ đạo: `diagram-design`.
- Phương pháp: **clean-room-oriented independent reimplementation**.
- `Thien-UI-UX-Ultra` chỉ dùng ở mức nguyên tắc và workflow.

## 2. Trạng thái có thẩm quyền

- P-00 đến P-21: `passed`.
- Historical v1.0.0 gates G-00…G-07: `PASS`.
- Source/gallery lineage 1.5.0: G-01, G-02, G-03, G-04 `PASS`; G-05/G-06/G-07 không dùng cho release line này.
- Target v2.0.0 gates G-00…G-07: `PASS`.
- P-21 private release execution: `PASS` theo D-133.
- Current authorization: không có. One-time authorization cho D-139 đã được sử dụng và hết hiệu lực sau khi commit `dee8c5c6d0722fd0ae61648a385d4f5493e79171` được push thành công lên `origin/main`. Package mutation, dist mutation, publication, commit, push, tag và Release chưa được phép.

## 3. Release bindings

Repository: private `thiendeptrainhat/Thien-Skill-Creative-Diagram`, default branch `main`.

Workspace gốc là canonical Git worktree; không duy trì nested release clone hoặc snapshot toàn cây trong workspace. Historical bytes đã được Git lưu tại `origin/main` commit `e1d685a57a38b101f674018687c128d7b3d7b0d9` và các release tag tương ứng.

Release v2.0.0:

- URL: `https://github.com/thiendeptrainhat/Thien-Skill-Creative-Diagram/releases/tag/v2.0.0`;
- release commit: `7f6165ffb60b75a65ffce51bf382ccb35529095f`;
- annotated tag object: `6dfd116c4a770d45508ca7bd93bbe6ec61796abe`;
- tag peels đúng release commit;
- non-draft, non-prerelease;
- remote asset digests:
  - checksum `96246d4d62153b82c9e3505ebe904433225f15b106e002d026fa069e8a4a8f17`;
  - Claude `7ef52b21be9dcc96caae5621e7788f9eb31cd46ae26ef94e47e3a75889ce99f6`;
  - OpenAI `65c2d6fbc33dc6d3065c5d6ae44a5b4fe02e5f7e8838b7f05eede07766124315`;
  - Universal `88e22caee1f7df7ff8893dbd5cb461c6117921765e56c349e3da6c6452f15f93`.

Historical Release v1.0.0 và bốn exact asset digest phải được bảo toàn; không di chuyển tag hoặc thay asset nếu chưa có authorization release mới.

## 4. Bất biến sản phẩm và QA

- Exact P-18R6 review-17 đã owner-approved; manifest SHA-256 `7925c1ab0515a59057851bb3888ff4d9974e5f5701b873b1f11468a5fd64a03a`.
- Exact P-19B review-45 và P-19C review-01 đã owner-approved.
- P-18 và P-19 là hai tập artifact riêng biệt: đúng 14 P-18 + 93 P-19 = 107 diagram trong combined comparison.
- P-19 không được thay thế, ghi đè, tái sinh hoặc loại bỏ P-18.
- Catalog công khai không phân biệt P-18/P-19; lineage phase chỉ được giữ trong provenance/QA nội bộ. Target D-136 là 14 anchor × 3 mode + 31 gallery identity × 3 mode = 135 sample, không làm thay đổi baseline approval 107.
- Exact catalog có 45 diagram identity; mỗi identity gồm đúng ba version `neutral-light`, `neutral-dark` và `editorial`. Cả ba version ngang cấp, cùng trạng thái owner-approved; không version nào là mặc định, chính, phụ, fallback hoặc có quyền ưu tiên cao hơn version khác.
- 31 masked silhouette chỉ là mẫu QA, không phải registry, catalog, template hoặc output cố định.
- Yêu cầu rõ ràng của người dùng có precedence; implementation phải thay đổi diagram, nội dung, cấu trúc, layout, visual treatment và presentation khi yêu cầu an toàn và phù hợp ngữ nghĩa.
- Static HTML/SVG phải giữ đủ nghĩa; không truyền trạng thái quan trọng chỉ bằng màu.
- Không tự cập nhật golden/benchmark để làm test xanh.

## 5. Legal, provenance và package

- License: `Tran Ngoc Thien's Skill Commercial Source-Available License 2.0`; không phải open source.
- Exact v2 legal aggregate: `93643da0d3183db68f1f70730840bd1bcae5935b130e405179f14284501f29c0`.
- G-06@2.0.0 dùng owner waiver cho exact version/hash; không có independent Vietnamese-lawyer review và không được tuyên bố là lawyer-reviewed.
- Không sao chép code, prose, CSS, template, script, specimen, gallery, font file hoặc asset upstream.
- Không đưa benchmark QA-only, đường dẫn máy cá nhân, secret hoặc dependency ngầm vào package/publication.
- Ba package phải được sinh xác định từ một canonical source và giữ logical runtime/legal parity.

## 6. Gate tối thiểu cho thay đổi sau release

Mọi maintenance/release mới phải đánh giá đúng các gate bị ảnh hưởng:

- G-00 governance/scope;
- G-01 source/provenance;
- G-02 product/design/test contract;
- G-03 semantic/visual direction;
- G-04 functional, security, accessibility và visual QA;
- G-05 package parity/install/smoke;
- G-06 legal/brand/provenance approval;
- G-07 exact owner approval, private-target preflight và release authorization.

Không được bù hard failure về security, semantic, numeric integrity, accessibility nghiêm trọng, provenance, package install hoặc legal bằng điểm thẩm mỹ. `DEFERRED` không tương đương `PASS`.

## 7. Quy trình thay đổi

1. Ghi scope/version/authorization hiện hành vào section 2 trước mutation vật chất.
2. Chỉ sửa đúng scope; bảo toàn frozen artifacts và thay đổi của người dùng.
3. Chạy kiểm chứng tương ứng và cập nhật section 8 bằng đường dẫn/hash.
4. Cần owner approval riêng khi thay legal, brand, golden, package hoặc release candidate.
5. Commit/push/tag/Release chỉ thực hiện khi yêu cầu hiện hành cho phép rõ ràng.
6. Sau closure, đặt current authorization về “không có”; không để phase `in-progress` giả.

## 8. Evidence hiện hành

- P-18: `evidence/p18/P-18R6-EVIDENCE.md` và `evidence/p18/G-03-1.5.0-EVIDENCE.md`.
- P-19: `evidence/p19/P-19B-EVIDENCE.md`, `evidence/p19/P-19C-EVIDENCE.md`, `evidence/p19/G-04-1.5.0-EVIDENCE.md`.
- P-20: `evidence/p20/P-20-EVIDENCE.md`, `evidence/p20/RELEASE-CANDIDATE-2.0.0.json`; duplicate local `candidate-dist` đã được D-138 loại bỏ sau khi exact bytes được promotion vào `dist/`, release asset và Git history.
- P-21: `evidence/p21/P-21-EVIDENCE.md`, `evidence/p21/RELEASE-EVIDENCE.json`.
- Sample library D-136/D-137: `assets/index.html` dẫn tới đúng 135 HTML trong một namespace `assets/diagrams/`; `screenshots/diagrams/` chứa đúng 135 PNG cùng basename. Phân bổ đúng 45 identity × 3 mode: neutral-light, neutral-dark và editorial; exact 135 đã được owner-approved, ba mode ngang cấp. Static QA xác nhận 135 unique detail link, 0 broken link, 0 basename mismatch, 0 empty/invalid PNG; 14 anchor neutral-light và 93 gallery specimen giữ exact approved SVG, 93 specimen giữ visual stylesheet đã duyệt, còn 28 variant anchor mới giữ đồng nhất geometry/text qua ba mode. Browser QA desktop/mobile xác nhận filter/search, 135/135 image load, 0 visible phase label, 0 horizontal page overflow, 0 browser error; full render sweep xác nhận 0 unstyled default-black visible shape và 28 variant mới không có failure. Canonical regression: 414/414 PASS.
- Pre-release verification: 15/15 PASS; package QA: 26/26 PASS; canonical regression: 414/414 PASS; sanitized mirror: 5/5 PASS.
- Historical snapshot/review paths được nhắc trong frozen evidence là binding theo thời điểm tạo evidence, không phải live workspace dependency. D-138 chuyển custody của các bytes superseded này sang Git commit `e1d685a57a38b101f674018687c128d7b3d7b0d9`; final manifest, exact source/gallery, review-45, P-19C và release evidence vẫn ở live tree.
- Repository cleanup D-138: canonical Git metadata đã được đưa về workspace root; `HEAD` và `origin/main` cùng trỏ `e1d685a57a38b101f674018687c128d7b3d7b0d9`, tag `v2.0.0` vẫn peel đúng `7f6165ffb60b75a65ffce51bf382ccb35529095f`. Đã loại bỏ 41.806 file trùng/superseded/rác, giảm workspace từ khoảng 3,8 GiB xuống 100 MiB gồm 54 MiB Git metadata. Post-cleanup QA: 135 HTML + 135 PNG, 0 basename mismatch; P-18/P-19 exact manifest hash giữ nguyên; bốn v2 dist digest khớp; canonical regression 414/414 PASS; Git fsck và diff whitespace PASS; 0 cache/`.DS_Store`; không có staged change.
- D-139 maintenance candidate: exact working tree gồm 20.312 path change — 20.037 deletion (20.030 historical/superseded evidence và bảy root governance file), một modification (`AGENTS.md`) và 274 addition (`PROJECT.md`, `.gitignore`, 136 asset HTML, 135 PNG screenshot và một canonical sample-library builder). Audit đã loại bỏ accidental personal-machine paths khỏi 24 live evidence/script file bằng placeholder trung lập trước khi chốt candidate; package/dist không đổi. QA: canonical regression 414/414 PASS; catalog check 45 identity × 3 mode = 135 HTML và 135/135 PNG hợp lệ; P-18 exact manifest SHA-256 `7925c1ab0515a59057851bb3888ff4d9974e5f5701b873b1f11468a5fd64a03a`; P-19 current gallery/freeze manifests có đủ live dependency, còn missing path trong frozen source manifest chỉ thuộc governance/review lịch sử đã được D-138 chuyển custody sang Git; bốn v2 dist digest khớp D-133; JSON 126/126 parse; root allowlist, secret/personal-path scan, symlink/runtime-junk scan và Git fsck PASS. Staged `git diff --check` chỉ báo trailing spaces đã có trong exact owner-approved/generated catalog HTML và ba Markdown hard-break; giữ nguyên catalog bytes để không làm drift exact approval, không có patch corruption khác. Trước execution index chưa stage; sau owner authorization exact 20.312 path đã được stage. `skill-creator` canonical `quick_validate.py` không thể nạp do runtime thiếu PyYAML, nhưng kiểm tra tương đương toàn bộ rule của validator và parse `agents/openai.yaml` đều PASS.

## 9. Quyết định còn hiệu lực

- D-126: owner-approved exact P-19B review-45; khóa coexistence 14 + 93 = 107 và cấm P-19 substitution.
- D-128: owner-approved P-19C; 31 silhouette là sample-not-fixed, user-request flexibility bắt buộc.
- D-129: `G-04@1.5.0 PASS`.
- D-131: owner-approved exact v2 legal/package/release candidate; G-06 dùng owner waiver, không phải lawyer review.
- D-132: authorize exact private release v2.0.0.
- D-133: P-21/release v2.0.0 hoàn tất và remote digests verified; không cấp maintenance authorization.
- D-134: owner yêu cầu tinh gọn quản trị và cấm tạo file rác/cẩu thả. Root governance được hợp nhất thành `AGENTS.md` + `PROJECT.md`; file superseded bị xóa, lịch sử dùng Git/evidence thay vì nhân bản.
- D-135: completed historical baseline. Bộ public copy 107 diagram đã được D-136 supersede; exact approved source và provenance 14 + 93 vẫn được bảo toàn trong evidence, sample library không tạo fixed-output constraint.
- D-136: implementation và technical QA completed. Catalog công khai hợp nhất đúng 135 sample, không lộ phase namespace; 14 anchor đã đủ ba mode và public folder cũ theo phase đã được loại bỏ. Baseline approval 14 + 93 = 107 không thay đổi. Quyết định này không cấp package, dist, publication, commit, push, tag hoặc Release.
- D-137: owner-approved exact unified catalog gồm 45 diagram identity × 3 version = 135 diagram. `neutral-light`, `neutral-dark` và `editorial` ngang cấp tuyệt đối; không mode nào là mặc định, chính, phụ, fallback hoặc ưu tiên hơn mode khác. Approval này đóng owner visual approval còn thiếu của 28 variant D-136 nhưng không cấp package, dist, publication, commit, push, tag hoặc Release.
- D-138: completed. Canonical Git worktree đã được hợp nhất tại root; release staging, snapshot history trùng lặp, review superseded, withdrawn artifacts, duplicate candidate-dist và rác runtime/file hệ thống đã bị xóa sau quarantine QA. Exact source/catalog 135 diagram, final evidence, release tags/digests và owner changes được bảo toàn; `.gitignore` ngăn rác tái phát. Không commit, push, tag, Release hoặc publication.
- D-139: completed. Owner-approved exact maintenance candidate theo inventory fingerprint SHA-256 `ce82e433cd774ab2bdffebe614fc1de08e072b832eb7b4a14010e061e0d73744`, sau đó cho phép stage/commit/push. Exact candidate được commit tại `dee8c5c6d0722fd0ae61648a385d4f5493e79171` và đã được xác minh trên `origin/main`; one-time authorization đã hết hiệu lực. Candidate hợp nhất governance, catalog 135 sample và cleanup D-138; không thay package/dist, release tag hoặc Release.

## 10. File policy

Root file allowlist: `AGENTS.md`, `PROJECT.md`, `README.md`, `LICENSE.md`, `.gitignore`, cộng file cấu hình kỹ thuật thật sự bắt buộc bởi runtime/tool.

Mọi file mới phải có:

1. consumer cụ thể;
2. lý do không thể dùng file hiện hữu;
3. vị trí đúng;
4. vòng đời và điều kiện xóa;
5. kiểm chứng tương ứng.

Thiếu một điều kiện thì không tạo file. Các tên kiểu `FINAL`, `NEW`, `COPY`, `BACKUP`, `TEMP`, `NOTES`, `STATUS`, `HANDOFF`, `PLAN` hoặc `ROADMAP` không phải lý do tạo artifact mới.
