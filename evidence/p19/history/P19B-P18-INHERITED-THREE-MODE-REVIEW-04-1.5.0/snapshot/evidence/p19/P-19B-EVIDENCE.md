# P-19B review-04 — six-station flywheel with shared state

**Candidate:** `P19B-P18-INHERITED-THREE-MODE-REVIEW-04-1.5.0`  
**Authority:** D-083, retaining D-080/D-081/D-082  
**Status:** in-progress / owner-review-pending  
**Date:** 2026-08-29

## Delivered

- Six rectangular stations around one circular path, continuous clockwise arrowed
  arcs, a larger dark “Tri thức chung” card, six dashed inward contribution
  spokes and one coral decision station.
- New original illustrative data in `source/flywheel_review04_fixture.py`.
  The cycle edges define order. Shared state is not a seventh station.
  Contributions are explicitly declared in two-target prose annotations; subtitles
  use one-target annotations. No semantic validator, schema, P-19A adapter or
  frozen minimal fixture was changed.
- New `scripts/flywheel_layout_v15.py` derives card placement and arc clipping from
  geometry. Shared circle, clockwise tangent directions, endpoint clearances and
  content-fit canvas; no erase overlay, label scaling or hidden dropped material.
  The native alternative table retains every node, edge and annotation.
- Exact 129 specimen HTML, 43 light previews and one gallery index retained.
  Three modes share identical SVG geometry. P-18 visual roles retained; central
  dark fill and light text deliberately retain contrast in all three modes.
- The reference guides abstract composition only. Text and implementation are
  original; no screenshot or upstream asset is embedded in diagram/package.
  The UI/UX skill guided preservation, reference analysis and rendered checks;
  the offline UX search's navigation-state suggestion was not adopted.

## Verification

- Focused renderer/Gantt/flywheel suites: **52/52 PASS**.
- Static exact gallery checks: **29/29 PASS**.
- Full canonical regression: **214/214 PASS**.
- `P-19B-REVIEW-04-VERIFICATION.json` verifies source-bound six cycle edges and six
  inward contributions, one shared-state node, one decision highlight, continuous
  serialized clockwise arcs, three-mode invariance, canvas/card separation and
  sampled arc/spoke clearance from every card.
- 126 non-target HTML are unchanged after candidate-ID normalization; 42
  non-target previews are byte-identical. This includes Gantt, dp-integration and
  swimlane, as well as fishbone/Sankey sharing the old special-geometry dispatcher.
- Three exact exported SVGs were rendered with macOS Quick Look at 1600px and
  visually inspected: neutral-light, neutral-dark, editorial. Vietnamese labels
  and subtitles are readable and contained; arrows follow the ring and dashed
  spokes point inward, with no observed text/line overlap.
- The actual canvas is 1600×1151. Quick Look square thumbnail padding is not part
  of the SVG. QA-only SVGs/PNGs and owner reference are in `review04-checks/`.
- Browser remains **BLOCKED_NOT_EXECUTABLE** under the prior local-file URL policy.
  No alternate browser/server bypass. Local raster inspection is not browser,
  reflow, keyboard, computed-font, screen-reader or full accessibility evidence.

## Preservation and boundary

Exact review-03 archived before mutation under
`history/P19B-P18-INHERITED-THREE-MODE-REVIEW-03-1.5.0/`: **238 archived files**
and **2569 protected file hashes** verified. Earlier review-02/03 reports and
proofs remain historical; do not rerun their scoped verifiers against review-04.

P-18 parent remains exact review-17 manifest SHA-256
`7925c1ab0515a59057851bb3888ff4d9974e5f5701b873b1f11468a5fd64a03a`.
P-18, P-19A, older archives, dist and publication mirror retain their protected
bytes. No package build, commit, push, tag or Release operation was performed.

Owner approval of review-04 is pending. P-19B in-progress; P-19C not-started and
unauthorized; G-04@1.5.0 NOT-EVALUATED. No broad visual PASS is claimed.

## Repeat checks

```sh
PYTHONDONTWRITEBYTECODE=1 python3 evidence/p19/source/generate_p19b_gallery.py
PYTHONDONTWRITEBYTECODE=1 python3 evidence/p19/source/verify_p19b.py
PYTHONDONTWRITEBYTECODE=1 python3 evidence/p19/source/verify_p19b_review04.py
PYTHONDONTWRITEBYTECODE=1 PYTHONPATH=thien-skill-creative-diagram/scripts:thien-skill-creative-diagram/scripts/tests python3 -m unittest discover -s thien-skill-creative-diagram/scripts/tests
```

Finalize plan/source manifests after evidence edits, then update the comparison
pins and run deterministic `--check`. Do not regenerate historical candidates.
