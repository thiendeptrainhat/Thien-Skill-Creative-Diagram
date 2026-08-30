# P-19B review-25 — global connector policy

Authority: D-105. Status: owner review pending.

## Rule

- One connector on a node edge attaches at the exact edge midpoint.
- Two or more connectors on the same edge use positions `i / (n + 1)`, giving equal outer margins and equal inter-port intervals.
- A single straight segment is the default route.
- A 90-degree route is permitted only when the straight segment would cross a node, boundary, label, or create an ambiguous reading order. The default 90-degree treatment remains rounded under the inherited P-18 connector grammar; every exception must carry a machine-readable reason.

## Review-25 proof

The detailed UML specimen is the exact geometry proof. `BillingService → PaymentOption` is a centered horizontal line. The two realization connectors attach to the interface bottom edge at `x=1040` and `x=1400`, producing equal `360`-unit left margin, interval, and right margin. Four of five semantic relations are straight. The lower association is the sole rounded-orthogonal exception because it must pass below the domain cards.

All 90 P-19 SVG roots declare `data-connector-policy="D-105-centered-even-straight-first"` and `data-route-priority="straight-first"`. This turns the rule into the mandatory renderer contract for every existing and future P-19 diagram; a detailed renderer must additionally serialize any orthogonal exception reason.

The supplied screenshot is only a structural rubric. No text, coordinate, CSS, SVG, template, or asset was copied.

## Boundary

Review-24 is preserved byte-bound before mutation. P-18, P-17, P-19A, package, `dist`, publication mirror, Git and Release remain untouched. P-19C and G-04 remain unauthorized/not evaluated.
