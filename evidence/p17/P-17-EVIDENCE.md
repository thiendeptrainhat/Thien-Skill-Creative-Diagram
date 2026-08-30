# P-17 — Semantic expansion to 39 types

**Target:** `v1.5.0`  
**Authority:** D-048, 2026-08-23  
**Result:** `PASS`  
**Boundary:** semantic source only; P-18/P-19, gallery, package, Git and release work remain unauthorized

## Outcome

P-17 expands the canonical semantic contract from 27 to 39 types and adds four capability variants under their approved parents:

- `CAP-V17` Dumbbell → `bar-chart`;
- `CAP-V18` Slopegraph → `line-chart`;
- `CAP-V19` Ridgeline → `line-chart`;
- `CAP-V20` Bubble → `scatter-plot`.

The canonical request and semantic-IR schemas, router, taxonomy, grammar registry, validators, fixtures, references, capability map and tests now express the exact G-02@1.5.0 contract. The inventory is 39 canonical types, 20 variants and 111 total capabilities. Each of the 12 new types and four new variants has an original semantic fixture, stable positive/boundary/hard/accessibility test mapping and an explicit render deferral.

No visual substitution is permitted before a visual phase: `full_renderer.py` fails closed with `type-visual-not-implemented` or `variant-visual-not-implemented` for the new semantics. This keeps P-17 from presenting a legacy generic renderer as evidence of P-18/P-19 visual completeness.

## Integrity and compatibility

Quantitative contracts use finite-number checks, Decimal-backed reconciliation where totals matter, the owner-approved tolerance `max(0.5 CSS px equivalent, |E| × 0.01)` where applicable, and Unicode NFC plus outer trimming for case-sensitive unit equality without implicit conversion. The P-17 tests cover polar radius, treemap hierarchy and totals, Sankey conservation, Wardley coordinates, journey order, database index scope, Dumbbell shared scale, Slopegraph two-state consistency, Ridgeline shared distribution/amplitude and Bubble non-negative size.

Historical v1.0 behavior remains explicit: 27 legacy type references and `specimen-map.json` are byte-identical to the sanitized v1.0.0 publication mirror. Historical P-07/P-08/P-11 evidence generators are pinned to the legacy 27 types and first 16 variants, while current semantic QA evaluates all 39 types and 20 variants. The owner-approved P-06 golden directory, legal files, brand asset and all four `dist/` files are unchanged.

## Verification

- Full regression: 148/148 `PASS`.
- P-17-focused suite: 20/20 `PASS`.
- Canonical reference drift check: `PASS`.
- Repository QA audit: `PASS`; 39 types, 111 capabilities, 96 links, 11 JSON files and 27 contrast pairs.
- Static parsing: 33 Python files and 11 JSON files `PASS`.
- Exact source delta: 39 files, hash-bound in `P-17-SOURCE-MANIFEST.json`.
- Canonical/runtime HTML count: 0; `evidence/p17/` HTML count: 0.
- `dist/` aggregate: unchanged at `188526fdf60b53183723bb231a6940896a42cf90db5df71094eebc66ac45c065`.
- Exact hash collisions with the capability-bearing upstream files recorded in P-16: 0. This is supporting evidence only; the controlling description remains **clean-room-oriented independent reimplementation**.

The skill-creator `quick_validate.py` command was attempted but could not start because the environment lacks PyYAML (`ModuleNotFoundError: yaml`). No dependency was installed and this command is not reported as passed. The canonical repository QA audit, link checks, JSON parsing, Python AST parsing and full regression provide the recorded compensating evidence.

Machine-readable detail is in `P-17-VERIFICATION.json`; implementation provenance is in `PROVENANCE-RECEIPTS.json`; exact source hashes are in `P-17-SOURCE-MANIFEST.json`.

## Phase boundary

P-17 contributes semantic-source readiness to `G-04@1.5.0`; it does not evaluate or pass that gate. P-18 remains `not-started` and unauthorized. No gallery HTML, build, package refresh, `dist` edit, commit, push, tag, Release change or publication action occurred.
