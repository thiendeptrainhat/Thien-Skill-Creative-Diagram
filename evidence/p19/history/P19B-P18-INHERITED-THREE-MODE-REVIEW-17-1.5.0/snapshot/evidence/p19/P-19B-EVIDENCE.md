# P-19B review-17 — detailed medallion lifecycle

**Candidate:** `P19B-P18-INHERITED-THREE-MODE-REVIEW-17-1.5.0`  
**Authority:** D-097, retaining D-084–D-096 gallery scope  
**Status:** in-progress / owner-review-pending  
**Date:** 2026-08-30

## Delivered

Review-17 preserves the 14 exact P-18 anchors and all prior P-19B remediation/addition work, then replaces only `medallion`. The new lifecycle derives five ordered semantic stages: tiếp nhận, ẩn danh, chuẩn hóa, tổng hợp and lưu trữ. Four continuous directed arcs promote data between adjacent stages; two bottom callouts distinguish repeatable SQL transformation from controlled notebook exploration.

Every stage directly exposes a technical storage name, tool, format, accountable writer and two concrete examples. The aggregated stage is the sole focal stage and carries coral boundary/fill plus a `TRỌNG TÂM` tag. The archive stage is the sole archive stage and carries dashed boundary plus a `LƯU TRỮ` tag. All three modes share identical SVG geometry; an exact five-stage table provides a non-visual alternative.

The supplied image was treated only as a non-executable rubric for five tall lifecycle cards, promotion arcs, focal/archive distinction, detailed stage fields and processing-path callouts. Vietnamese prose, illustrative data, semantic IDs, layout, CSS and SVG are independently authored.

P-19 remains 75 canonical + 12 capability + 3 Layers-variant HTML = 90 specimens and 30 previews. The comparison remains 14 approved P-18 originals + 90 P-19 specimens = 104 diagrams.

## Verification

- Review-17 exact checks: **PASS** — 5 stages, 4 continuous directed promotions, 2 processing paths, 1 focal stage, 1 archive stage, complete per-stage fields, non-color state redundancy, exact alternative table and three-mode geometry.
- Review-16 immutable archive: **350 files** verified.
- Protected P-18/history/P-19A/P-17 grammar/dist/publication corpus: **6118 hashes** verified.
- Non-target preservation: **87 HTML** unchanged after candidate-ID normalization and **29 preview SVG** byte-identical.
- Active gallery static checks: **34/34 PASS**.
- Neutral-light medallion was rasterized locally with Quick Look and visually inspected after separating promotion labels from the arc geometry; five cards, four arrows, focal/archive states and both path callouts are visible without clipping or overlap.
- Focused detailed-layout suite: **140/140 PASS**; gallery scope suite: **8/8 PASS**; full regression: **302/302 PASS**.
- Exact SVG proofs for all three modes and the inspected raster are under `review17-checks/`.

Browser remains **BLOCKED_NOT_EXECUTABLE** under the existing local-file URL policy. Local raster inspection is focused visual evidence, not browser, responsive, keyboard, computed-font or screen-reader PASS.

## Boundary

P-18 exact manifest SHA-256 remains `7925c1ab0515a59057851bb3888ff4d9974e5f5701b873b1f11468a5fd64a03a`.

P-19B review-17 is not owner-approved. P-19C remains not-started/unauthorized; G-04@1.5.0 remains NOT-EVALUATED. No package build, `dist`/publication mutation, commit, push, tag or Release operation.

## Repeat checks

```sh
PYTHONDONTWRITEBYTECODE=1 python3 evidence/p19/source/generate_p19b_gallery.py
PYTHONDONTWRITEBYTECODE=1 python3 evidence/p19/source/verify_p19b.py
PYTHONDONTWRITEBYTECODE=1 python3 evidence/p19/source/verify_p19b_review17.py
PYTHONDONTWRITEBYTECODE=1 PYTHONPATH=evidence/p19/source:thien-skill-creative-diagram/scripts:thien-skill-creative-diagram/scripts/tests python3 -m unittest test_medallion_layout_v15 test_line_chart_layout_v15 test_layers_layout_v15 test_kanban_layout_v15 test_it_current_state_layout_v15 test_high_level_layout_v15 test_er_data_model_layout_v15 test_dp_security_matrix_layout_v15 test_bar_chart_layout_v15 test_dp_integration_layout_v15 test_gallery_renderer_v15 test_fishbone_layout_v15 test_gantt_layout_v15 test_flywheel_layout_v15
```

Finalize plan/source manifests after evidence edits, bind comparison pins and run deterministic `--check`. Never rerun archive/withdrawal operations or historical candidate verifiers against the current gallery.
