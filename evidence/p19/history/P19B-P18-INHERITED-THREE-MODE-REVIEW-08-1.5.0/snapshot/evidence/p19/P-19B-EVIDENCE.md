# P-19B review-08 — detailed bar-chart remediation

**Candidate:** `P19B-P18-INHERITED-THREE-MODE-REVIEW-08-1.5.0`  
**Authority:** D-088, retaining D-084–D-087 gallery scope  
**Status:** in-progress / owner-review-pending  
**Date:** 2026-08-29

## Delivered

Review-08 changes only P-19 bar-chart. Its independently authored illustrative
fixture declares one eight-sprint series, two axes, a linear 0–120 point domain and
one record-high annotation targeting Sprint 5. The renderer derives eight equal-width
bars on one zero-baseline, six horizontal tick/grid levels, direct numeric/category
labels, a redundant focal treatment, legend and exact-value semantic table.

P-19 now contains 75 canonical + 12 capability HTML = 87 specimens and 29 previews.
The gallery links the 14 approved originals separately. The comparison sheet
shows 101 diagrams: 14 P-18 + 87 P-19. It does not relabel an approved P-18 artifact
as new P-19 output. Generator filtering prevents duplicate rows from returning.

Gantt, loop-flywheel, Fishbone, dp-integration, all four capabilities and other
retained artwork are unchanged. Semantic source and the frozen P-19A adapter inventory
remain 39 canonical types + four capabilities; Bubble remains present despite
its parent scatter-plot being P-18-only in this gallery.

The D-086 Fishbone and D-087 dp-integration remain byte-identical outside candidate
metadata. The UI/UX skill guided P-18 visual inheritance, chart mechanics, hierarchy,
redundant encoding and visual QA. The supplied image was treated only as a
non-executable chart reference; exact values, coordinates, code, CSS, SVG, template
and assets were not copied.

## Verification

- Focused renderer/Bar/DP/Fishbone/Gantt/Flywheel tests: **75/75 PASS**.
- Gallery selection/scope regression tests: **8/8 PASS**.
- Active gallery static checks: **32/32 PASS**.
- Full canonical regression: **237/237 PASS**.
- Review-08 exact checks: **PASS** — 8 bars, 2 axes, 6 ticks, 1 focal record high,
  exact zero-baseline, direct labels, full exact-value table and identical geometry
  across three modes.
- Review-07 immutable archive: **230 files** verified.
- Protected P-18/history/P-19A/dist/publication corpus: **3553 hashes** verified.
- Non-target preservation: **84 HTML** unchanged after candidate-ID normalization
  and **28 preview SVG** byte-identical.
- All three bar-chart modes were rasterized locally with Quick Look and inspected
  at useful scale for label fit, bar spacing, baseline alignment, grid hierarchy,
  focal redundancy and legend clearance. No clipping or overlap was observed.
  Evidence: `review08-checks/type-bar-chart--*.svg.png`.
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
PYTHONDONTWRITEBYTECODE=1 python3 evidence/p19/source/verify_p19b_review08.py
PYTHONDONTWRITEBYTECODE=1 PYTHONPATH=thien-skill-creative-diagram/scripts:thien-skill-creative-diagram/scripts/tests:evidence/p19/source python3 -m unittest test_bar_chart_layout_v15 test_dp_integration_layout_v15 test_gallery_renderer_v15 test_fishbone_layout_v15 test_gantt_layout_v15 test_flywheel_layout_v15
```

Finalize plan/source manifests after evidence edits, then bind comparison pins
and run its deterministic `--check`. Never rerun archive/withdrawal operations
or historical candidate verifiers against the current gallery.
