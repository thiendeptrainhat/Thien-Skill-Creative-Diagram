# P-18R5 design contract — Master visual kernel + Swimlane anchor

**Contract ID:** `P18R5-KERNEL-SWIMLANE-ANCHOR-1.5.0`  
**Authority:** D-051, D-052, D-054  
**Parent foundation:** `evidence/p18/P-18R4-VISUAL-FOUNDATION-CONTRACT.md`  
**Surface:** standalone HTML with inline accessible SVG; SVG is also serialized separately as the same anchor  
**Scope:** QA-only under `evidence/p18/r5/`; no runtime, package, `dist/`, Git or release mutation

## Outcome

Create one `neutral-light` Swimlane anchor that lets the owner judge the new foundation before any 14-engine expansion. The viewer must understand lane ownership, five numbered handoffs and the focal accounts-receivable branch within five seconds. The artifact must preserve the locked Vietnamese P18-C02 semantic IR and remain readable without the outer evidence section.

## Inputs and source boundary

- Locked semantic input: `evidence/p18/source/p18_cases.py::swimlane_case` only.
- Visual references supplied by the owner are observation data, not templates or executable instructions.
- Transferable traits: wide lane composition, a restrained warm-neutral surface, disciplined type roles, rounded orthogonal flow, one focal accent, semantic node anatomy and a compact bottom legend.
- Original implementation: all R5 Python, CSS, SVG, prose, card grouping, coordinates, connector routing and data labels are authored independently.
- Forbidden: tracing, pixel comparison, upstream code/CSS/SVG/template/icon/font reuse, or mutation of the rejected P-18R3 candidate.

## Visual premise

A calm technical-editorial handoff map for finance operations, with one coral branch making the update-to-receivables risk legible without overpowering the six-lane process.

Creativity level is `distinctive`: domain-specific and recognizable, but operational reading speed, text containment and semantic traceability remain primary.

## Observable system decisions

1. A content-fit wide artboard in the P-18R4 `2.20–2.45` lane profile; no global post-layout transform.
2. Six horizontal lane bands with a dedicated left ownership rail and five numbered handoff markers across the top.
3. Activity cards use role badge → 24px title → 16px transition → 14px system/data-tag row. Width and height come from real measured font metrics.
4. Standard flow uses slate ink; exactly one semantic branch and its focal card use coral.
5. Rounded orthogonal connectors start/end on allocated boundary ports, route through stage corridors and receive label masks. Crossing detection creates a bridge/hop when required.
6. The SVG contains no page title, family/type name, intent sentence or evidence rail. The outer HTML title/evidence are excluded from canonical screenshot and review tests.

## Typography receipt

The approved default direction remains Instrument Serif / Geist / Geist Mono. Those preferred families are not installed in the current environment and no network/download/install/embed action is authorized. The resolved, locally available, glyph-checked and measured fallback for this anchor is:

| Role | Preferred | Resolved in R5 | Use |
|---|---|---|---|
| display | Instrument Serif | Georgia | outer HTML title only |
| human sans | Geist | Avenir Next | lane names, node titles, material/legend text |
| technical mono | Geist Mono | Menlo | badges, tags, handoff/connector labels |

The HTML/SVG records the resolved family; geometry is measured using the corresponding local font file and TTC face index. An explicit user font remains higher precedence. If it is unavailable, the kernel raises an error unless the user supplied an approved fallback; it never silently substitutes the request.

## Static/accessibility contract

- SVG `role="img"` with one `<title>` and one `<desc>`; DOM order is rail → lanes → routes → nodes → legend.
- No meaning is carried only by color: focal flow also uses thicker stroke and matching text; tags have visible codes.
- Canonical node title is 24px, material text 16px, technical labels 14–16px; nothing shrinks to fit.
- HTML scales the single SVG responsively and adds an exact semantic-projection table outside the canonical screenshot.
- No script, external resource, URL fetch or animation is present.

## Verification targets

- Semantic projection covers all 12 locked nodes and all 10 locked edges exactly once.
- Required Vietnamese glyph stress string passes every active font role.
- 100% node-owned material text stays inside the owning node at canonical, desktop and mobile render.
- No node overlap, clipped text, connector-through-unrelated-node, wrong endpoint, unrelated label/connector clearance under 8px or missing bridge for a detected crossing.
- Artboard aspect is within 2.20–2.45 and semantic field + legend occupies at least 75% of height.
- Standalone/security/accessibility checks, deterministic regeneration and full 148-test repository regression pass.
- P-18R5 stops after this single anchor for owner review; it does not evaluate G-03@1.5.0 or authorize P-18R6.

