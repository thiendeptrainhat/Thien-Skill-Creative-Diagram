# P-19B review-06 — detailed Fishbone remediation

**Candidate:** `P19B-P18-INHERITED-THREE-MODE-REVIEW-06-1.5.0`  
**Authority:** D-086, retaining D-084/D-085 gallery scope  
**Status:** in-progress / owner-review-pending  
**Date:** 2026-08-29

## Delivered

Review-06 changes only the P-19 Fishbone. Its independently authored illustrative
fixture declares five cause categories, two detailed causes per category and one
observed effect, `Hồ sơ xử lý trễ`. The data-driven renderer derives alternating
top/bottom bones, two cause ticks per bone, one continuous main spine, a coral
observed-effect card, a compact legend and an alternative semantic table.

P-19 now contains 75 canonical + 12 capability HTML = 87 specimens and 29 previews.
The gallery links the 14 approved originals separately. The comparison sheet
shows 101 diagrams: 14 P-18 + 87 P-19. It does not relabel an approved P-18 artifact
as new P-19 output. Generator filtering prevents duplicate rows from returning.

Gantt, loop-flywheel, dp-integration, all four capabilities and other retained
artwork are unchanged. Semantic source and the frozen P-19A adapter inventory
remain 39 canonical types + four capabilities; Bubble remains present despite
its parent scatter-plot being P-18-only in this gallery.

The UI/UX skill guided the P-18 visual inheritance, hierarchy, spacing and visual
QA. The supplied image was treated only as a non-executable abstract-anatomy
reference; no labels, code, CSS, SVG, template or asset were copied.

## Verification

- Focused renderer/Fishbone/Gantt/Flywheel tests: **60/60 PASS**.
- Gallery selection/scope regression tests: **8/8 PASS**.
- Active gallery static checks: **32/32 PASS**.
- Full canonical regression: **222/222 PASS**.
- Review-06 exact checks: **PASS** — 5 categories, 10 causes, 1 effect,
  alternating sides, tick→bone→spine→effect continuity, full semantic table and
  identical geometry across three modes.
- Review-05 immutable archive: **207 files** verified.
- Protected P-18/history/P-19A/dist/publication corpus: **3128 hashes** verified.
- Non-target preservation: **84 HTML** unchanged after candidate-ID normalization
  and **28 preview SVG** byte-identical.
- Neutral-light Fishbone was rasterized locally with Quick Look and visually
  inspected for canvas fit, label clipping, continuity and legend clarity.
  Evidence: `review06-checks/type-fishbone.svg.png`.
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
PYTHONDONTWRITEBYTECODE=1 python3 evidence/p19/source/verify_p19b_review06.py
PYTHONDONTWRITEBYTECODE=1 PYTHONPATH=thien-skill-creative-diagram/scripts:thien-skill-creative-diagram/scripts/tests:evidence/p19/source python3 -m unittest test_gallery_renderer_v15 test_fishbone_layout_v15 test_gantt_layout_v15 test_flywheel_layout_v15
```

Finalize plan/source manifests after evidence edits, then bind comparison pins
and run its deterministic `--check`. Never rerun archive/withdrawal operations
or historical candidate verifiers against the current gallery.
