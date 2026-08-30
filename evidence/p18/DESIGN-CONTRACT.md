# P-18R design contract — visual vNext replacement pilot

**Authority:** D-047, D-049, D-050  
**Exact semantic/data matrix:** `evidence/p16/PILOT-GALLERY-CONTRACT.md`  
**Visual acceptance source:** `evidence/p18/VISUAL-CRAFT-RUBRIC.md`  
**Route:** create → static/executive technical artifact → render → inspect → score → revise → verify  
**Maturity:** remediation candidate; QA-only; not package/runtime/golden output

## Outcome

Replace the superseded first candidate with exactly 36 original, standalone HTML specimens: the locked 12 families in `neutral-light`, `neutral-dark` and `editorial`. Each specimen must read as a purpose-built diagram rather than a generic card layout, retain exact source semantics and data, and remain directly inspectable without a build or network resource.

The replacement is eligible for owner review only after P-18R0→P-18R3 completes. File creation, automated checks and internal scoring do not approve `G-03@1.5.0` and do not authorize P-19.

## Architecture

```text
locked semantic IR
  → visual intent and focal claim
  → family-specific grammar
  → measured text and reserved labels
  → layout / anchor / route plan
  → original scene primitives
  → approved mode skin
  → inline SVG artboard
  → external HTML title + evidence ledger
  → technical and visual-craft QA
```

The SVG contains the semantic field and its type legend only. The visible case title, reading instruction, exact ledger and provenance disclosure live in HTML outside the SVG. Accessible SVG `<title>`/`<desc>` remain metadata and are not duplicate visible headings.

## Fixed scope and exclusions

- Preserve the exact 12-case data, assertions and 12×3 count approved at D-047.
- Keep output under `evidence/p18/`; anchor proof files are non-counted and live outside `gallery/`.
- No package, `dist/`, publication mirror, commit, push, tag, Release or P-19 work.
- No JavaScript, external fonts, CDN, build prerequisite, absolute machine path or hidden dependency in a specimen.
- No upstream code, prose, CSS, SVG, template, gallery asset, trace or pixel target.

## Artboard profiles

Three profile contracts share one canonical 1440×900 coordinate space so geometry remains byte-deterministic and mode-comparable:

- `network-field`: topology, owned process and runtime placement; emphasizes zones, anchors and directed routes.
- `quantitative-field`: area, band, coordinate and comparative encodings; emphasizes calibrated plot area and direct value labels.
- `narrative-field`: journey and causal analysis; emphasizes sequence/spine, focal outcome and interpretive legend.

Profile is a composition contract, not a generic template. Every family keeps a unique silhouette and may define its own internal grid.

## Visual thesis

**Quiet technical editorial:** generous usable field, exact geometry, one declared focal path or outcome, strong type hierarchy, low decoration and a compact semantic legend. The viewer should identify the diagram family and takeaway before reading the evidence ledger.

- `neutral-light` is the anchor proof mode.
- `neutral-dark` derives the same geometry with verified opaque contrast.
- `editorial` retains the same semantic positions but may use warmer paper, a serif display role and a more publication-like outer title treatment.
- System sans/mono/serif stacks only; no font download or font bundling in P-18R.
- Flat surfaces and deliberate strokes; drop shadows are retired.
- One primary accent/focal path; secondary colors appear only when data series or state meaning requires them.

## Typography

At canonical render:

- display title in HTML: 40–48px;
- visible node/stage title: 20–24px;
- material body/label text: at least 16px;
- mono metadata, values and axis ticks: 14–16px;
- no ellipsis, text compression or character-count-only wrapping for material text.

The renderer uses deterministic width estimates to reserve line boxes. Browser QA measures actual rendered bounds and rejects clipping/overlap.

## Geometry and routing

- Semantic field plus type legend uses at least 75% of artboard height, counting intentional whitespace inside the field.
- Connectors terminate at declared ports or node boundaries; they do not run through unrelated nodes.
- Labels reserve an opaque/near-opaque mask and at least 8px connector clearance.
- Unavoidable crossings use a visible bridge/hop; route coincidence is not treated as a crossing.
- Orthogonal routes use stable bend radii and consistent arrowheads.
- Quantitative encodings retain the approved numeric tolerances in the P-16 contract.

## Original scene primitives

The shared foundation may provide independently authored cards, zones, documents, files, service/host glyphs, database cylinders, ports, label plates, orthogonal routes, crossing bridges, calibrated axes, dots/paper fields and semantic legends. A family must not collapse into the same node-and-arrow silhouette merely because it reuses a primitive.

## HTML evidence wrapper

The wrapper presents one visible title and reading instruction, then the SVG artboard. Exact semantic/data tables and provenance appear below in a separate evidence section and are excluded from the artboard/contact-sheet crop. The wrapper remains printable, keyboard reachable and responsive; narrow screens scale the complete artboard rather than reordering semantic marks.

## Verification sequence

1. P-18R1: render and inspect Architecture, Swimlane and Sankey in `neutral-light`; verify foundation, anchors, routes, type legends and title separation.
2. Derive the two remaining modes without geometry drift that would change meaning.
3. P-18R2: regenerate the exact 36 files, index, provenance and contact sheets.
4. P-18R3: rerun semantic, quantitative, accessibility, geometry, security, standalone, browser, determinism and full regression checks.
5. Score the replacement with `VISUAL-CRAFT-RUBRIC.md`, run blind silhouette and five-second takeaway reviews, then freeze the exact manifest.
6. Present the frozen replacement to the owner. Only the owner may approve it for `G-03@1.5.0`.

## Design-intelligence disposition

The offline tool suggested a low-confidence SaaS/Bento route, web fonts, pink accent and motion. Those suggestions were rejected because this is a static technical artifact and because they conflict with self-contained output, restrained semantic signaling and the approved three-mode contract. Accepted abstract guidance is Swiss/minimal composition, generous whitespace, geometric hierarchy and explicit contrast verification; no accessibility conformance claim is made from labels alone.
