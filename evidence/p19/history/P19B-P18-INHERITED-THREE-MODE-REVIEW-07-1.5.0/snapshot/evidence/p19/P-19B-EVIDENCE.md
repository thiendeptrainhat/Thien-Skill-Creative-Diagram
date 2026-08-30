# P-19B review-07 — detailed DP integration remediation

**Candidate:** `P19B-P18-INHERITED-THREE-MODE-REVIEW-07-1.5.0`  
**Authority:** D-087, retaining D-084–D-086 gallery scope  
**Status:** in-progress / owner-review-pending  
**Date:** 2026-08-29

## Delivered

Review-07 changes only P-19 dp-integration. Its independently authored illustrative
fixture declares three sources, three data-platform core services, three consumers,
two shared services, eleven directed integrations and one platform boundary. The
renderer derives a source→platform→consumer map, orchestration rail, focal store/query
cards, identity/observability bands, protocol labels, type-key legend and semantic table.

P-19 now contains 75 canonical + 12 capability HTML = 87 specimens and 29 previews.
The gallery links the 14 approved originals separately. The comparison sheet
shows 101 diagrams: 14 P-18 + 87 P-19. It does not relabel an approved P-18 artifact
as new P-19 output. Generator filtering prevents duplicate rows from returning.

Gantt, loop-flywheel, dp-integration, all four capabilities and other retained
artwork are unchanged. Semantic source and the frozen P-19A adapter inventory
remain 39 canonical types + four capabilities; Bubble remains present despite
its parent scatter-plot being P-18-only in this gallery.

The D-086 Fishbone remains byte-identical outside candidate metadata. The UI/UX
skill guided P-18 visual inheritance, hierarchy, spacing and visual QA. The supplied
image was treated only as a non-executable topology reference; no English labels,
exact coordinates, icons, code, CSS, SVG, template or asset were copied.

## Verification

- Focused renderer/DP/Fishbone/Gantt/Flywheel tests: **68/68 PASS**.
- Gallery selection/scope regression tests: **8/8 PASS**.
- Active gallery static checks: **32/32 PASS**.
- Full canonical regression: **230/230 PASS**.
- Review-07 exact checks: **PASS** — 11 nodes, 11 directed edges, 1 platform
  group, exact containment/endpoints, continuous routes, full semantic table and
  identical geometry across three modes.
- Review-06 immutable archive: **216 files** verified.
- Protected P-18/history/P-19A/dist/publication corpus: **3336 hashes** verified.
- Non-target preservation: **84 HTML** unchanged after candidate-ID normalization
  and **28 preview SVG** byte-identical.
- All three dp-integration modes were rasterized locally with Quick Look. The first
  pass exposed two clipped external-card details; card widths/routes were revised,
  then all modes were re-rendered and inspected for fit, clipping and continuity.
  Evidence: `review07-checks/type-dp-integration--*.svg.png`.
- Comparison generator checks exact coverage, every source link, inert embedded
  SVG, exact P-18 preview bytes and deterministic output. Its manifest records
  the actual results; no diagram geometry/style is changed by the viewer.

Browser remains **BLOCKED_NOT_EXECUTABLE** under the prior local-file URL policy.
No alternate server/browser bypass. The local raster is a focused visual check,
not a broad browser/visual-craft PASS. Browser responsive, keyboard, computed-font
and screen-reader checks remain unverified.

## Boundary

P-18 exact manifest SHA-256:
`7925c1ab0515a59057851bb3888ff4d9974e5f5701b873b1f11468a5fd64a03a`.

P-19B is not owner-approved. P-19C remains not-started/unauthorized;
G-04@1.5.0 remains NOT-EVALUATED. No package build, dist/publication mutation,
commit, push, tag or Release operation.

## Repeat checks

```sh
PYTHONDONTWRITEBYTECODE=1 python3 evidence/p19/source/generate_p19b_gallery.py
PYTHONDONTWRITEBYTECODE=1 python3 evidence/p19/source/verify_p19b.py
PYTHONDONTWRITEBYTECODE=1 python3 evidence/p19/source/verify_p19b_review07.py
PYTHONDONTWRITEBYTECODE=1 PYTHONPATH=thien-skill-creative-diagram/scripts:thien-skill-creative-diagram/scripts/tests:evidence/p19/source python3 -m unittest test_dp_integration_layout_v15 test_gallery_renderer_v15 test_fishbone_layout_v15 test_gantt_layout_v15 test_flywheel_layout_v15
```

Finalize plan/source manifests after evidence edits, then bind comparison pins
and run its deterministic `--check`. Never rerun archive/withdrawal operations
or historical candidate verifiers against the current gallery.
