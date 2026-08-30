# P-19B review-31 — detailed sequence

**Candidate:** `P19B-P18-INHERITED-THREE-MODE-REVIEW-31-1.5.0`  
**Authority:** D-111, retaining D-084–D-110 gallery scope  
**Status:** technical evidence PASS; owner visual approval pending

## Outcome

Review-31 preserves the 14 exact P-18 anchors and every prior P-19B remediation, then replaces only `sequence` with an independently authored content-delivery interaction. It contains four evenly spaced participant cards, four lifelines centered to those cards, two centered activations and six chronologically ordered messages.

Five cross-participant messages use straight horizontal routes. The only non-straight route is the `DỰNG TRANG` self-call, implemented as a documented rounded-orthogonal exception because its source and target are the same lifeline. Request, return/async and primary response remain distinguishable by direct labels, line treatment and legend; the origin participant and primary response receive restrained coral emphasis.

The owner screenshot informed structure and hierarchy only. Scenario, Vietnamese labels, semantic IDs, coordinates, CSS and SVG are original; the result inherits the approved P-18 review-17 palette, typography roles, ultra-thin outlines and restrained focal treatment. The `thien-skill-ui-ux-ultra` workflow contributed reference analysis, design-contract discipline and render inspection only; no code, template or asset was copied.

## Preservation and verification

- Exact review-30 was archived before mutation: 501 snapshot records and 12,040 protected records verified.
- Three `type-sequence` HTML files changed; 87 non-target HTML artworks are equal after candidate-ID normalization.
- One sequence preview changed; 29 non-target previews are byte-identical.
- All three modes serialize identical geometry: 4 participants, 4 lifelines, 2 activations and 6 messages.
- Five cross-participant routes are straight; the single self-call is a documented rounded-orthogonal exception.
- All four participant cards and both activations are centered on their lifeline axes under D-105.
- The neutral-light sequence was rasterized locally at 2000×1140 and visually inspected without overlap, clipping, line-through-label or attachment drift.
- Browser execution remains `BLOCKED_URL_POLICY`; local raster evidence is not represented as a browser PASS.

Focused sequence tests `3/3`, scope tests `8/8`, static verification `34/34` and full regression `366/366` pass. Exact review verification also passes.

## Boundary

P-19B review-31 is not owner-approved. P-19C remains not-started/unauthorized; G-04@1.5.0 remains NOT-EVALUATED. No package build, `dist`/publication mutation, commit, push, tag or Release operation was performed.

## Reproduction

```sh
PYTHONDONTWRITEBYTECODE=1 python3 evidence/p19/source/generate_p19b_gallery.py
node evidence/p19/source/render_review31_proof.mjs
PYTHONDONTWRITEBYTECODE=1 python3 evidence/p19/source/verify_p19b_review31.py
PYTHONPATH=thien-skill-creative-diagram/scripts:thien-skill-creative-diagram/scripts/tests:evidence/p19/source PYTHONDONTWRITEBYTECODE=1 python3 -m unittest thien-skill-creative-diagram/scripts/tests/test_sequence_layout_v15.py
PYTHONDONTWRITEBYTECODE=1 python3 -m unittest discover -s evidence/p19/source -p 'test_*.py'
PYTHONDONTWRITEBYTECODE=1 python3 evidence/p19/source/verify_p19b.py
PYTHONPATH=evidence/p19/source:thien-skill-creative-diagram/scripts:thien-skill-creative-diagram/scripts/tests PYTHONDONTWRITEBYTECODE=1 python3 -m unittest discover -s thien-skill-creative-diagram/scripts/tests -p 'test_*.py'
PYTHONDONTWRITEBYTECODE=1 python3 evidence/p19/source/build_p19b_manifests.py
PYTHONDONTWRITEBYTECODE=1 python3 evidence/p19/comparison/generate_comparison.py
PYTHONDONTWRITEBYTECODE=1 python3 evidence/p19/comparison/generate_comparison.py --check
```
