# Portable output and static-first motion

Read this reference when delivering HTML, SVG, PNG, HTML+PNG, print behavior, or motion.

## Output workflow

1. Validate the normalized request, common IR, and selected type grammar.
2. Use `scripts/output_pipeline.py::export_artifacts`; it renders a complete static frame through the canonical renderer before adding any HTML or motion layer.
3. Return the artifact ledger with requested/delivered formats, hashes, dials, warnings, renderer/rasterizer capability, output/motion capability IDs, font policy, and validation dispositions.
4. Write files only through `write_bundle` with one explicit relative target per delivered artifact. It rejects traversal, absolute targets, extension mismatch, missing targets, and implicit overwrite.

HTML is self-contained: one inline SVG, inline project-authored CSS, and optional project-authored motion controller. It has no required network resource. SVG is standalone and script-free. Quantitative charts and the permission matrix include an exact text/table alternative. Every size preset keeps the same validated IR and viewBox; the exported width/height and print `@page` rule express the selected surface.

## PNG boundary

PNG is conditional. The pipeline may use only a preinstalled, detected adapter (`cairosvg`, `rsvg-convert`, or ImageMagick) or an explicitly registered equivalent. It never downloads or installs a renderer. PNG must have the expected signature and exact preset dimensions. Failure or absence returns:

- SVG for a PNG request;
- HTML for an HTML+PNG request;
- a precise warning and `png = unavailable-or-not-requested` in the ledger.

Do not describe an injected test adapter as real environment rasterizer evidence.

## Motion contract

- `none`: script-free complete static default.
- `reveal`: one deterministic emphasis sequence with replay/pause controls.
- `step`: deterministic current/past/future emphasis with previous, next, replay, pause/resume, Arrow Left/Right, Home, and End controls.
- `loop`: a decorative token only; all semantic content remains visible.

All modes start from the same complete static SVG. JavaScript adds progressive enhancement only. No-JS and a motion-runtime failure leave complete static HTML. `prefers-reduced-motion` and print disable animation, transition, dimming, and transforms. SVG and PNG are complete static frames.

The 12 motion inventory capabilities map to these four public modes through `scripts/motion_catalog.py`. Motion selectors can specialize paths, items, queues, fields, policy states, containment, and chronology only when the corresponding validated IR structure exists.

## Limitations and verification

- System/local fonts only; never fetch a font. Disclose a known substitution and revalidate wrapping in the target renderer.
- Browser behavior is not passed by static source inspection. Run representative live browser checks when a compatible browser is available; otherwise record `blocked / not executable` and retain DOM/security/unit results.
- P-08 does not create automated golden infrastructure, mutation harnesses, or benchmark forward tests; those remain P-11/P-12.
