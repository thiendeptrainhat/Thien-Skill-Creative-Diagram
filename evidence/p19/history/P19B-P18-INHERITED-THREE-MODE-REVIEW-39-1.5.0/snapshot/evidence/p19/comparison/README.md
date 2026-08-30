# P-18 / P-19 — approved originals and additional diagrams

This directory is a QA-only viewing aid, not a phase transition, owner approval,
golden, runtime change or P-19C execution. Current scope follows
D-084/D-085/D-086/D-087/D-088/D-089/D-090/D-091/D-092/D-093/D-094/D-095/D-096/D-097/D-098/D-099/D-100/D-101/D-102/D-103/D-104/D-105/D-106/D-107/D-108/D-109/D-110/D-111/D-112/D-113/D-114/D-115/D-116/D-117/D-118/D-119.

## Design contract

- Owner's job: see all retained diagrams on one page without competing P-19
  versions of the 14 canonical types already approved in P-18.
- Preserve: exact P-18R6 review-17 SVG bytes and all 90 non-target P-19B artworks,
  typography, colors, text and geometry. Review-39 changes only Process paint weight
  under D-119 while preserving all D-118 connector contacts/routes; all retained
  diagrams remain intact.
- Display: 14 approved P-18 neutral-light originals + 93 P-19 specimens
  (25 canonical types + four capabilities + two presentation variants, each
  with three modes) = **107 diagrams**.
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
107 unique previews, complete P-19 modes, inert SVG, original links and source
preservation. The comparison manifest contains every source/preview hash.
`--check` is read-only and proves deterministic bytes.

Browser verification is **blocked by URL policy** due to the local-file
URL denial. No alternate browser or bypass is used. Responsive,
keyboard, image loading and computed fonts remain unverified in-browser.

Historical candidates and withdrawn duplicates are intentionally excluded.
Exact review-04 is archived in P-19 history; withdrawn files and the interrupted
Sankey adoption draft are recoverable under `../withdrawn/review05-duplicates/`.
P-18 originals, frozen P-19A, packages, publication mirror and Release remain
unchanged. The UI/UX skill guides preservation, clear status and honest QA.
