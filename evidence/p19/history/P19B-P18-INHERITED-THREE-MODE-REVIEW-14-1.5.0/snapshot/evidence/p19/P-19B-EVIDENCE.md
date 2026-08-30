# P-19B review-14 — detailed Kanban board

**Candidate:** `P19B-P18-INHERITED-THREE-MODE-REVIEW-14-1.5.0`  
**Authority:** D-094, retaining D-084–D-093 gallery scope  
**Status:** in-progress / owner-review-pending  
**Date:** 2026-08-29

## Delivered

Review-14 preserves all accepted D-086–D-093 work and changes only the P-19 Kanban diagram. The replacement is an original four-column operational board with 11 work items distributed 3/4/2/2, one visible `4/3` WIP breach, one blocked item, one waiting-external item and two completed items.

The renderer derives all column ownership, item ordering, WIP status and work states from declared semantic material. State is not color-only: blocked and waiting use distinct dashed boundaries, blocked adds a coral rail, done uses separate fill/stroke, and the legend names every state. Geometry is identical across neutral-light, neutral-dark and editorial modes. The supplied image was treated as non-executable hierarchy/reference data; its prose, coordinates, CSS, SVG, template and assets were not copied.

The frozen P-17 grammar remains byte-identical. Because it rejects an already-exceeded structured group `wip_limit`, the illustrative operational limit `3` is encoded by a semantic annotation targeting the in-progress column; the renderer derives `4/3` from that annotation and its four owned items.

P-19 remains 75 canonical + 12 capability HTML = 87 specimens and 29 previews. The combined comparison remains 14 approved P-18 originals + 87 P-19 specimens = 101 diagrams.

## Verification

- Focused renderer/Kanban/current-state/high-level/ER/matrix/Bar/DP/Fishbone/Gantt/Flywheel tests: **116/116 PASS**.
- Gallery selection/scope regression tests: **8/8 PASS**.
- Active gallery static checks: **32/32 PASS**.
- Full canonical regression: **278/278 PASS**.
- Review-14 exact checks: **PASS** — 4 columns, 11 items, 3/4/2/2 distribution, one WIP breach, one blocked, one waiting-external and two done.
- Review-13 immutable archive: **311 files** verified.
- Protected P-18/history/P-19A/dist/publication corpus: **5143 hashes** verified.
- Non-target preservation: **84 HTML** unchanged after candidate-ID normalization and **28 preview SVG** byte-identical.
- Neutral-light Kanban was rasterized locally with Quick Look and inspected for hierarchy, text fit, card containment, WIP emphasis, non-color state cues and legend clearance. No clipping or overlap was observed. Exact SVG proofs for all three modes are under `review14-checks/`.
- Exact gallery manifest SHA-256: `1ee5be8ff832fd19725270be8349479048d92662ceb69cd3437116f9e09acef6`.

Browser remains **BLOCKED_NOT_EXECUTABLE** under the prior local-file URL policy. Quick Look raster inspection is focused visual evidence, not a browser, responsive, keyboard, computed-font or screen-reader PASS.

## Boundary

P-18 exact manifest SHA-256 remains `7925c1ab0515a59057851bb3888ff4d9974e5f5701b873b1f11468a5fd64a03a`.

P-19B review-14 is not owner-approved. P-19C remains not-started/unauthorized; G-04@1.5.0 remains NOT-EVALUATED. No package build, dist/publication mutation, commit, push, tag or Release operation.

## Repeat checks

```sh
PYTHONDONTWRITEBYTECODE=1 python3 evidence/p19/source/generate_p19b_gallery.py
PYTHONDONTWRITEBYTECODE=1 python3 evidence/p19/source/verify_p19b.py
PYTHONDONTWRITEBYTECODE=1 python3 evidence/p19/source/verify_p19b_review14.py
PYTHONDONTWRITEBYTECODE=1 PYTHONPATH=evidence/p19/source:thien-skill-creative-diagram/scripts:thien-skill-creative-diagram/scripts/tests python3 -m unittest test_kanban_layout_v15 test_it_current_state_layout_v15 test_high_level_layout_v15 test_er_data_model_layout_v15 test_dp_security_matrix_layout_v15 test_bar_chart_layout_v15 test_dp_integration_layout_v15 test_gallery_renderer_v15 test_fishbone_layout_v15 test_gantt_layout_v15 test_flywheel_layout_v15
```

Finalize plan/source manifests after evidence edits, then bind comparison pins and run its deterministic `--check`. Never rerun archive/withdrawal operations or historical candidate verifiers against the current gallery.
