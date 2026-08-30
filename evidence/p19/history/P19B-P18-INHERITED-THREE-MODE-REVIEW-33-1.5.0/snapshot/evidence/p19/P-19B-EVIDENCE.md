# P-19B review-33 — detailed scatter-chart presentation variant

**Candidate:** `P19B-P18-INHERITED-THREE-MODE-REVIEW-33-1.5.0`  
**Authority:** D-113, retaining D-084–D-112 gallery scope  
**Status:** technical evidence PASS; owner visual approval pending

## Outcome

Review-33 preserves the 14 exact P-18 anchors and all 90 prior P-19B HTML specimens, then adds `scatter-chart` as a presentation variant under the frozen P-18 parent `scatter-plot`. It does not create a new canonical type or replace the approved P-18 scatter anchor.

The new chart contains exactly 12 independently authored `(deploys/week, lead-time days)` pairs, arrow-free linear axes `0–20` and `0–24`, six x-ticks, five y-ticks, 12 hollow-circle points, one descending dashed OLS trend and one coral focal point for Platform at `(18,3)`. The focal role is also represented by a direct label, legend entry and exact 12-row alternative table. All three modes use identical SVG geometry.

The `thien-skill-ui-ux-ultra` workflow contributed reference decomposition, visual hierarchy, chart-mechanics checks and render inspection only; no code, template or asset was copied.

## Preservation and verification

- Exact review-32 was archived before mutation: 522 snapshot records and 13,056 protected records verified.
- All 90 prior HTML artworks are equal after candidate-ID normalization.
- All 30 prior previews are byte-identical.
- Exactly three `type-scatter-chart` HTML specimens and one preview were added, producing 93 HTML/31 previews and 107 combined comparison diagrams.
- The scatter artifact has exactly 12 points, one focal point, two axes, 11 ticks and one dashed OLS trend; slope/intercept are `-0.9891304347826086` and `20.141304347826086`.
- The exact 12-row alternative table and three-mode geometry equality are machine-verified.
- The neutral-light 2000×1020 proof was rasterized locally and visually inspected against the owner's structural reference.
- Browser execution remains `BLOCKED_URL_POLICY`; local raster evidence is not represented as a browser PASS.

Focused scatter tests `7/7`, scope tests `8/8`, static verification `34/34` and full regression `373/373` pass. Exact review-33 verification also passes.

## Boundary

P-19B review-33 is not owner-approved. P-19C remains not-started/unauthorized; G-04@1.5.0 remains NOT-EVALUATED. No package build, `dist`/publication mutation, commit, push, tag or Release operation was performed.

## Reproduction

```sh
PYTHONDONTWRITEBYTECODE=1 python3 evidence/p19/source/generate_p19b_gallery.py
node evidence/p19/source/render_review33_proof.mjs
PYTHONDONTWRITEBYTECODE=1 python3 evidence/p19/source/verify_p19b_review33.py
PYTHONPATH=thien-skill-creative-diagram/scripts:thien-skill-creative-diagram/scripts/tests:evidence/p19/source PYTHONDONTWRITEBYTECODE=1 python3 -m unittest thien-skill-creative-diagram/scripts/tests/test_scatter_chart_layout_v15.py
PYTHONDONTWRITEBYTECODE=1 python3 -m unittest discover -s evidence/p19/source -p 'test_*.py'
PYTHONDONTWRITEBYTECODE=1 python3 evidence/p19/source/verify_p19b.py
PYTHONPATH=evidence/p19/source:thien-skill-creative-diagram/scripts:thien-skill-creative-diagram/scripts/tests PYTHONDONTWRITEBYTECODE=1 python3 -m unittest discover -s thien-skill-creative-diagram/scripts/tests -p 'test_*.py'
PYTHONDONTWRITEBYTECODE=1 python3 evidence/p19/source/build_p19b_manifests.py
PYTHONDONTWRITEBYTECODE=1 python3 evidence/p19/comparison/generate_comparison.py
PYTHONDONTWRITEBYTECODE=1 python3 evidence/p19/comparison/generate_comparison.py --check
```
