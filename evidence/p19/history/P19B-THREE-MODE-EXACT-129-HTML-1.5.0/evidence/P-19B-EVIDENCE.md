# P-19B evidence — three-mode derivation and exact 129 HTML

**Candidate:** `P19B-THREE-MODE-EXACT-129-HTML-1.5.0`  
**Authority:** D-079  
**Status:** `passed`  
**Date:** 2026-08-27

## Delivered

- Canonical renderer: `thien-skill-creative-diagram/scripts/gallery_renderer_v15.py`.
- Generated renderer registry: `thien-skill-creative-diagram/references/gallery-renderer-v15.json`.
- Focused tests: `thien-skill-creative-diagram/scripts/tests/test_gallery_renderer_v15.py`.
- Exact gallery: `evidence/p19/gallery/`.
- Exactly 129 standalone HTML specimens under `evidence/p19/gallery/specimens/`:
  - 39 canonical types × three modes = 117;
  - four capabilities × three modes = 12.
- One separate `index.html` contact sheet, not counted as a specimen.
- 43 local neutral-light SVG previews used by the contact sheet; these are navigation previews, not additional specimens.
- Inventory, gallery manifest, design contract, provenance and focused static/browser evidence.

## Renderer and derivation contract

- Every specimen is produced only after `validate_semantics` and `adapt_visual` succeed.
- All 43 adapter identities retain the exact P-19A layout-engine and unique silhouette binding; no generic or unknown fallback exists.
- `neutral-light`, `neutral-dark` and `editorial` use the inherited semantic tokens.
- After mode-specific IDs are normalized, SVG markup/geometry is identical across all three mode derivations for each fixture.
- Every HTML file is scriptless, network-independent and opens without a build step.
- Each document contains machine-readable fixture/type/capability/parent/mode/engine/silhouette/check metadata, one named inline SVG, a responsive/print/reduced-motion contract and an alternative semantic-ID table.

## Verification

- Focused renderer unit suite: `11/11 PASS`.
- Focused static gallery verification: `22/22 PASS`.
- Full canonical regression: `173/173 PASS`.
- Desktop browser: `129/129 PASS` at `1440×1000`; zero metadata, body-overflow, SVG naming, duplicate-ID or rendered SVG text-containment failure.
- Mobile browser engine-mode matrix: `42/42 PASS` at `390×844` — one specimen per 14 engine per three modes; zero body overflow and wide diagrams remain contained by the artifact scroll region.
- Contact sheet browser: 43 cards, 129 links, 43 preview images, zero iframe, zero console error/warning and zero body overflow.
- Native disclosure receives visible `3px solid` focus; reduced-motion rule is present; direct specimen browser tab has zero console error/warning.
- Deterministic memory regeneration matches all 129 recorded specimen hashes.
- Gallery manifest verifies 175 records: 129 specimen HTML, 43 preview SVG, `index.html`, inventory and renderer registry.

Machine-readable results:

- `evidence/p19/P-19B-STATIC-VERIFICATION.json`
- `evidence/p19/P-19B-BROWSER-VERIFICATION.json`
- `evidence/p19/P-19B-PLAN-MANIFEST.json`
- `evidence/p19/P-19B-SOURCE-MANIFEST.json`
- `evidence/p19/gallery/P-19B-INVENTORY.json`
- `evidence/p19/gallery/P-19B-MANIFEST.json`

## Integrity and boundaries

- Exact P-18R5 review-04 manifest remains SHA-256 `7725a03c82c370f6d9bb984b0d6e50c585efb07529a47f2c3dfad45877c1cca8`.
- Exact P-18R6 review-17 manifest remains SHA-256 `7925c1ab0515a59057851bb3888ff4d9974e5f5701b873b1f11468a5fd64a03a`.
- Exact P-19A plan/source manifest hashes remain `c47a66f9555492207c3676ffd8d3f66c4d6688571d63c77b9284afcf0ebc6361` and `87a5ef0fdb7f2903490f67be757662139eb9dffe8ffd6a111547583fba6d8ae0`.
- `dist/SHA256SUMS.txt` and all three v1.0.0 ZIP hashes remain unchanged.
- No package build, `dist`, publication mirror, commit, push, tag or Release mutation was performed.
- `ROADMAP.md` was not changed because milestone relationships did not change.

## Honest limitation

P-19B is a technically verified source/gallery candidate, not the P-19C freeze or owner-approved full gallery. Full typography/glyph/containment, quantitative and pairwise QA, masked recognition, five-second review, exact freeze, owner review and `G-04@1.5.0` evaluation remain P-19C. No WCAG conformance or cross-browser certification is claimed.

