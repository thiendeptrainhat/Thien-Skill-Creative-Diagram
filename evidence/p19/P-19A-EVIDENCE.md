# P-19A evidence — 39+4 visual adapters

**Candidate:** `P19A-THIRTY-NINE-PLUS-FOUR-ADAPTERS-1.5.0`  
**Authority:** D-078, 2026-08-27  
**Result:** `PASS`  
**Boundary:** P-19A only; no P-19B/P-19C, HTML/SVG gallery, package, `dist/`, publication mirror, Git, tag, or Release mutation

## Outcome

P-19A adds one canonical adapter source, `scripts/visual_adapters_v15.py`, between validated P-17 semantic IR and the future P-19B renderer. The layer covers exactly 39 canonical types and the four approved capability variants, maps them to the exact fourteen P-18R4 engines, and creates deterministic engine-specific layout plans.

Each adapter declares a distinct silhouette, semantic focus, primary mark, connector policy, content-fit artboard profile, and accessible alternative. Engine projectors preserve type-specific structures such as trust boundaries, pipeline roles, placement, cycles/fan-in, guards, lanes/messages, temporal facts, work/journey/story metadata, hierarchy roots, containment, class/table members, spatial axes, exact quantitative values, Sankey flow, Fishbone cause groups, and Flywheel cycles.

The four quantitative capability projections are executable rather than documentary:

- Dumbbell produces exact paired endpoints and signed gap per category.
- Slopegraph produces two-state endpoints and signed delta per series.
- Ridgeline produces the validated shared-domain/global-amplitude normalized profile.
- Bubble preserves exact x/y and area-bearing magnitude; it does not reinterpret the value as radius.

The public skill workflow now routes validated 39+4 IR through the P-19A adapter layer while keeping `full_renderer.py` explicitly historical for the original 27 types. P-19A does not weaken the existing fail-closed render boundary for the 12 additions or four capabilities.

## Verification

- Focused P-19A tests: `14/14 PASS`.
- Full canonical regression: `162/162 PASS` (the previous 148 tests plus 14 P-19A tests).
- Registry: `39/39` canonical adapters, `4/4` capability adapters, `14/14` layout engines.
- Silhouette declarations: `43/43` unique; zero `generic`, `unknown`, or generic-card fallback.
- Exact P-18R4 engine mapping comparison: `PASS`.
- Deterministic reference regeneration: `PASS`; before/after SHA-256 identical.
- Python AST parsing: `3/3 PASS` for new source/test/builder at the focused checkpoint; final verification records the complete P-19A source set.
- JSON parsing and generated-reference drift: `PASS`.
- P-19A emitted HTML/SVG/CSS count: `0`.
- Browser verification: `not run (out of scope)` because P-19A emits no executable web artifact; this is not a browser PASS.
- Exact P-18R5 review-04 manifest remains SHA-256 `7725a03c82c370f6d9bb984b0d6e50c585efb07529a47f2c3dfad45877c1cca8`.
- Exact P-18R6 review-17 manifest remains SHA-256 `7925c1ab0515a59057851bb3888ff4d9974e5f5701b873b1f11468a5fd64a03a`.
- All four `dist/` artifact hashes remain the locked v1.0.0 values.

Machine-readable results are in `P-19A-VERIFICATION.json`; exact adapter-plan hashes are in `P-19A-PLAN-MANIFEST.json`; source hashes are in `P-19A-SOURCE-MANIFEST.json`; provenance is in `P-19A-PROVENANCE.json`.

## Skill-driven design decisions

The `thien-skill-ui-ux-ultra` workflow was used only at principle/process level. It led to a preserve/extend design contract, explicit per-type silhouettes, exact-value accessible alternatives, deterministic verification, and a strict distinction between adapter planning and rendered evidence. No code, prose, template, token, asset, or test was copied from that skill.

## Phase boundary

P-19 is now `in-progress` because its first subphase is complete. P-19A is `passed`; P-19B and P-19C remain `not-started` and unauthorized. No three-mode derivation, 129-file gallery, full visual QA/freeze, owner gallery review, package build, commit, push, tag, or release action occurred.

