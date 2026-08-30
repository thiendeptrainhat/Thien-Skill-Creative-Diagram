# P-19B review-21 — exact-area continent Treemap

**Candidate:** `P19B-P18-INHERITED-THREE-MODE-REVIEW-21-1.5.0`  
**Authority:** D-101, retaining D-084–D-100 gallery scope  
**Status:** technical evidence PASS; owner visual approval pending

## Outcome

Review-21 preserves the 14 exact P-18 anchors and every prior P-19B remediation/addition, then replaces only `treemap`. The new original illustrative fixture contains six continent leaves with values 4,780 / 1,480 / 750 / 610 / 430 / 50 million and an exact 8,100-million parent total.

The 2,000×1,040 SVG uses six contiguous rectangles. Each tile's geometric area equals its value share; Châu Á is the only focal tile and Châu Đại Dương is the only compact-label tile. Five tiles carry direct labels, the smallest tile carries an `i` marker, and the legend plus exact-value table preserve the unavailable inline text.

## Preservation and verification

- Exact review-20 was archived before mutation: 398 snapshot files and 7,594 protected files verified.
- Three `type-treemap` HTML files changed; 87 non-target HTML artworks are equal after candidate-ID normalization.
- One Treemap preview changed; 29 non-target previews are byte-identical.
- Six positive leaves and both hierarchy totals reconcile exactly.
- Six serialized rectangle areas reconcile to their six values.
- One focal tile and one compact-label tile have non-color/direct-text disclosure.
- All three modes share exact SVG geometry.
- Neutral-light Treemap was rasterized locally with Quick Look and visually inspected; all tiles remain within the mosaic, five label stacks fit, the small-tile marker is visible and the footer legend is intact.
- Exact SVG proofs for three modes and the inspected raster are under `review21-checks/`.
- Browser execution remains `BLOCKED_URL_POLICY`; static/raster evidence is not represented as a browser PASS.

Final verification is green: focused 174/174, scope 8/8, static 34/34 and full regression 336/336 PASS. The same counts are recorded in `PLAN.md`, `HANDOFF-CURRENT.md` and `P-19B-REVIEW-21-VERIFICATION.json`.

## Boundary

P-19B review-21 is not owner-approved. P-19C remains not-started/unauthorized; G-04@1.5.0 remains NOT-EVALUATED. No package build, `dist`/publication mutation, commit, push, tag or Release operation.

## Reproduction

```sh
PYTHONDONTWRITEBYTECODE=1 python3 evidence/p19/source/generate_p19b_gallery.py
PYTHONDONTWRITEBYTECODE=1 python3 evidence/p19/source/verify_p19b_review21.py
PYTHONDONTWRITEBYTECODE=1 PYTHONPATH=evidence/p19/source:thien-skill-creative-diagram/scripts:thien-skill-creative-diagram/scripts/tests python3 -m unittest test_treemap_layout_v15 test_venn_layout_v15 test_wardley_map_layout_v15 test_polar_chart_layout_v15 test_medallion_layout_v15 test_line_chart_layout_v15 test_layers_layout_v15 test_kanban_layout_v15 test_it_current_state_layout_v15 test_high_level_layout_v15 test_er_data_model_layout_v15 test_dp_security_matrix_layout_v15 test_bar_chart_layout_v15 test_dp_integration_layout_v15 test_gallery_renderer_v15 test_fishbone_layout_v15 test_gantt_layout_v15 test_flywheel_layout_v15
PYTHONDONTWRITEBYTECODE=1 python3 -m unittest discover -s evidence/p19/source -p 'test_*.py'
PYTHONDONTWRITEBYTECODE=1 python3 evidence/p19/source/verify_p19b.py
PYTHONDONTWRITEBYTECODE=1 PYTHONPATH=evidence/p19/source:thien-skill-creative-diagram/scripts:thien-skill-creative-diagram/scripts/tests python3 -m unittest discover -s thien-skill-creative-diagram/scripts/tests -p 'test_*.py'
PYTHONDONTWRITEBYTECODE=1 python3 evidence/p19/source/build_p19b_manifests.py
PYTHONDONTWRITEBYTECODE=1 python3 evidence/p19/comparison/generate_comparison.py
PYTHONDONTWRITEBYTECODE=1 python3 evidence/p19/comparison/generate_comparison.py --check
```
