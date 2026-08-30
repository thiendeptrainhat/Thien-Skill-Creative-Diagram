# P-19B review-26 — centered three-tier tree

Authority: D-106. Status: owner review pending.

## Design premise

The P-19 `tree` is now a detailed three-tier capability hierarchy rather than a generic three-node sample. It inherits the approved P-18 org-chart geometry: the root is centered over the complete descendant span; every multi-child parent is centered over the midpoint between its outermost child centers; every single-child parent and child share one center axis.

Multi-child fanout uses one centered vertical trunk, one horizontal bus and evenly placed vertical drops. A single-child relation is one direct vertical line. The hierarchy does not use arrowheads because rank and enclosure establish parent-to-child reading order. All attachment points land on card-edge centers.

## Independent expression

The owner image is used only as a structural rubric for three tiers, detail density, root/branch/leaf roles and orthogonal hierarchy reading. Vietnamese labels, semantic fixture, dimensions, spacing, CSS, SVG, legend and table are independently authored. No text, coordinates, template, code or asset is copied.

## Acceptance geometry

- 9 nodes, 8 parent relations and 3 tiers.
- Root center `x=1000` equals the midpoint of the branch span `x=360..1640`.
- Branch centers are evenly spaced at `x=360`, `1000`, `1640`.
- Two-child groups use symmetric child offsets of `±150` from their parent.
- The single-child research branch is a direct centered line at `x=1640`.
- 14 straight connector primitives, no arrowhead and no corner curve.
- The exact geometry is identical across neutral-light, neutral-dark and editorial modes.

## Boundary

Review-25 was archived byte-bound before mutation. Only the three `type-tree` HTML specimens and one tree preview may change artwork; P-18, P-17, P-19A, package, `dist`, publication mirror, Git and Release remain untouched. P-19C and G-04 remain unauthorized/not evaluated.
