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

P-19A adds `scripts/visual_adapters_v15.py` as a separate planning layer for all 39 canonical types and the four approved v1.5 capabilities. It validates semantic IR, selects the exact P-18R4 layout engine, projects type-specific semantic structures, declares a unique silhouette and accessible alternative, and preserves typography/geometry constraints for the next renderer phase.

The generated registry is [visual-adapters-v15.json](visual-adapters-v15.json). An adapter plan is not rendered evidence by itself and must not be passed to the historical P-07 renderer.

## P-19B three-mode QA renderer

P-19B remediation adds `scripts/gallery_renderer_v15.py` and generated binding [gallery-renderer-v15.json](gallery-renderer-v15.json). It consumes the validated P-19A plan, binds all 43 approved adapter identities to an explicit recipe across the exact 14 engines, and derives `neutral-light`, `neutral-dark`, and `editorial` without changing geometry or semantic IR. Active candidate `P19B-P18-INHERITED-THREE-MODE-REVIEW-17-1.5.0` binds the exact P-18R6 review-17 parent manifest and preserves its warm-paper/navy/coral, typography-role, frame, node, connector, grid and legend grammar. It retains D-090–D-096 behavior, then applies D-097 to `medallion`: five ordered stages, four directed promotion arcs, two processing paths and non-color focal/archive redundancy. The D-079 initial candidate is historical owner-rejected visual evidence under `evidence/p19/history/`.

Under D-084/D-085/D-095/D-096/D-097, the candidate gallery at `evidence/p19/gallery/` contains exactly 75 canonical plus 12 capability plus three `layers` presentation-variant standalone HTML specimens. Fourteen canonical types instead link directly to the unchanged approved P-18 review-17 neutral-light anchors. The gallery generator's `evidence/p19/source/p19_scope.py` selects the remaining 25 types plus all four capabilities; the D-095 fixture adds `layers` under parent `layer-stack`, D-096 details `line-chart`, and D-097 replaces only `medallion`, without modifying the frozen adapter registry. The generator must not emit duplicate P-19 canonical alternatives or derive extra P-18 modes. The combined viewer contains 104 diagrams; no three-mode coverage is claimed for the 14 P-18 originals. Each document is scriptless, network-independent, self-contained, machine-labelled, has a named inline SVG, and exposes an alternative semantic-ID table. `index.html` is a contact sheet and is not counted as a specimen.

P-19B is still QA-only and `in-progress` pending owner visual approval of the D-080 successor. Browser execution for the successor is `blocked / not executable` under local file URL policy; static inheritance and local raster evidence do not replace browser evidence. Full typography/glyph/containment, quantitative, pairwise, masked recognition, freeze and `G-04@1.5.0` evaluation remain P-19C. Do not include the gallery in a package or claim owner approval, release readiness or broad browser/accessibility conformance from the P-19B focused checks.
