# P-19B remediation evidence — P-18 inherited three-mode exact 129 HTML

**Candidate:** `P19B-P18-INHERITED-THREE-MODE-REVIEW-02-1.5.0`  
**Authority:** D-080 / D-081  
**Status:** `in-progress · technically ready for owner visual review`  
**Date:** 2026-08-27

## Owner correction and lineage

The owner rejected the design direction of initial candidate `P19B-THREE-MODE-EXACT-129-HTML-1.5.0` because it did not inherit the approved P-18 style closely enough. That candidate remains byte-bound historical evidence under `evidence/p19/history/P19B-THREE-MODE-EXACT-129-HTML-1.5.0/`; its gallery/plan/source manifest hashes remain `ed6a145…b106`, `59edd733…b40f`, and `44cdbe31…188c`.

The successor binds every document to exact visual parent `P18R6-FOURTEEN-ENGINE-NEUTRAL-LIGHT-REVIEW-17-1.5.0`, manifest SHA-256 `7925c1ab0515a59057851bb3888ff4d9974e5f5701b873b1f11468a5fd64a03a`.

## Delivered remediation

- Active renderer: `thien-skill-creative-diagram/scripts/gallery_renderer_v15.py`.
- Generated renderer registry: `thien-skill-creative-diagram/references/gallery-renderer-v15.json`.
- Exact gallery: 129 standalone HTML under `evidence/p19/gallery/specimens/`, one contact sheet and 43 neutral-light SVG previews.
- Exact composition remains 39 canonical × three modes = 117 plus four capabilities × three modes = 12.
- All 43 adapter identities retain their P-19A engine/silhouette binding; no generic/unknown fallback.

## P-18 inheritance implemented

- Neutral-light preserves P-18 review-17 warm paper/canvas/surface, ink/connector/grid and coral/accent-soft roles.
- Georgia display, Avenir Next material and Menlo technical roles are exposed in each specimen.
- Artifact frame, shadow, evidence rail, focal-card, connector, dot-field and legend grammar now follow P-18 review-17.
- Neutral-dark and editorial change only semantic color roles; SVG structure and geometry remain invariant across all three modes.
- Every HTML root, inline SVG, inert metadata, inventory and renderer registry bind the exact P-18 parent candidate and manifest hash.
- Legacy initial-candidate blue direction `#246BCE`/`#F5F7FA` is absent from all 129 active specimens.

## Review-02 repair and preservation

- Exact review-01 archived before mutation: `evidence/p19/history/P19B-P18-INHERITED-THREE-MODE-REVIEW-01-1.5.0/`; all 199 snapshot files verified.
- `dp-integration`: original parent `(470,190,260,290)` failed containment (right gap −20px) and x-centering (20px error). Parent now derives from child bounds: `(466,190,308,290)`, gaps L/T/R/B = `24/85/24/85px`, center error `0/0px`. Node positions, sizes, text and connector endpoints remain unchanged.
- `swimlane`: removed the background-colored `.bridge` overlay at a normal bend. One contiguous stroked path now covers the complete handoff. Rounded is still default; a scoped `connector_corner_style="straight"` rendering option is tested on the same vertices/endpoints, with no new gallery specimens.
- Added ten unit tests, including regressions/mutations for overflow, off-centering, invalid routes, second subpaths, erase overlays and invisible strokes. Runtime refuses invalid target geometry before returning HTML.
- 123 non-target HTML are byte-identical after candidate-ID normalization; 41 non-target preview SVG are byte-identical. Target styles, header, semantic table and metadata (except candidate ID) are preserved.
- `P-19B-REVIEW-02-VERIFICATION.json` records six target geometry checks, three straight proofs, 199 archive hashes and 1,954 protected-file hashes.
- Proof SVGs/PNGs and the owner's two defect screenshots are QA-only under `evidence/p19/review02-checks/`; they do not add to the exact 129 gallery HTML count.

## Verification

- Focused renderer unit suite: `24/24 PASS`.
- Focused static gallery/inheritance verification: `29/29 PASS`.
- Full canonical regression: `186/186 PASS`.
- Deterministic generation: exact 129 specimens, 43 previews and one index; per-file hashes and manifest integrity `PASS`.
- Geometry invariance: `43/43` fixture groups have identical SVG structure across the three modes after mode ID normalization.
- Historical initial-candidate archive manifest triplet remains byte-identical.
- Local raster inspection: nine focused Quick Look renders inspected (dp-integration and rounded swimlane × three modes, plus straight swimlane × three modes). Both reported defects are repaired. This does not assert that every other diagram is visually correct; the earlier review-01 broad inspection claim missed these defects and is superseded.
- Browser execution: `blocked / not executable`. The in-app browser URL policy rejected reload of the local `file://` gallery; no workaround was used and the previous initial-candidate browser PASS is not carried forward.

The first full regression run failed the repository-hygiene check because Finder had created two `.DS_Store` files in canonical root/scripts. They were moved, not deleted, to the temporary `p19-review02-raster.aK2Yyo` directory as `canonical-root.DS_Store` / `canonical-scripts.DS_Store`; hashes `0c34e703242de3ae50c77c7276a332847b3dd57dc645fb581fe666dc21a6be62` / `a5149ea86fe217e395e9bb083de77ea0f151ba5544518edd7486beeacddf3eb5`. Unchanged tests then passed 186/186.

Machine-readable records:

- `evidence/p19/P-19B-STATIC-VERIFICATION.json`
- `evidence/p19/P-19B-BROWSER-VERIFICATION.json`
- `evidence/p19/P-19B-PLAN-MANIFEST.json`
- `evidence/p19/P-19B-SOURCE-MANIFEST.json`
- `evidence/p19/gallery/P-19B-INVENTORY.json`
- `evidence/p19/gallery/P-19B-MANIFEST.json`

## Integrity and boundaries

- Exact P-18R5 review-04 and P-18R6 review-17 remain unchanged.
- Exact P-19A plan/source manifests remain unchanged.
- `dist/SHA256SUMS.txt` and the three v1.0.0 ZIPs remain unchanged.
- No package build, `dist`, publication mirror, commit, push, tag or Release mutation was performed.
- P-19C remains `not-started` and unauthorized; `G-04@1.5.0` remains `NOT-EVALUATED`.

## Stop condition

This successor is technically ready for owner visual review but is not marked `passed`. Owner approval of the exact P-18-inherited direction is pending. Browser responsive/console/focus/computed-style evidence and full P-19C QA/freeze/masked review are not claimed.

## Repeat focused checks

```sh
PYTHONDONTWRITEBYTECODE=1 python3 evidence/p19/source/generate_p19b_gallery.py
PYTHONDONTWRITEBYTECODE=1 python3 evidence/p19/source/verify_p19b.py
PYTHONDONTWRITEBYTECODE=1 python3 evidence/p19/source/verify_p19b_review02.py
PYTHONDONTWRITEBYTECODE=1 PYTHONPATH=thien-skill-creative-diagram/scripts:thien-skill-creative-diagram/scripts/tests python3 -m unittest discover -s thien-skill-creative-diagram/scripts/tests
```

Rebuild source/plan manifests only after intended governance/evidence edits, then
refresh the auxiliary comparison's exact manifest pins. Do not regenerate archived
candidates. No package build is part of this workflow.
