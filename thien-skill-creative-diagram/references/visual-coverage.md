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
