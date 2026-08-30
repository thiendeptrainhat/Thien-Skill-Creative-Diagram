# P-18 / P-19 — approved originals and additional diagrams

This directory is a QA-only viewing aid, not a phase transition, owner approval,
golden, runtime change or P-19C execution. Current scope follows
D-084/D-085/D-086/D-087/D-088/D-089/D-090/D-091/D-092/D-093.

## Design contract

- Owner's job: see all retained diagrams on one page without competing P-19
  versions of the 14 canonical types already approved in P-18.
- Preserve: exact P-18R6 review-17 SVG bytes and all non-target P-19B review-12
  artwork, typography, colors, text, geometry and paint order. Review-13 changes
  only it-current-state relative to archived review-12; all retained detailed diagrams
  remain intact.
- Display: 14 approved P-18 neutral-light originals + 87 P-19 specimens
  (25 canonical types + four capabilities × three modes) = **101 diagrams**.
  No duplicate canonical type exists across the phases.
- Keep all four capabilities, including Bubble whose canonical parent is
  scatter-plot. Do not infer deletion of a capability from its parent type.
- Group by 14 layout engines. Engines without additional P-19 types show the
  approved P-18 once, at full available width. Other engines show the P-18
  reference alongside additional P-19 types, clearly distinguished.
- Keep the warm-paper viewer, Georgia/Avenir Next/Menlo stack, fluid layout,
  native enlargement checkbox, focus/skip navigation and source links.
- No new font, network, dependency, asset, motion or alternate mode for P-18.
  P-19 remains pending owner review. Grouping by engine does not mean identical
  scenarios or equivalent data.

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
101 unique previews, complete P-19 modes, inert SVG, original links and source
preservation. The comparison manifest contains every source/preview hash.
`--check` is read-only and proves deterministic bytes.

Browser verification is **blocked / not executable** due to the earlier local-file
URL denial. No HTTP server, alternate browser or bypass is used. Responsive,
keyboard, image loading and computed fonts remain unverified in-browser.

Historical candidates and withdrawn duplicates are intentionally excluded.
Exact review-04 is archived in P-19 history; withdrawn files and the interrupted
Sankey adoption draft are recoverable under `../withdrawn/review05-duplicates/`.
P-18 originals, frozen P-19A, packages, publication mirror and Release remain
unchanged. The UI/UX skill guides preservation, clear status and honest QA.
