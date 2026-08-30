# P-19B review-26 — centered three-tier tree

**Candidate:** `P19B-P18-INHERITED-THREE-MODE-REVIEW-26-1.5.0`  
**Authority:** D-106, retaining D-084–D-105 gallery scope  
**Status:** technical evidence PASS; owner visual approval pending

## Outcome

Review-26 preserves the 14 exact P-18 anchors and all prior P-19B work, then changes only `tree`. The independently authored fixture contains one root, three category branches, five leaves and eight parent relations across three tiers.

The layout turns the P-18 `org-chart` centering rule into exact geometry: the root is centered over the complete branch span; every multi-child parent is centered between its two outermost children; same-tier branch spacing is equal; two-child offsets are symmetric; and the single-child branch uses one direct centered line. Multi-child fanout uses a centered trunk, shared horizontal bus and centered drops. Connectors are 14 straight primitives with no arrowheads or curves, and all endpoints attach at card-edge centers.

## Preservation and verification

- Exact review-25 was archived before mutation: 448 snapshot files and 9,694 protected files verified.
- Three `type-tree` HTML files changed; 87 non-target HTML artworks are equal after candidate-ID normalization.
- One tree preview changed; 29 non-target previews are byte-identical.
- All three modes serialize the same 9 nodes, 8 parent relations, 3 tiers and exact connector geometry.
- Root center `x=1000` equals the midpoint of branch centers `360..1640`; branch intervals are `640/640`.
- Both two-child groups use offsets `-150/+150`; the one-child group is vertically aligned at `x=1640`.
- Four parent-span centering proofs and one direct single-child proof pass in every mode.
- All 90 P-19 SVGs retain the D-105 centered/even/straight-first connector-policy declaration.
- Neutral-light tree was rasterized locally with Sharp after resolving CSS variables in a proof-only SVG, then visually inspected. The hierarchy, labels and connectors are visible without collision.
- Exact SVG proof, proof-only resolved SVG and inspected raster are under `review26-checks/`.
- Browser execution remains `BLOCKED_URL_POLICY`; local raster evidence is not represented as a browser PASS.

Final verification is green: focused tree tests 5/5, scope 8/8, static 34/34 and full regression 356/356 PASS.

## Boundary

P-19B review-26 is not owner-approved. P-19C remains not-started/unauthorized; G-04@1.5.0 remains NOT-EVALUATED. No package build, `dist`/publication mutation, commit, push, tag or Release operation was performed.

## Reproduction

```sh
PYTHONDONTWRITEBYTECODE=1 python3 evidence/p19/source/generate_p19b_gallery.py
PYTHONDONTWRITEBYTECODE=1 python3 evidence/p19/source/verify_p19b_review26.py
PYTHONDONTWRITEBYTECODE=1 PYTHONPATH=evidence/p19/source:thien-skill-creative-diagram/scripts:thien-skill-creative-diagram/scripts/tests python3 -m unittest test_tree_layout_v15
PYTHONDONTWRITEBYTECODE=1 python3 -m unittest discover -s evidence/p19/source -p 'test_*.py'
PYTHONDONTWRITEBYTECODE=1 python3 evidence/p19/source/verify_p19b.py
PYTHONDONTWRITEBYTECODE=1 PYTHONPATH=evidence/p19/source:thien-skill-creative-diagram/scripts:thien-skill-creative-diagram/scripts/tests python3 -m unittest discover -s thien-skill-creative-diagram/scripts/tests -p 'test_*.py'
PYTHONDONTWRITEBYTECODE=1 python3 evidence/p19/source/build_p19b_manifests.py
PYTHONDONTWRITEBYTECODE=1 python3 evidence/p19/comparison/generate_comparison.py
PYTHONDONTWRITEBYTECODE=1 python3 evidence/p19/comparison/generate_comparison.py --check
```
