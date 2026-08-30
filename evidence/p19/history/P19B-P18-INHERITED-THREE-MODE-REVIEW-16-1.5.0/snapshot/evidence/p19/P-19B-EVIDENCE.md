# P-19B review-16 — detailed line chart

**Candidate:** `P19B-P18-INHERITED-THREE-MODE-REVIEW-16-1.5.0`  
**Authority:** D-096, retaining D-084–D-095 gallery scope  
**Status:** in-progress / owner-review-pending  
**Date:** 2026-08-30

## Delivered

Review-16 preserves the 14 exact P-18 anchors and all prior P-19B remediation/addition work, then replaces only `line-chart`. The new quantitative view derives three declared series across eight ordered weeks: 24 exact points on a shared 0–240 linear scale, six visible y ticks and two plain arrow-free axes.

The focal series uses coral line, circle markers, direct endpoint value and a restrained area fill. Two comparison series remain distinguishable without color through long-dash/square and dot-dash/diamond encodings. All three modes share identical SVG geometry; an exact 24-value table provides a non-visual alternative.

The supplied image was treated only as a non-executable rubric for multi-series trend, ordered periods, axis/grid hierarchy, focal-area emphasis and legend. Vietnamese prose, illustrative values, semantic IDs, layout, CSS and SVG are independently authored.

P-19 remains 75 canonical + 12 capability + 3 Layers-variant HTML = 90 specimens and 30 previews. The comparison remains 14 approved P-18 originals + 90 P-19 specimens = 104 diagrams.

## Verification

- Review-16 exact checks: **PASS** — 3 series, 24 points, 2 arrow-free axes, 6 ticks, 1 focal area, direct endpoint labels, non-color series redundancy, exact alternative table and three-mode geometry.
- Review-15 immutable archive: **338 files** verified.
- Protected P-18/history/P-19A/P-17 grammar/dist/publication corpus: **5779 hashes** verified.
- Non-target preservation: **87 HTML** unchanged after candidate-ID normalization and **29 preview SVG** byte-identical.
- Active gallery static checks: **34/34 PASS**.
- Neutral-light line chart was rasterized locally with Quick Look and inspected after correcting token binding and right-edge label clearance; all three series, markers, endpoint labels, ticks and legend are visible without clipping or overlap.
- Focused detailed-layout suite: **132/132 PASS**; gallery scope suite: **8/8 PASS**; full regression: **294/294 PASS**.
- Exact SVG proofs for all three modes and the inspected raster are under `review16-checks/`.

Browser remains **BLOCKED_NOT_EXECUTABLE** under the existing local-file URL policy. Local raster inspection is focused visual evidence, not browser, responsive, keyboard, computed-font or screen-reader PASS.

## Boundary

P-18 exact manifest SHA-256 remains `7925c1ab0515a59057851bb3888ff4d9974e5f5701b873b1f11468a5fd64a03a`.

P-19B review-16 is not owner-approved. P-19C remains not-started/unauthorized; G-04@1.5.0 remains NOT-EVALUATED. No package build, `dist`/publication mutation, commit, push, tag or Release operation.

## Repeat checks

```sh
PYTHONDONTWRITEBYTECODE=1 python3 evidence/p19/source/generate_p19b_gallery.py
PYTHONDONTWRITEBYTECODE=1 python3 evidence/p19/source/verify_p19b.py
PYTHONDONTWRITEBYTECODE=1 python3 evidence/p19/source/verify_p19b_review16.py
PYTHONDONTWRITEBYTECODE=1 PYTHONPATH=evidence/p19/source:thien-skill-creative-diagram/scripts:thien-skill-creative-diagram/scripts/tests python3 -m unittest test_line_chart_layout_v15 test_layers_layout_v15 test_kanban_layout_v15 test_it_current_state_layout_v15 test_high_level_layout_v15 test_er_data_model_layout_v15 test_dp_security_matrix_layout_v15 test_bar_chart_layout_v15 test_dp_integration_layout_v15 test_gallery_renderer_v15 test_fishbone_layout_v15 test_gantt_layout_v15 test_flywheel_layout_v15
```

Finalize plan/source manifests after evidence edits, bind comparison pins and run deterministic `--check`. Never rerun archive/withdrawal operations or historical candidate verifiers against the current gallery.
