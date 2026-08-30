# P-19B review-30 — detailed state machine

**Candidate:** `P19B-P18-INHERITED-THREE-MODE-REVIEW-30-1.5.0`  
**Authority:** D-110, retaining D-084–D-109 gallery scope  
**Status:** technical evidence PASS; owner visual approval pending

## Outcome

Review-30 preserves the 14 exact P-18 anchors and every prior P-19B remediation, then replaces only `state-machine` with an independently authored knowledge-content lifecycle. It contains one initial marker, four stable states, one terminal marker, five straight transitions and one rounded-orthogonal dashed return transition.

The owner screenshot informed structure and hierarchy only. Scenario, Vietnamese labels, semantic IDs, coordinates, CSS and SVG are original; the result inherits the approved P-18 review-17 palette, typography roles, ultra-thin outlines and restrained focal treatment. The `thien-skill-ui-ux-ultra` workflow contributed reference analysis, design-contract discipline and render inspection only; no code, template or asset was copied.

## Preservation and verification

- Exact review-29 was archived before mutation: 489 snapshot records and 11,550 protected records verified.
- Three `type-state-machine` HTML files changed; 87 non-target HTML artworks are equal after candidate-ID normalization.
- One state-machine preview changed; 29 non-target previews are byte-identical.
- All three modes serialize the same four state cards, initial/terminal markers and six transitions.
- Five normal routes are straight; the single return route is a documented rounded-orthogonal exception.
- All 12 connector endpoints attach to geometric edge midpoints under D-105.
- The neutral-light state machine was rasterized locally at 2000×980 and visually inspected without overlap, clipping, line-through-label or attachment drift.
- Browser execution remains `BLOCKED_URL_POLICY`; local raster evidence is not represented as a browser PASS.

Focused state-machine tests `3/3`, scope tests `8/8`, static verification `34/34` and full regression `363/363` pass. Exact review verification also passes.

## Boundary

P-19B review-30 is not owner-approved. P-19C remains not-started/unauthorized; G-04@1.5.0 remains NOT-EVALUATED. No package build, `dist`/publication mutation, commit, push, tag or Release operation was performed.

## Reproduction

```sh
PYTHONDONTWRITEBYTECODE=1 python3 evidence/p19/source/generate_p19b_gallery.py
PYTHONDONTWRITEBYTECODE=1 python3 evidence/p19/source/verify_p19b_review30.py
PYTHONPATH=thien-skill-creative-diagram/scripts:thien-skill-creative-diagram/scripts/tests:evidence/p19/source PYTHONDONTWRITEBYTECODE=1 python3 -m unittest thien-skill-creative-diagram/scripts/tests/test_state_machine_layout_v15.py
PYTHONDONTWRITEBYTECODE=1 python3 -m unittest discover -s evidence/p19/source -p 'test_*.py'
PYTHONDONTWRITEBYTECODE=1 python3 evidence/p19/source/verify_p19b.py
PYTHONPATH=evidence/p19/source:thien-skill-creative-diagram/scripts:thien-skill-creative-diagram/scripts/tests PYTHONDONTWRITEBYTECODE=1 python3 -m unittest discover -s thien-skill-creative-diagram/scripts/tests -p 'test_*.py'
PYTHONDONTWRITEBYTECODE=1 python3 evidence/p19/source/build_p19b_manifests.py
PYTHONDONTWRITEBYTECODE=1 python3 evidence/p19/comparison/generate_comparison.py
PYTHONDONTWRITEBYTECODE=1 python3 evidence/p19/comparison/generate_comparison.py --check
```
