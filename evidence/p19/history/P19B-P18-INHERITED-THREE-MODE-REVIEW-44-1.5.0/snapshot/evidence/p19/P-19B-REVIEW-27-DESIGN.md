# P-19B review-27 — thin-stroke tree refinement

Authority: D-107. Status: owner review pending.

## Design contract

Review-27 preserves the exact D-106 tree content, hierarchy, node geometry, centered-span fanout and three-mode composition. It repairs only visual stroke weight so the tree reads with the restrained line hierarchy of the approved P-18 org-chart.

- hierarchy connector: `2.6 → 1.6`
- regular branch/leaf card outline: `2.4 → 1.8`
- focal root outline: `3.0 → 2.2`

The root remains visually stronger than ordinary cards, while connectors remain lighter than every card outline. Badge, legend and separator strokes are unchanged.

## Invariants

- 9 nodes, 8 parent relations, 3 tiers and 14 straight connector primitives.
- Root and every parent remain centered over the exact child span.
- Three modes keep identical geometry.
- All emitted `rect`, `line` and `text` geometry is byte-equivalent to archived review-26.
- Only three `type-tree` HTML files and one tree preview may change artwork.

## Boundary

Exact review-26 is archived byte-bound before mutation. P-18, P-17, P-19A, package, `dist`, publication mirror, Git and Release remain untouched. P-19C and G-04 remain unauthorized/not evaluated.
