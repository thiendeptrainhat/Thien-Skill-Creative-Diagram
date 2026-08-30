# P-19B review-20 — exact three-set Venn

**Candidate:** `P19B-P18-INHERITED-THREE-MODE-REVIEW-20-1.5.0`  
**Authority:** D-100, retaining D-084–D-099 gallery scope  
**Status:** in-progress / owner-review-pending  
**Date:** 2026-08-30

## Delivered

Review-20 preserves the 14 exact P-18 anchors and all prior P-19B remediation/addition work, then replaces only `venn`. The new original illustrative model contains three equal-radius sets—`Đáng mong muốn`, `Khả thi` and `Bền vững`—with one exclusive semantic member each and one shared member, `Sẵn sàng triển khai`, belonging to all three.

The focal region is not a manually approximated lens: it is the exact geometric intersection of all three circles, serialized through two nested SVG clip paths. Every set has a direct title/subtitle; the core repeats its meaning through the direct title and non-color technical role `ĐIỂM CÂN BẰNG`. One accessible table lists all four members and their exact set membership. All three modes share identical SVG geometry.

The supplied image was treated only as a non-executable rubric for balanced three-circle composition, label hierarchy and central-intersection emphasis. Vietnamese prose, illustrative data, semantic IDs, coordinates, layout, CSS and SVG are independently authored.

P-19 remains 75 canonical + 12 capability + 3 Layers-variant HTML = 90 specimens and 30 previews. The comparison remains 14 approved P-18 originals + 90 P-19 specimens = 104 diagrams.

## Verification

- Review-20 exact checks: **PASS** — 3 equal-radius sets, 4 members, 1 exact nested-clipped triple intersection, balanced lower-set axis, direct set/core labels, exact membership table and three-mode geometry.
- Review-19 immutable archive: **386 files** verified.
- Protected P-18/history/P-19A/P-17 grammar/dist/publication corpus: **7207 hashes** verified.
- Non-target preservation: **87 HTML** unchanged after candidate-ID normalization and **29 preview SVG** byte-identical.
- Active gallery static checks: **34/34 PASS**.
- Neutral-light Venn was rasterized locally with Quick Look and visually inspected; all circles, outlines, direct labels and the focal triple-intersection region are visible and the core title fits inside its region.
- Focused detailed-layout suite: **166/166 PASS**; gallery scope suite: **8/8 PASS**; full regression: **328/328 PASS**.
- Exact SVG proofs for all three modes and the inspected raster are under `review20-checks/`.

Browser execution remains **BLOCKED_URL_POLICY**: the in-app browser rejected the local file URL and no bypass was attempted. Local raster inspection is focused visual evidence, not browser, responsive, keyboard, computed-font or screen-reader PASS.

## Boundary

P-18 exact manifest SHA-256 remains `7925c1ab0515a59057851bb3888ff4d9974e5f5701b873b1f11468a5fd64a03a`.

P-19B review-20 is not owner-approved. P-19C remains not-started/unauthorized; G-04@1.5.0 remains NOT-EVALUATED. No package build, `dist`/publication mutation, commit, push, tag or Release operation.

## Repeat checks

```sh
PYTHONDONTWRITEBYTECODE=1 python3 evidence/p19/source/generate_p19b_gallery.py
PYTHONDONTWRITEBYTECODE=1 python3 evidence/p19/source/verify_p19b.py
PYTHONDONTWRITEBYTECODE=1 python3 evidence/p19/source/verify_p19b_review20.py
PYTHONDONTWRITEBYTECODE=1 PYTHONPATH=evidence/p19/source:thien-skill-creative-diagram/scripts:thien-skill-creative-diagram/scripts/tests python3 -m unittest test_venn_layout_v15 test_wardley_map_layout_v15 test_polar_chart_layout_v15 test_medallion_layout_v15 test_line_chart_layout_v15 test_layers_layout_v15 test_kanban_layout_v15 test_it_current_state_layout_v15 test_high_level_layout_v15 test_er_data_model_layout_v15 test_dp_security_matrix_layout_v15 test_bar_chart_layout_v15 test_dp_integration_layout_v15 test_gallery_renderer_v15 test_fishbone_layout_v15 test_gantt_layout_v15 test_flywheel_layout_v15
```

Finalize plan/source manifests after evidence edits, bind comparison pins and run deterministic `--check`. Never rerun archive/withdrawal operations or historical candidate verifiers against the current gallery.
