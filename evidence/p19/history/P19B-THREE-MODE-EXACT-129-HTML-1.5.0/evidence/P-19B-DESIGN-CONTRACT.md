# P-19B design contract — three-mode exact 129 HTML

**Candidate:** `P19B-THREE-MODE-EXACT-129-HTML-1.5.0`  
**Authority:** D-079  
**Surface:** QA-only standalone web evidence under `evidence/p19/gallery/`  
**Boundary:** P-19B only; no P-19C freeze/owner review, G-04 evaluation, package, `dist`, publication, Git or Release mutation

## Outcome

Create exactly 129 standalone HTML specimens from the passed P-19A adapter layer: 39 canonical types × three modes = 117, plus four capabilities × three modes = 12. A separate `index.html` is the contact sheet and does not count as a specimen.

The single job is to let a reviewer navigate and compare every approved type/capability and mode without a build step or network dependency.

## Inputs and preserved decisions

- Preserve exact P-18R5 review-04 and exact P-18R6 review-17 byte-for-byte.
- Consume validated semantic IR through `visual_adapters_v15.py`; do not bypass semantic validation.
- Preserve the exact 14-engine map, 43 unique silhouette declarations and three approved modes.
- Preserve `visual-system.json` as the semantic token source.
- Use original fixtures, prose, layout, CSS and SVG only; no upstream specimen or asset is copied, traced or translated.

## Visual thesis

Calm technical evidence with one semantic accent: every specimen should reveal its diagram family through silhouette first, while typography and metadata remain restrained and comparable across modes.

The signature element is a large content-fit diagram field followed by a compact three-cell evidence rail and an accessible disclosure containing the semantic-ID table.

## System

- `neutral-light`, `neutral-dark` and `editorial` derive from semantic tokens only.
- Geometry and source IR remain byte-equivalent across the three mode derivations after mode-specific IDs are normalized.
- System fonts only; no font download, embedding or silent network fallback.
- Canonical SVG viewBox is `0 0 1200 760`; no global post-layout transform.
- Complex diagrams use a contained horizontal scroll region on narrow viewports rather than shrinking material text below the inherited minimum.
- Static is the only state; no executable script and no information-bearing motion.

## Accessibility and security

- Vietnamese `lang`, useful HTML title, heading hierarchy and named regions.
- Every inline SVG has one programmatic title and description with document-unique IDs.
- Alternative semantic-ID table is available through a native `details`/`summary` control.
- Focus indicator, print rules and `prefers-reduced-motion` fallback are explicit.
- No external resource, URL, event handler, executable script, font request or network runtime.
- Type/capability, parent, mode, engine, silhouette, fixture and check disposition are machine-readable on the root element and in inert hidden metadata.

## Verification matrix

- Focused renderer unit tests for exact counts, explicit bindings, metadata, security, accessibility anatomy, mode invariance and fail-closed behavior.
- Static verification of all 129 specimens, all hashes, contact-sheet links/cards, manifest integrity and non-package boundary.
- Browser check of all 129 specimens at desktop plus 14 engines × three modes at mobile, contact-sheet structure, console, focus and reduced-motion rule.
- Full typography/glyph/containment, quantitative, pairwise, masked review, freeze and owner review remain P-19C.

