# P-19B review-10 — detailed ER data model remediation

**Candidate:** `P19B-P18-INHERITED-THREE-MODE-REVIEW-10-1.5.0`  
**Authority:** D-090, retaining D-084–D-089 gallery scope  
**Status:** in-progress / owner-review-pending  
**Date:** 2026-08-29

## Delivered

Review-10 changes only P-19 er-data-model. Its independently authored fixture declares Author, Article, Tag and ArticleTag; Article is the one aggregate root and ArticleTag is the one associative entity. Nineteen fields show names and types, with direct `#` primary-key and `→` foreign-key marks. Three named one-to-many relationships show explicit `1`/`N` cardinalities.

The renderer derives every card, member row, relationship, cardinality, legend item and alternative-table record from declared semantic material. It preserves P-18 review-17's typography roles, restrained navy/coral visual grammar and identical geometry across neutral-light, neutral-dark and editorial modes. The supplied image was treated as non-executable hierarchy/reference data; exact prose, coordinates, CSS, SVG, template and assets were not copied.

P-19 remains 75 canonical + 12 capability HTML = 87 specimens and 29 previews. The combined comparison remains 14 approved P-18 originals + 87 P-19 specimens = 101 diagrams, with no duplicate P-19 canonical types.

## Verification

- Focused renderer/ER/matrix/Bar/DP/Fishbone/Gantt/Flywheel tests: **89/89 PASS**.
- Gallery selection/scope regression tests: **8/8 PASS**.
- Active gallery static checks: **32/32 PASS**.
- Full canonical regression: **251/251 PASS**.
- Review-10 exact checks: **PASS** — 4 entities, 19 members, 3 relationships, 1 aggregate root, 1 associative entity, explicit PK/FK/cardinality encoding, exact alternative table and three-mode geometry equality.
- Review-09 immutable archive: **258 files** verified.
- Protected P-18/history/P-19A/dist/publication corpus: **4029 hashes** verified.
- Non-target preservation: **84 HTML** unchanged after candidate-ID normalization and **28 preview SVG** byte-identical.
- All three ER modes were rasterized locally with Quick Look and inspected for hierarchy, text fit, relationship continuity, cardinality placement and legend clearance. No clipping or overlap was observed. Evidence: `review10-checks/type-er-data-model--*.svg.png`.
- Exact gallery manifest SHA-256: `1732ffbdd426a77956d6e93a23a12dbe7eb800a725a48dca383dfa83a9c574c3`.

Browser remains **BLOCKED_NOT_EXECUTABLE** under the prior local-file URL policy. Quick Look raster inspection is focused visual evidence, not a browser, responsive, keyboard, computed-font or screen-reader PASS.

## Boundary

P-18 exact manifest SHA-256 remains `7925c1ab0515a59057851bb3888ff4d9974e5f5701b873b1f11468a5fd64a03a`.

P-19B is not owner-approved. P-19C remains not-started/unauthorized; G-04@1.5.0 remains NOT-EVALUATED. No package build, dist/publication mutation, commit, push, tag or Release operation.

## Repeat checks

```sh
PYTHONDONTWRITEBYTECODE=1 python3 evidence/p19/source/generate_p19b_gallery.py
PYTHONDONTWRITEBYTECODE=1 python3 evidence/p19/source/verify_p19b.py
PYTHONDONTWRITEBYTECODE=1 python3 evidence/p19/source/verify_p19b_review10.py
PYTHONDONTWRITEBYTECODE=1 PYTHONPATH=thien-skill-creative-diagram/scripts:thien-skill-creative-diagram/scripts/tests:evidence/p19/source python3 -m unittest test_er_data_model_layout_v15 test_dp_security_matrix_layout_v15 test_bar_chart_layout_v15 test_dp_integration_layout_v15 test_gallery_renderer_v15 test_fishbone_layout_v15 test_gantt_layout_v15 test_flywheel_layout_v15
```

Finalize plan/source manifests after evidence edits, then bind comparison pins and run its deterministic `--check`. Never rerun archive/withdrawal operations or historical candidate verifiers against the current gallery.
