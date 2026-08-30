# P-19B review-28 — ultra-thin centered tree

**Candidate:** `P19B-P18-INHERITED-THREE-MODE-REVIEW-28-1.5.0`  
**Authority:** D-108, retaining D-084–D-107 gallery scope  
**Status:** technical evidence PASS; owner visual approval pending

## Outcome

Review-28 preserves the 14 exact P-18 anchors, all prior P-19B work and the complete D-106 tree geometry. Because review-27 remained perceptually heavy, it reduces the complete tree stroke system: connector `1.0`, regular card `1.2`, focal root `1.6`, badge `0.9`, separator `1.0`, and legend cards `1.2/1.6`.

The root remains stronger than branch/leaf cards, while connectors are lighter than every card. Badge, legend and separator strokes are unchanged. The tree remains one root, three category branches, five leaves and eight parent relations across three tiers.

## Preservation and verification

- Exact review-27 was archived before mutation: 468 snapshot files and 10,603 protected files verified.
- Three `type-tree` HTML files changed; 87 non-target HTML artworks are equal after candidate-ID normalization.
- One tree preview changed; 29 non-target previews are byte-identical.
- Every emitted tree `rect`, `line` and `text` geometry element is byte-equivalent to archived review-27.
- All three modes serialize the same 9 nodes, 8 parent relations, 3 tiers and exact connector geometry.
- Root center `x=1000` equals the midpoint of branch centers `360..1640`; branch intervals are `640/640`.
- Both two-child groups use offsets `-150/+150`; the one-child group is vertically aligned at `x=1640`.
- Four parent-span centering proofs and one direct single-child proof pass in every mode.
- All 90 P-19 SVGs retain the D-105 centered/even/straight-first connector-policy declaration.
- Neutral-light tree was rasterized locally with Sharp after resolving CSS variables in a proof-only SVG, then visually inspected. The hierarchy, labels and connectors are visible without collision.
- Exact SVG proof, proof-only resolved SVG and inspected raster are under `review28-checks/`.
- Browser execution remains `BLOCKED_URL_POLICY`; local raster evidence is not represented as a browser PASS.

Final verification is green: focused tree tests 6/6, scope 8/8, static 34/34 and full regression 357/357 PASS.

## Boundary

P-19B review-28 is not owner-approved. P-19C remains not-started/unauthorized; G-04@1.5.0 remains NOT-EVALUATED. No package build, `dist`/publication mutation, commit, push, tag or Release operation was performed.

## Reproduction

```sh
PYTHONDONTWRITEBYTECODE=1 python3 evidence/p19/source/generate_p19b_gallery.py
PYTHONDONTWRITEBYTECODE=1 python3 evidence/p19/source/verify_p19b_review28.py
PYTHONDONTWRITEBYTECODE=1 PYTHONPATH=evidence/p19/source:thien-skill-creative-diagram/scripts:thien-skill-creative-diagram/scripts/tests python3 -m unittest test_tree_layout_v15
PYTHONDONTWRITEBYTECODE=1 python3 -m unittest discover -s evidence/p19/source -p 'test_*.py'
PYTHONDONTWRITEBYTECODE=1 python3 evidence/p19/source/verify_p19b.py
PYTHONDONTWRITEBYTECODE=1 PYTHONPATH=evidence/p19/source:thien-skill-creative-diagram/scripts:thien-skill-creative-diagram/scripts/tests python3 -m unittest discover -s thien-skill-creative-diagram/scripts/tests -p 'test_*.py'
PYTHONDONTWRITEBYTECODE=1 python3 evidence/p19/source/build_p19b_manifests.py
PYTHONDONTWRITEBYTECODE=1 python3 evidence/p19/comparison/generate_comparison.py
PYTHONDONTWRITEBYTECODE=1 python3 evidence/p19/comparison/generate_comparison.py --check
```
