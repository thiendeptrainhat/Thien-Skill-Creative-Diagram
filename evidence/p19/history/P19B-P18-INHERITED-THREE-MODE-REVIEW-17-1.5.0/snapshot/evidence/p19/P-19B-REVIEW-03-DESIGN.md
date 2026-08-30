# D-082 — Gantt grouped-calendar remediation

Scope: P-19B only; candidate review-03; owner review pending. Route: change →
standalone SVG/HTML visual artifact → executive-artifact profile, reference
analysis, chart mechanics, localization, accessibility and rendered verification.

## Design lock

Single job: compare task timing and the review window across three phases.
Preserve P-18 review-17 tokens, warm dotted field, navy outlines, restrained coral,
typographic roles, three-mode geometry, all non-Gantt recipes and P-18 originals.
Repair the hard-coded two-bar Gantt using a shared timestamp scale; extend grouped
rows, month headers, calendar grid, task/gate/phase legend and exact-date table.
The supplied screenshot informs abstract hierarchy and grouping only. New code,
Vietnamese scenario, dates, spacing and proportions are independently authored;
this is clean-room-oriented independent reimplementation, not absolute clean room.
The offline chart search returned heatmap/line-chart suggestions, neither suitable;
they are not adopted. No additional fonts, assets or dependencies are introduced.

## Data authority

The owner explicitly approved original illustrative data: 3 phases, 6 ordinary
tasks and 1 gate across 3 months. The single schedule source is
`source/gantt_review03_fixture.py`; the frozen minimal P-19A fixture is unchanged.
The gate is a declared approval **window**, not a zero-duration milestone.
Intervals are half-open [start, end), ISO timestamps with UTC+07:00; no invented
dependencies. Original minimal input dependencies must still remain represented.

## Rendering and verification

One continuous time scale, actual calendar-month lengths, no duration inflation.
Phase bands enclose every owned row; bars have independent rows and balanced
vertical insets. Names stay in a left column. A GATE label and distinct outline
provide redundant encoding beyond color. Months and exact ISO timestamps are
available as text; all labels remain editable SVG text. No animation/JS or remote
resource. Long labels wrap; canvas height grows from content, never shrinks type.
Gantt has a content-fit wide canvas; other diagrams retain their existing viewBox.
Inspect actual SVG rasters in all three modes and run geometry/semantic regressions,
deterministic 129-HTML checks and comparison provenance checks. Preserve review-02
before mutation; compare all 126 non-Gantt HTML modulo candidate ID and all 42
non-Gantt previews byte-for-byte. Browser execution remains blocked by URL policy;
local raster checks are not browser, reflow, keyboard or screen-reader passes.
No P-19C, package, dist, publication or Git/Release action is authorized.
