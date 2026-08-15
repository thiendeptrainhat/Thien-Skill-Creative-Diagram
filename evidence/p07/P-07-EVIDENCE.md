# P-07 Evidence — Full visual coverage & safe input/import

**Phase:** P-07  
**Date:** 2026-08-15  
**Result:** PASS  
**Gate contribution:** G-04 import/security section; G-04 remains `NOT-EVALUATED` because P-08, P-11, and P-12 have not run.

## Authorized boundary

Only P-07 was executed. P-08 was not started. This change contains no production exporter, rasterizer, motion system, logo/license work, ZIP/package build, Git initialization, commit, push, or release action. The implementation is a clean-room-oriented independent reimplementation: it uses the locked abstract capability inventory and approved visual principles, without copying upstream code, prose, CSS, template, script, specimen, or asset.

## Deliverables

- `thien-skill-creative-diagram/scripts/full_renderer.py` — deterministic, self-contained static SVG visual coverage for all 27 canonical types and three approved modes; explicitly not the P-08 production exporter or motion layer.
- `thien-skill-creative-diagram/scripts/safe_import.py` — bounded, inert parsers for natural language, pasted tables, CSV, JSON, draw.io carriers/multi-page data, and the four approved Mermaid subsets; explicit source-backed mapping and fidelity reconciliation.
- `thien-skill-creative-diagram/scripts/p07_coverage.py` — single P-07 disposition source over the locked 95-capability P-05 inventory.
- `thien-skill-creative-diagram/references/import-security.md` and `references/visual-coverage.md` — progressive-disclosure runtime guidance.
- `thien-skill-creative-diagram/references/visual-coverage-map.json` — exact 95-capability visual/import/static-fallback map with the P-08 boundary stated per deferred class.
- `thien-skill-creative-diagram/scripts/tests/test_safe_import.py`, `test_full_renderer.py`, and `test_p07_coverage.py` — parser, adversarial, fidelity, render, inventory, and phase-boundary tests.
- `evidence/p07/visual-smoke-manifest.json` — 81 type×mode runs, 16 variant runs, seven pattern runs, eight specimen groups totaling 97, deterministic hashes, and the P-08 boundary.
- `evidence/p07/import-test-manifest.json` — supported carriers, Mermaid subsets, and enforced safety properties.
- `evidence/p07/contact-sheet.html` and `qa-svg/` — QA-only local review artifacts; excluded from any future release package by project boundary.
- `evidence/p07/artifact-hashes.json` — SHA-256 for all generated P-07 QA evidence artifacts except itself.

## Verification results

1. Full unit/regression suite: `python3 -m unittest discover -s thien-skill-creative-diagram/scripts/tests -p 'test_*.py'` → **75 tests, PASS**.
2. Visual inventory: **27/27 canonical types × 3 modes = 81/81 deterministic static runs, PASS**; 81 unique hashes.
3. Variant inventory: **16/16, PASS**. `CAP-V15` is deliberately a text-equivalent fallback; its symbol asset remains P-09.
4. Semantic patterns: **7/7 transformed and rendered under their existing canonical parent, PASS**.
5. Specimen inventory: all eight locked groups reconcile to **97/97**; no approved P-05 inventory was rewritten.
6. Capability inventory: **95/95** entries have a P-07 visual/import/static-fallback disposition. Output and motion classes explicitly state that production behavior remains deferred to P-08.
7. Carrier coverage: natural language, pasted table, CSV, JSON, draw.io XML/compressed page/PNG embedded model/SVG embedded model, page selection, Mermaid text, and Markdown Mermaid fences are covered.
8. Safety/adversarial coverage: prompt-like cells remain data; formulas remain literal; duplicate/non-finite/deep JSON, ambiguous CSV, executable Mermaid, DTD/entity/XInclude, malformed/missing embedded models, decompression/resource abuse, absolute targets, and path traversal fail explicitly with zero side effect.
9. Fidelity: every source item must reconcile exactly once as kept, merged, dropped, or source rot; `invented_count` must equal zero before IR construction succeeds.
10. SVG checks: XML parse, unique IDs, canvas bounds, non-overlap, material-label presence, text escaping, and absence of script/external resources pass.
11. Generated JSON files parse successfully; generated evidence counts are 81 type-mode, 16 variant, seven pattern, 97 specimen, and 95 capability entries.
12. The skill-creator `quick_validate.py` helper could not start because its environment lacks the optional `PyYAML` module; no package was installed. Equivalent frontmatter validation with Ruby's standard YAML parser passed and confirmed exactly the `name`/`description` keys and canonical skill name. Semantic-reference drift validation also passed.

## Visual QA note

The local browser refused the `file://` contact sheet under its URL security policy. Per the browser-control rules, no alternate browser, localhost workaround, or raw browser command was used. Automated SVG structural, geometry, label-preservation, contrast-system, and deterministic-hash checks all passed. The QA-only contact sheet and representative SVGs remain available for owner/manual inspection. This tool limitation does not weaken the explicit P-07 exit criteria, which require visual smoke evidence rather than a browser gate.

## Key hashes at phase close

- `safe_import.py`: `bfd6143365c69661fbf739b82e1b2a22776aa2f5deb0dd97c2403bdfa1c8dc4d`
- `full_renderer.py`: `781bc121cb697da7f69c2913289947e462edc920a408bf368c704bb5cd123e93`
- `p07_coverage.py`: `3a116600a3bb86a7123a358443d2e261168805f0d0810c6ab2b070a3949ea0f0`
- `visual-coverage-map.json`: `5de56ac4275029015bbec4e9adde67184fdade1416ff56035ca14b2973176abe`
- `visual-smoke-manifest.json`: `e753f4767169febf5dbd7f71735551877185d65013230e4c318c9b90d326bc41`
- `import-test-manifest.json`: `e27c247ba06b50d80ef64524a80a14b59a07662026fb94a47ed2a537eada7cd5`
- `contact-sheet.html`: `bf19e3fefeb1c0364b9158fbc44acdfee50b50140d9402fbe0ebf307ace8e979`
- `artifact-hashes.json`: `c9f5801a41d9363d82767238d0bb93664e9a1cd1124ef6f104a3675bd4a5bf96`

P-07 satisfies its phase verification: complete visual smoke coverage, bounded safe import, zero side effects, zero invented content, and explicit accounting for semantic loss. P-08 remains `not-started` and unauthorized.
