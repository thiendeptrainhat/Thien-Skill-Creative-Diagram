# P-18 / P-19 — approved originals and additional diagrams

This directory is a P-19C QA-only viewing aid, not a package, publication,
runtime change, owner approval or gate decision. Current scope follows
D-084–D-127 and preserves the exact owner-approved P-19B review-45 artwork.

## Design contract

- Owner's job: see all retained diagrams on one page without competing P-19
  versions of the 14 canonical types already approved in P-18.
- Preserve: exact P-18R6 review-17 SVG/HTML bytes and all exact P-19B review-45
  HTML/preview bytes, typography, colors, text and geometry.
- Display: 14 approved P-18 neutral-light originals + 93 P-19 specimens
  (25 canonical types + four capabilities + two presentation variants, each
  with three modes) = **107 diagrams**.
  No duplicate canonical type exists across the phases.
- Keep all four capabilities, including display identity `dumbbell` whose internal
  ID is `CAP-V17` and canonical parent is `bar-chart`, plus `slope-graph`/`CAP-V18`/`line-chart`
  and `bubble`/`CAP-V20`/`scatter-plot`. Do not infer deletion
  of a capability from its parent type.
- Group by 14 layout engines. Engines without additional P-19 types show the
  approved P-18 once, at full available width. Other engines show the P-18
  reference alongside additional P-19 types, clearly distinguished.
- Keep the warm-paper viewer, Georgia/Avenir Next/Menlo stack, fluid layout,
  native enlargement checkbox, focus/skip navigation and source links.
- No new font, network, dependency, asset, motion or alternate mode for P-18.
  P-19B review-45 is owner-approved under D-126. Grouping by engine does not
  mean identical scenarios or equivalent data.

## Preview fidelity

P-18 images embed exact approved standalone SVG bytes. P-19 images extract the
exact inline SVG and insert the original base stylesheet. Only page-responsive,
print and reduced-motion media rules are excluded from the scaled preview;
namespace and intrinsic dimensions come from the original viewBox. No diagram
element or paint value is rewritten. SVG image boundaries isolate IDs/styles.

## Verification / limits

```sh
PYTHONDONTWRITEBYTECODE=1 python3 evidence/p19/comparison/generate_comparison.py
PYTHONDONTWRITEBYTECODE=1 python3 evidence/p19/comparison/generate_comparison.py --check
```

The generator verifies exact source pins/hashes, non-overlapping canonical sets,
107 unique previews, complete P-19 modes, inert SVG, original links and source
preservation. The comparison manifest contains every source/preview hash.
`--check` is read-only and proves deterministic bytes.

Browser verification runs through a read-only localhost server rather than a
`file://` URL. Desktop/mobile counts, image loading, responsive containment,
keyboard accessibility and representative standalone specimens are recorded in
`../P-19C-BROWSER-VERIFICATION.json`.

Historical candidates and withdrawn duplicates are intentionally excluded.
Historical candidates remain archived in P-19 history; withdrawn duplicates are
recoverable under `../withdrawn/review05-duplicates/`. P-18 originals, exact
P-19B artwork, frozen P-19A, packages, publication mirror and Release remain
unchanged. The UI/UX skill guides preservation, clear status and honest QA.
