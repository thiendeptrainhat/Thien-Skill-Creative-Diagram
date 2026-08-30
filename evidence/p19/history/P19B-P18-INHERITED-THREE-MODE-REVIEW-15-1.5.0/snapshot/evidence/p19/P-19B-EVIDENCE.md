# P-19B review-15 — Layers presentation variant

**Candidate:** `P19B-P18-INHERITED-THREE-MODE-REVIEW-15-1.5.0`  
**Authority:** D-095, retaining D-084–D-094 gallery scope  
**Status:** in-progress / owner-review-pending  
**Date:** 2026-08-29

## Delivered

Review-15 preserves all D-086–D-094 detailed work and adds a new presentation identity `layers` under canonical parent `layer-stack`. It does not change the frozen 39-type semantic taxonomy, P-17 grammar or P-19A adapter registry.

The new diagram contains five contiguous bands L5→L1, an upward abstraction axis, direct level/title/scope labels, and one focal `Điều phối quy trình` layer. Focal meaning is not color-only: it combines coral boundary/fill, a visible `TRỌNG TÂM` tag and an explanatory note. The three modes use identical SVG geometry and expose an exact five-row alternative table.

The owner image was treated only as a non-executable rubric for ordered bands, axis direction and focal emphasis. Vietnamese scenario content, semantic data, layout, CSS and SVG are independently authored.

P-19 now contains 75 canonical + 12 capability + 3 Layers-variant HTML = 90 specimens and 30 previews. The comparison contains 14 approved P-18 originals + 90 P-19 specimens = 104 diagrams.

## Verification

- Review-15 exact checks: **PASS** — 5 layers, one focal layer, one abstraction axis, four declared dependencies, exact alternative table and three-mode geometry.
- Review-14 immutable archive: **322 files** verified.
- Protected P-18/history/P-19A/P-17 grammar/dist/publication corpus: **5456 hashes** verified.
- Prior-artwork preservation: **87 HTML** unchanged after candidate-ID normalization and **29 preview SVG** byte-identical.
- Active gallery static checks: **34/34 PASS**.
- Neutral-light Layers was rasterized locally with Quick Look and inspected for five-band hierarchy, text fit, row continuity, abstraction-axis clearance, focal tag/note redundancy and clipping/overlap; no visual defect was observed.
- Focused detailed-layout suite: **124/124 PASS**; gallery scope suite: **8/8 PASS**; full regression: **286/286 PASS**.
- Exact SVG proofs for all three modes are under `review15-checks/`.
- Exact gallery manifest SHA-256 is recorded in `P-19B-REVIEW-15-VERIFICATION.json` and the active manifests.

Browser remains **BLOCKED_NOT_EXECUTABLE** under the prior local-file URL policy. Local raster inspection is focused visual evidence, not browser, responsive, keyboard, computed-font or screen-reader PASS.

## Boundary

P-18 exact manifest SHA-256 remains `7925c1ab0515a59057851bb3888ff4d9974e5f5701b873b1f11468a5fd64a03a`.

P-19B review-15 is not owner-approved. P-19C remains not-started/unauthorized; G-04@1.5.0 remains NOT-EVALUATED. No package build, dist/publication mutation, commit, push, tag or Release operation.

## Repeat checks

```sh
PYTHONDONTWRITEBYTECODE=1 python3 evidence/p19/source/generate_p19b_gallery.py
PYTHONDONTWRITEBYTECODE=1 python3 evidence/p19/source/verify_p19b.py
PYTHONDONTWRITEBYTECODE=1 python3 evidence/p19/source/verify_p19b_review15.py
PYTHONDONTWRITEBYTECODE=1 PYTHONPATH=evidence/p19/source:thien-skill-creative-diagram/scripts:thien-skill-creative-diagram/scripts/tests python3 -m unittest test_layers_layout_v15 test_kanban_layout_v15 test_it_current_state_layout_v15 test_high_level_layout_v15 test_er_data_model_layout_v15 test_dp_security_matrix_layout_v15 test_bar_chart_layout_v15 test_dp_integration_layout_v15 test_gallery_renderer_v15 test_fishbone_layout_v15 test_gantt_layout_v15 test_flywheel_layout_v15
```

Finalize plan/source manifests after evidence edits, then bind comparison pins and run its deterministic `--check`. Never rerun archive/withdrawal operations or historical candidate verifiers against the current gallery.
