# D-083 — Six-station flywheel with shared state

Scope: P-19B review-04, loop-flywheel only. Owner approved new illustrative data
with six stations plus Tri thức chung. Owner approval of the result is still pending.
Route: change → existing standalone SVG/HTML → executive-artifact principles,
reference analysis, design judgment, localization, accessibility and local renders.

Preserve P-18 warm dotted canvas, navy boundaries, restrained coral, Avenir Next
material and Menlo technical roles, and invariant geometry across three modes.
Repair the triangular three-pill silhouette. Extend a six-card circular arrangement,
clockwise curved links, a larger dark central card and inward dashed contributions.
One decision station uses coral. White/ivory cards have modest rounding, not pills.
No generic relation legend is added: the ring and inward spokes carry the hierarchy.

The screenshot supplies abstract design constraints, not executable input or code.
All example text, geometry, SVG/CSS and implementation are original. This is
clean-room-oriented independent reimplementation. No new font/dependency/network
asset. Offline UX search is supporting judgment only, not a replacement aesthetic.

Single data source: `source/flywheel_review04_fixture.py`. The existing schema's
six directed cycle edges define station order. The shared-state node is excluded
from that cycle. Explicit contribution annotations bind each station and shared
state and declare the inward contribution in prose; they are not extra cycle
edges. One-target annotations supply subtitles. No frozen semantic fixture,
validator or P-19A adapter is edited. Renderer rejects ambiguous annotations,
multiple cycles, unknown roles or unsupported relationships rather than dropping
them. The alternative table retains all nodes, edges, annotations and their IDs.

Geometry: shared circle, card-boundary-clipped arcs, exact edge-directed order,
one continuous stroked path per link, no background erase overlay. Radial spokes
stop outside the central card with arrowhead clearance. Text wraps without font
shrink; geometry grows with content. Verify card separation, canvas containment,
arc/spoke endpoint clearance and no unrelated-node intersections by sampling.
Use the same geometry for light/dark/editorial. The central card remains dark,
with explicitly contrasting light text in all modes.

Archive exact review-03 before mutation. Check 126 non-target HTML modulo candidate
ID and 42 preview SVG byte-identical, including Gantt and both D-081 repairs. Run
focused/static/full regression, deterministic regeneration and all-three-mode
local raster inspection. Browser stays BLOCKED_NOT_EXECUTABLE under the previously
reported local URL policy; do not bypass it or claim browser/accessibility PASS.
No P-19C, package, dist, publication mirror, Git or Release action.
