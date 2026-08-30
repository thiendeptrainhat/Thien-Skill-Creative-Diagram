# P-19B review-29 — detailed story map

**Candidate:** `P19B-P18-INHERITED-THREE-MODE-REVIEW-29-1.5.0`  
**Authority:** D-109, retaining D-084–D-108 gallery scope  
**Status:** technical evidence PASS; owner visual approval pending

## Outcome

Review-29 preserves the 14 exact P-18 anchors and every prior P-19B remediation, then replaces only `story-map` with an independently authored four-activity map. It contains six backbone steps, nine story cards, three release slices, one labeled MVP cut and one high-risk story with dashed-boundary, badge and exact-table redundancy.

The owner screenshot informed structure and hierarchy only. Scenario, Vietnamese labels, semantic fixture, coordinates, CSS and SVG are original; the result inherits the approved P-18 review-17 palette, typography roles, thin outlines and restrained focal treatment.

## Preservation and verification

- Exact review-28 was archived before mutation: 477 snapshot records and 11,072 protected records verified.
- Three `type-story-map` HTML files changed; 87 non-target HTML artworks are equal after candidate-ID normalization.
- One story-map preview changed; 29 non-target previews are byte-identical.
- All three modes serialize the same 4 activities, 6 steps, 9 stories, 3 release slices, one MVP cut and one risk story.
- All 90 P-19 SVGs retain the D-105 centered/even/straight-first connector-policy declaration.
- The neutral-light story map was rasterized locally at 2000×1040 and visually inspected without overlap or clipping.
- Browser execution remains `BLOCKED_URL_POLICY`; local raster evidence is not represented as a browser PASS.

Final verification is green: focused story-map `3/3`, scope `8/8`, static `34/34` and full regression `360/360` PASS.

## Boundary

P-19B review-29 is not owner-approved. P-19C remains not-started/unauthorized; G-04@1.5.0 remains NOT-EVALUATED. No package build, `dist`/publication mutation, commit, push, tag or Release operation was performed.

## Reproduction

```sh
PYTHONDONTWRITEBYTECODE=1 python3 evidence/p19/source/generate_p19b_gallery.py
PYTHONDONTWRITEBYTECODE=1 python3 evidence/p19/source/verify_p19b_review29.py
PYTHONPATH=thien-skill-creative-diagram/scripts:thien-skill-creative-diagram/scripts/tests:evidence/p19/source PYTHONDONTWRITEBYTECODE=1 python3 -m unittest thien-skill-creative-diagram/scripts/tests/test_story_map_layout_v15.py
PYTHONDONTWRITEBYTECODE=1 python3 -m unittest discover -s evidence/p19/source -p 'test_*.py'
PYTHONDONTWRITEBYTECODE=1 python3 evidence/p19/source/verify_p19b.py
PYTHONPATH=evidence/p19/source:thien-skill-creative-diagram/scripts:thien-skill-creative-diagram/scripts/tests PYTHONDONTWRITEBYTECODE=1 python3 -m unittest discover -s thien-skill-creative-diagram/scripts/tests -p 'test_*.py'
PYTHONDONTWRITEBYTECODE=1 python3 evidence/p19/source/build_p19b_manifests.py
PYTHONDONTWRITEBYTECODE=1 python3 evidence/p19/comparison/generate_comparison.py
PYTHONDONTWRITEBYTECODE=1 python3 evidence/p19/comparison/generate_comparison.py --check
```
