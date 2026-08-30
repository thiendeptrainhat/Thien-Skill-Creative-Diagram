# P-19B review-18 — detailed polar chart

**Candidate:** `P19B-P18-INHERITED-THREE-MODE-REVIEW-18-1.5.0`  
**Authority:** D-098, retaining D-084–D-097 gallery scope  
**Status:** in-progress / owner-review-pending  
**Date:** 2026-08-30

## Delivered

Review-18 preserves the 14 exact P-18 anchors and all prior P-19B remediation/addition work, then replaces only `polar-chart`. The new chart derives one original illustrative series across eight ordered UTC windows. Eight straight spokes share one origin; each endpoint radius is proportional to its exact value on the linear 0–100% scale, with rings at 20/40/60/80/100.

Every window exposes a direct category label, exact percentage and open endpoint marker. The unique 100% maximum is the sole focal datum and repeats its meaning through coral color, thicker stroke, coral marker outline, direct `ĐỈNH` text and the `Đỉnh ngày` role in an exact eight-row table. Spokes have no arrowheads and the earlier filled-wedge rendering is absent. All three modes share identical SVG geometry.

The supplied image was treated only as a non-executable rubric for radial spokes, a 0–100 scale, direct external labels and one emphasized maximum. Vietnamese prose, illustrative values, semantic IDs, layout, CSS and SVG are independently authored.

P-19 remains 75 canonical + 12 capability + 3 Layers-variant HTML = 90 specimens and 30 previews. The comparison remains 14 approved P-18 originals + 90 P-19 specimens = 104 diagrams.

## Verification

- Review-18 exact checks: **PASS** — 1 series, 8 UTC windows, 8 common-origin proportional spokes, 8 endpoint markers, 5 radial rings, 1 unique peak, arrow-free geometry, non-color peak redundancy, exact alternative table and three-mode geometry.
- Review-17 immutable archive: **362 files** verified.
- Protected P-18/history/P-19A/P-17 grammar/dist/publication corpus: **6469 hashes** verified.
- Non-target preservation: **87 HTML** unchanged after candidate-ID normalization and **29 preview SVG** byte-identical.
- Active gallery static checks: **34/34 PASS**.
- Neutral-light polar chart was rasterized locally with Quick Look and visually inspected; all rings, spokes, direct labels, endpoint markers and the focal maximum are visible without clipping or overlap.
- Focused detailed-layout suite: **149/149 PASS**; gallery scope suite: **8/8 PASS**; full regression: **311/311 PASS**.
- Exact SVG proofs for all three modes and the inspected raster are under `review18-checks/`.

Browser remains **BLOCKED_NOT_EXECUTABLE** under the existing local-file URL policy. Local raster inspection is focused visual evidence, not browser, responsive, keyboard, computed-font or screen-reader PASS.

## Boundary

P-18 exact manifest SHA-256 remains `7925c1ab0515a59057851bb3888ff4d9974e5f5701b873b1f11468a5fd64a03a`.

P-19B review-18 is not owner-approved. P-19C remains not-started/unauthorized; G-04@1.5.0 remains NOT-EVALUATED. No package build, `dist`/publication mutation, commit, push, tag or Release operation.

## Repeat checks

```sh
PYTHONDONTWRITEBYTECODE=1 python3 evidence/p19/source/generate_p19b_gallery.py
PYTHONDONTWRITEBYTECODE=1 python3 evidence/p19/source/verify_p19b.py
PYTHONDONTWRITEBYTECODE=1 python3 evidence/p19/source/verify_p19b_review18.py
PYTHONDONTWRITEBYTECODE=1 PYTHONPATH=evidence/p19/source:thien-skill-creative-diagram/scripts:thien-skill-creative-diagram/scripts/tests python3 -m unittest test_polar_chart_layout_v15 test_medallion_layout_v15 test_line_chart_layout_v15 test_layers_layout_v15 test_kanban_layout_v15 test_it_current_state_layout_v15 test_high_level_layout_v15 test_er_data_model_layout_v15 test_dp_security_matrix_layout_v15 test_bar_chart_layout_v15 test_dp_integration_layout_v15 test_gallery_renderer_v15 test_fishbone_layout_v15 test_gantt_layout_v15 test_flywheel_layout_v15
```

Finalize plan/source manifests after evidence edits, bind comparison pins and run deterministic `--check`. Never rerun archive/withdrawal operations or historical candidate verifiers against the current gallery.
