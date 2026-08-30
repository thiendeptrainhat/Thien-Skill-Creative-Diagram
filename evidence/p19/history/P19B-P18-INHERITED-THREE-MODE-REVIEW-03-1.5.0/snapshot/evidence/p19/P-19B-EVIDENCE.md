# P-19B review-03 — grouped-calendar Gantt

**Candidate:** `P19B-P18-INHERITED-THREE-MODE-REVIEW-03-1.5.0`  
**Authority:** D-082, retaining D-080/D-081  
**Status:** in-progress / owner-review-pending  
**Date:** 2026-08-29

## Delivered

- Gantt now follows the reference's abstract calendar/grouped-row grammar: month
  header, left-side labels, enclosing phase bands, neutral task bars, coral gate
  window and task/gate/phase legend.
- Original illustrative data: three phases, six ordinary tasks and one approval
  window across September–November 2026. Single source:
  `source/gantt_review03_fixture.py`. Not actual project dates or copied reference
  content. The frozen minimal P-19A fixture is untouched.
- Actual timestamp geometry, 91-day shared calendar scale, exact month lengths,
  timezone-aware half-open intervals and a native exact-date/semantic-ID table.
  Zero-duration input gets a marker; a short interval is never visually inflated.
- New reusable `scripts/gantt_layout_v15.py` drives Gantt only. Timeline and all
  other diagram recipes remain unchanged. P-18 tokens, material/technical font
  roles and dot-field remain; all three modes share identical SVG geometry.
- Exact 129 specimen HTML, 43 neutral-light previews and one gallery index.
  The auxiliary comparison still contains all 14 P-18 and 129 P-19 previews.
- Prior dp-integration containment and swimlane continuity repairs are preserved.

## Evidence and checks

- Focused renderer/calendar tests: **38/38 PASS** (24 existing + 14 added).
- Static gallery checks: **29/29 PASS**, including exact counts, security,
  deterministic regeneration, hashes, lineage and three-mode invariance.
- Full canonical regression: **200/200 PASS**.
- `P-19B-REVIEW-03-VERIFICATION.json`: three-mode calendar/containment assertions;
  126 non-Gantt HTML unchanged after candidate-ID normalization; 42 non-Gantt
  previews byte-identical; 223 archived and 2345 protected file hashes match.
- Three exact local SVG exports rendered with macOS Quick Look at 1600px, then
  visually inspected in neutral-light, neutral-dark and editorial. Vietnamese
  labels are legible, no observed bar/label overlap, phase borders enclose rows,
  and GATE is visible. SVG canvas is content-fit 1600×900; Quick Look's square
  thumbnail padding is not part of the SVG canvas.
- Rasters, source SVGs and the owner's reference are QA-only in `review03-checks/`.
  The reference is not embedded in generated diagrams or any package.
- Browser remains **BLOCKED_NOT_EXECUTABLE** after the earlier file-URL policy
  rejection. No bypass attempted. Local raster evidence is not browser, reflow,
  keyboard, computed-font, screen-reader or full accessibility verification.

The initial focused run exposed two outdated anatomy expectations: a fixed count
of SVG titles and a generic-only table. Gantt now retains the Semantic IDs column
alongside exact dates, and tests additionally require one date tooltip per mark.
The final focused/static/full suites above passed; no checks were disabled.

## Preserved lineage

Exact review-02 was archived before mutation under
`history/P19B-P18-INHERITED-THREE-MODE-REVIEW-02-1.5.0/`. Its receipt binds the
gallery/plan/source manifest triplet and 223 copied files. The review-02 evidence
there records the D-081 repairs and nine earlier focused raster proofs; the old
active `P-19B-REVIEW-02-VERIFICATION.json` remains historical and must not be rerun
against review-03.

Visual parent remains exact
`P18R6-FOURTEEN-ENGINE-NEUTRAL-LIGHT-REVIEW-17-1.5.0`, manifest SHA-256
`7925c1ab0515a59057851bb3888ff4d9974e5f5701b873b1f11468a5fd64a03a`.
P-18 corpus, P-19A adapter/minimal fixture/manifests, older P-19 history, dist and
publication mirror retain their protected bytes. No package build, commit, push,
tag, release or publication mutation was performed.

## Stop and reproduce

Owner approval of review-03 is pending. P-19B remains in-progress, P-19C not-started
and unauthorized; G-04@1.5.0 NOT-EVALUATED. No broad visual PASS is claimed.

```sh
PYTHONDONTWRITEBYTECODE=1 python3 evidence/p19/source/generate_p19b_gallery.py
PYTHONDONTWRITEBYTECODE=1 python3 evidence/p19/source/verify_p19b.py
PYTHONDONTWRITEBYTECODE=1 python3 evidence/p19/source/verify_p19b_review03.py
PYTHONDONTWRITEBYTECODE=1 PYTHONPATH=thien-skill-creative-diagram/scripts:thien-skill-creative-diagram/scripts/tests python3 -m unittest discover -s thien-skill-creative-diagram/scripts/tests
```

Finalize the source/plan manifests after governance/evidence edits; then update the
comparison's exact pins and run its deterministic `--check`. Do not regenerate
historical archives. Manifest creation is not a package build or phase freeze.
