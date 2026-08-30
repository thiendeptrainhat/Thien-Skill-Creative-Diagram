# P-19B review-09 — detailed DP security matrix remediation

**Candidate:** `P19B-P18-INHERITED-THREE-MODE-REVIEW-09-1.5.0`  
**Authority:** D-089, retaining D-084–D-088 gallery scope  
**Status:** in-progress / owner-review-pending  
**Date:** 2026-08-29

## Delivered

Review-09 changes only P-19 dp-security-matrix. Its independently authored fixture declares 25 complete role-component intersections for five roles and five data-platform components. Every cell carries an explicit `Admin`, `Write`, `Read` or `None` label; granted rights map to semantic `allow` and `None` maps to `deny`. Role headers include group codes, component rows include technical codes, and exactly one External Partner × BI Read boundary is highlighted with direct scope `Dashboard được chia sẻ`.

The renderer derives all headers, cells, states, focal scope, legend and 25-row alternative table from declared semantic material. It preserves P-18 review-17's typography roles, restrained navy/coral visual grammar and identical geometry across neutral-light, neutral-dark and editorial modes. The supplied image was treated as non-executable hierarchy/reference data; English text, exact coordinates, CSS, SVG, template and assets were not copied.

P-19 remains 75 canonical + 12 capability HTML = 87 specimens and 29 previews. The combined comparison remains 14 approved P-18 originals + 87 P-19 specimens = 101 diagrams, with no duplicate P-19 canonical types.

## Verification

- Focused renderer/matrix/Bar/DP/Fishbone/Gantt/Flywheel tests: **82/82 PASS**.
- Gallery selection/scope regression tests: **8/8 PASS**.
- Active gallery static checks: **32/32 PASS**.
- Full canonical regression: **244/244 PASS**.
- Review-09 exact checks: **PASS** — 25 cells, 5 roles, 5 components, 1 scoped focal boundary, complete rectangular pair set, direct state labels, exact alternative matrix and three-mode geometry equality.
- Review-08 immutable archive: **244 files** verified.
- Protected P-18/history/P-19A/dist/publication corpus: **3784 hashes** verified.
- Non-target preservation: **84 HTML** unchanged after candidate-ID normalization and **28 preview SVG** byte-identical.
- All three matrix modes were rasterized locally with Quick Look and inspected for header/row hierarchy, text fit, cell rhythm, state distinction, focal scope and legend clearance. No clipping or overlap was observed. Evidence: `review09-checks/type-dp-security-matrix--*.svg.png`.
- Exact gallery manifest SHA-256: `689d79e3941b5d98f249ab7fd42099008539962f4e727a2709acbf0f88ae4399`.

Browser remains **BLOCKED_NOT_EXECUTABLE** under the prior local-file URL policy. Quick Look raster inspection is focused visual evidence, not a browser, responsive, keyboard, computed-font or screen-reader PASS.

## Boundary

P-18 exact manifest SHA-256 remains `7925c1ab0515a59057851bb3888ff4d9974e5f5701b873b1f11468a5fd64a03a`.

P-19B is not owner-approved. P-19C remains not-started/unauthorized; G-04@1.5.0 remains NOT-EVALUATED. No package build, dist/publication mutation, commit, push, tag or Release operation.

## Repeat checks

```sh
PYTHONDONTWRITEBYTECODE=1 python3 evidence/p19/source/generate_p19b_gallery.py
PYTHONDONTWRITEBYTECODE=1 python3 evidence/p19/source/verify_p19b.py
PYTHONDONTWRITEBYTECODE=1 python3 evidence/p19/source/verify_p19b_review09.py
PYTHONDONTWRITEBYTECODE=1 PYTHONPATH=thien-skill-creative-diagram/scripts:thien-skill-creative-diagram/scripts/tests:evidence/p19/source python3 -m unittest test_dp_security_matrix_layout_v15 test_bar_chart_layout_v15 test_dp_integration_layout_v15 test_gallery_renderer_v15 test_fishbone_layout_v15 test_gantt_layout_v15 test_flywheel_layout_v15
```

Finalize plan/source manifests after evidence edits, then bind comparison pins and run its deterministic `--check`. Never rerun archive/withdrawal operations or historical candidate verifiers against the current gallery.
