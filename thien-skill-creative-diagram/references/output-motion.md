# Portable output and static-first motion

Read this reference when delivering HTML, SVG, PNG, HTML+PNG, print behavior, or motion.

## Output workflow

1. Normal target-v2.1 creation is an executable package path, not a hand-written Python driver. Inspect its bounded input once with `python3 /absolute/skill/scripts/output_pipeline.py --print-job-contract`, then run `python3 /absolute/skill/scripts/output_pipeline.py --job /absolute/job.json --output-dir /absolute/new-output`.
2. The job keeps material semantics explicit through two agent-authored representations. `source_assertions` is written first from minimal verbatim relation clauses and declares exact collection/member IDs plus one atomic edge assertion per endpoint pair. `relation_groups` is then materialized separately and expands `sources × targets`; both representations and `expected_counts` must agree before IR construction. The runtime reconciles those declared assertions with exact IR node IDs, edge ID/source/target/direction/kind tuples, nested/member IDs, and group/lane memberships. A mismatch exits nonzero and leaves no output directory.
3. The canonical `create_profiled_diagram` call resolves and hashes the profile before render, dispatches its exact executable layout engine, renders independently from approved sample bytes, validates semantic coverage, engine primitive, bounds, overlap, ports, route continuity/family, direction and arrows, then atomically publishes exactly `diagram.svg` and `diagram.ledger.json`. The ledger carries an exact validated `semantic_snapshot` and SHA-256; the SVG carries the same canonical JSON in `metadata[data-kind=exact-semantics]`. Only runtime provenance handles named `source_refs` are stripped.
4. Normal profiled creation fixes `format=svg`, `motion=none`, and `structural_override=none`. Do not hand-author SVG, inspect runtime source to discover the API, call the historical renderer, or silently change the requested format. Lower-level `build_profiled_plan`, `render_profiled_svg`, `export_profiled_artifacts`, and `write_bundle` are integration/test surfaces only.
5. Return the command result and ledger with hashes, dials, warnings, font policy, the complete profile binding, the exact semantic snapshot/hash, `semantic_coverage=pass`, `semantic_coverage_scope=declared-source-assertions-to-validated-ir`, `source_interpretation_attestation=agent-authored-not-independently-proven`, `profile_binding=pass`, `structural_conformance=pass`, and `geometry_validation.status=pass`. The receipt proves declared assertion→IR preservation, not independent completeness of a natural-language interpretation; a QA gate must use a separately frozen prompt oracle. Any missing or failed disposition blocks delivery.
6. Use `scripts/output_pipeline.py::export_artifacts` only for an explicitly historical P-08/P-07 operation; its output never establishes v2.1 profile conformance.

Historical HTML is self-contained: one inline SVG, inline project-authored CSS, and optional project-authored motion controller. It has no required network resource. Target-v2.1 profiled SVG is standalone and script-free; its ledger includes exact quantitative data metadata and geometry validation. Every size preset preserves the same validated IR and selected structural profile while the renderer reflows geometry for the selected canvas.

Profile and engine identity belong in machine-readable receipts, never in visible diagram text. A strict blind visual review receives only a neutral raster rendered at the frozen viewport and no filename, metadata, prompt, oracle, profile, engine, or package identity. When a capability intentionally transposes canonical axes for presentation, the SVG must expose an explicit physical-axis mapping while retaining the original semantic axis dimensions in its receipts.

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
- Distinguish profile fallback from output fallback. A missing PNG rasterizer may transparently fall back to SVG/HTML; an unsupported structural profile may not fall back to a generic or different profile.
- Browser behavior is not passed by static source inspection. Run representative live browser checks when a compatible browser is available; otherwise record `blocked / not executable` and retain DOM/security/unit results.
- P-08 does not create automated golden infrastructure, mutation harnesses, or benchmark forward tests; those remain P-11/P-12.
