# P-07 static visual coverage

P-07 extends the approved P-06 visual system to all 27 canonical types while keeping the same three modes: `neutral-light`, `neutral-dark`, and `editorial`.

## Rendering contract

- Validate common IR and the selected type grammar before rendering.
- Use `scripts/full_renderer.py::render_static` for deterministic, self-contained static SVG coverage.
- Preserve all material labels and quantitative values in visible or accessible text.
- Keep node boxes within the 1600×900 coverage canvas, prohibit node overlap, use unique IDs, and reject executable or external SVG content.
- Use family-specific composition for graph/topology, ordered interaction, timeline, owned lanes/layers, cartesian charts, radar, cycle, containment/set membership, funnel, Gantt, and permission matrix.
- Variants retain their canonical parent. `CAP-V15` uses a text-equivalent fallback because symbol assets remain owned by P-09.
- The seven semantic patterns render only after their P-05 transformation under the existing canonical parent.

The exact 95-capability disposition is in [visual-coverage-map.json](visual-coverage-map.json). The locked 97-specimen grouping remains in [specimen-map.json](specimen-map.json); P-07 evidence verifies the group counts without altering the approved P-05 inventory.

## Deferred boundary

This renderer remains the P-07 static coverage layer, not the portable exporter or motion layer. Those behaviors were deferred at P-07 close and are now implemented separately by P-08 in [output-motion.md](output-motion.md). A P-07 script-free static result is evidence of the fallback frame; use the P-08 ledger to claim export or motion behavior.

## P-19A adapter layer

P-19A adds `scripts/visual_adapters_v15.py` as a separate planning layer for all 39 canonical types and four capability variants. It validates semantic IR, selects the approved P-18 layout-engine family, projects type-specific semantic structures, declares an accessible alternative, and preserves typography/geometry constraints for rendering. The engine plan is a starting structure: an explicit user request may safely change content, structure, layout, visual treatment, and presentation without being restricted to a frozen specimen.

The generated registry is [visual-adapters-v15.json](visual-adapters-v15.json). An adapter plan is not rendered evidence by itself and must not be passed to the historical P-07 renderer.

## P-19B three-mode QA renderer

P-19B remediation adds `scripts/gallery_renderer_v15.py` and generated binding [gallery-renderer-v15.json](gallery-renderer-v15.json). It consumes the validated P-19A plan and reproduces the exact three-mode QA specimens across 14 engine families. Exact candidate `P19B-P18-INHERITED-THREE-MODE-REVIEW-45-1.5.0` binds the P-18R6 review-17 visual parent and preserves its warm-paper/navy/coral, typography-role, frame, node, connector, grid, and legend grammar. D-084–D-125 record the independent remediation lineage; D-079 remains historical owner-rejected evidence.

The frozen gallery at `evidence/p19/gallery/` contains exactly 75 canonical, 12 capability, three `layers`, and three `scatter-chart` standalone HTML specimens: 93 P-19 artifacts with 31 preview identities. Fourteen canonical types link separately to unchanged P-18 review-17 neutral-light anchors. The combined viewer therefore contains exactly `14 + 93 = 107` diagrams, and P-19 never replaces or regenerates P-18. Each P-19 document is scriptless, network-independent, self-contained, machine-labelled, has a named inline SVG, and exposes an alternative semantic-ID table. `index.html` is a contact sheet and is not counted as a specimen.

P-19B review-45 was owner-approved under D-126. P-19C review-01 completed the frozen QA evidence under D-128, and G-04@1.5.0 passed under D-129. Those decisions approve the exact evidence candidate only. The gallery, its 31 preview/masked silhouettes, and its fixed fixtures remain QA-only and are excluded from package payloads. They do not constrain user output: safely adapt the selected type, data, structure, layout, styling, and presentation to the request, then run checks appropriate to that new artifact.
