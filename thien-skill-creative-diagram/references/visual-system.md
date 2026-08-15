# Original visual system and pilot boundary

Read this reference only after semantic validation and before a supported pilot render. Exact token values live in `visual-system.json`; this file owns behavior and usage rules.

## Design contract

- **Outcome:** create a neutral, professional diagram whose supplied structure, quantities and handoffs can be understood quickly by a mixed audience.
- **Single job:** reveal the primary relationship without losing traceability to exact labels, values, owners or steps.
- **Visual thesis:** calm editorial clarity, using disciplined whitespace and one restrained accent while keeping semantic evidence visually explicit.
- **Creativity:** distinctive, not expressive; operational truth and readability stay ahead of novelty.
- **Signature element:** a narrow signal rail on semantic cards plus compact handoff badges. The rail reinforces role, and the label/shape remains sufficient without color.
- **Inputs:** validated common IR, one selected type grammar, approved dials and local capability facts. Reference images remain QA data only.
- **Rights:** use only original vectors, shapes, code and fixtures. Do not copy or trace any upstream or benchmark expression.
- **Open decisions:** the owner must approve or reject the rendered golden direction; no visual candidate is self-approved.

## System rules

- Use the exact semantic tokens in `visual-system.json`; do not scatter raw presentation colors through render code.
- Keep the system font stack local and preserve Vietnamese glyphs. Never fetch a font.
- Use the 8-unit rhythm with 4-unit optical adjustments, at least 32 px safe area and the approved preset text minima.
- Apply one of `neutral-light`, `neutral-dark` or `editorial`. Editorial adds context composition but cannot change diagram semantics.
- Encode state or role with at least two channels from label, shape, border, pattern and color.
- Use direct text or orthogonal routes for relationship diagrams. Charts use scale-bound marks and never inherit connector rules.
- Prefer a larger canvas or a split before reducing material text. Ellipsis is forbidden for material labels.

## Semantic shape vocabulary

- **system/service/activity:** rounded card with a left signal rail and text role label;
- **money/check:** ticket form with two side notches and a double baseline;
- **document:** sheet form with a folded corner;
- **listing:** ruled sheet form whose line marks are decorative and hidden from accessibility APIs;
- **stored file:** folder form with a visible tab;
- **boundary/group:** labeled enclosure with border and background contrast, never color alone;
- **chart series:** position and length on a shared scale, plus direct legend and alternating solid/hatch treatment.

The vocabulary is original to this project. These are abstract geometric primitives, not borrowed assets.

## Connector and layout rules

- Bind every route to declared source and target bounds.
- Maintain the approved clearance from unrelated nodes and text; route through explicit channels when a direct dogleg is blocked.
- Render crossings only after alternatives fail and never as a junction.
- Keep arrowheads outside labels and inside the route endpoint.
- Derive peer positions from semantic order, lane membership, graph layer or chart domain rather than specimen-specific coordinates.
- Run bounds, overlap, endpoint and unrelated-node intersection checks before serializing SVG.

## Pilot support boundary

P-06 supports only these visual pilots:

1. multi-connector Architecture using the secure-route semantic pattern;
2. grouped Bar chart using exact synthetic data disclosed as synthetic;
3. grouped Vietnamese Swimlane for `REF-SWIMLANE-CASH-RECEIPTS-001` semantics.

This is not full 27-type visual coverage. Carrier parsing, full renderer/export behavior, motion and P-07/P-08 capabilities remain unavailable.

## Accessibility and output

- Give each standalone SVG a unique title and description; keep DOM order aligned with narrative order.
- Include exact chart values and units in an HTML data table and SVG description.
- Keep error, deny and permission semantics labeled and patterned; never rely on hue alone.
- HTML pilots are self-contained and contain the exact validated SVG. SVG is diagram-only.
- Print and no-script views show the complete static state.
- Contrast calculations are necessary checks, not a WCAG conformance claim.

## Verification matrix

- all three modes on every pilot;
- bounds, node overlap, connector endpoints and unrelated-node crossings;
- minimum text size, Vietnamese text retention and unique SVG IDs;
- self-contained HTML/SVG with no external URL, script or font;
- exact bar values, scale and zero baseline plus accessible table;
- reference benchmark ownership headers, six lanes, semantic shapes, numbered handoffs and legend;
- full-resolution visual inspection of rendered candidates.
