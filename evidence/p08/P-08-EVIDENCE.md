# P-08 Evidence — Renderer, export & motion

**Phase:** P-08  
**Date:** 2026-08-15  
**Result:** PASS  
**Gate contribution:** G-04 render/accessibility/motion sections; G-04 remains `NOT-EVALUATED` because P-11 and P-12 have not run.

## Authorized boundary

Only P-08 was executed. P-09 and P-11 were not started. This change contains no brand/logo derivative, license/legal work, automated golden infrastructure, benchmark forward test, ZIP/package build, Git initialization, commit, push, or release action. Implementation is a clean-room-oriented independent reimplementation. The approved P-06/P-07 visual system is preserved and extended through original output/motion code; no upstream or Thien-UI-UX-Ultra code, prose, CSS, template, script, specimen, or asset was copied.

## Design route and contract

- Route: `extend → static diagram/web artifact → executive-artifact + design-system + chart integrity + localization + accessibility + motion`.
- Premise: preserve the complete approved static diagram and add portable output plus progressive motion that can always disappear without semantic loss.
- Preserved: P-06 tokens/modes, P-07 renderer/type coverage, semantic validation, exact fidelity, and neutral default styling.
- Extended: diagram-only SVG, self-contained HTML, conditional PNG, size/print output, exact-data alternatives, system-font fallback, generated motion controls, reduced-motion/no-JS/print behavior, capability ledger, and safe explicit file writing.
- The offline design-intelligence search reinforced reduced-motion control and exact text/table alternatives. Its results were treated as unverified design candidates; repository contracts and executed checks remained authoritative.

## Deliverables

- `thien-skill-creative-diagram/scripts/output_pipeline.py` — validated HTML/SVG export, conditional preinstalled rasterizer adapters, PNG validation/fallback, responsive/print sizing, exact-data alternatives, generated motion shell, ledger, capability registration, and safe writer.
- `thien-skill-creative-diagram/scripts/motion_catalog.py` — exact 12-capability static-first motion catalog and IR-evidence selector.
- `thien-skill-creative-diagram/scripts/p08_coverage.py` — exact P-08 disposition for seven output, 12 motion, and six P-08 failure capabilities.
- `thien-skill-creative-diagram/references/output-motion.md` and `references/p08-coverage-map.json` — runtime workflow and machine-readable P-08 coverage.
- `thien-skill-creative-diagram/scripts/tests/test_output_pipeline.py` — 27-type export, four-mode motion, size, accessibility, raster, safe-write, determinism, failure, and capability tests.
- `evidence/p08/output-motion-manifest.json` — deterministic 135-run output matrix, nine size runs, environment capability record, representative ledgers, and phase boundary.
- `evidence/p08/representative-static.html`, `representative-reveal.html`, `representative-step.html`, `representative-loop.html`, and `representative.svg` — QA-only local artifacts, not package payload.
- `evidence/p08/artifact-hashes.json` — SHA-256 of generated P-08 QA artifacts except this record and the hash file itself.

## Verification results

1. Full unit/regression suite: **93 tests, PASS**.
2. Portable matrix: **27/27 types**, each with standalone SVG plus HTML in `none`, `reveal`, `step`, and `loop` = **135/135 deterministic artifact runs, PASS**.
3. Output inventory: `CAP-O01..O07` = **7/7 mapped and tested**.
4. Motion inventory: `CAP-M01..M12` = **12/12 mapped and tested**. Public modes are exactly `none`, `reveal`, `step`, and `loop`.
5. P-08 failures: `CAP-F07..F12` = **6/6 mapped and tested** for missing rasterizer, target ambiguity, SVG boundary, font fallback, motion failure, and reduced-motion/print.
6. P-08 coverage map: **25/25 capability entries**, each with implementation disposition and stable test ID.
7. HTML: one inline complete SVG; no required external resource; no inline event handler; project-authored CSS/optional JS only; CSP blocks network/object/form/base activity; deterministic unique IDs; localized keyboard controls; no-JS complete state.
8. SVG: standalone XML, script-free, external-resource-free, accessible name/description, unique IDs, complete static frame, no P-07 QA badge, and localized exact data in description/metadata where required.
9. Exact-data alternative: quantitative charts and permission matrix add a source-precision table in HTML and exact data in SVG description/metadata.
10. Motion: complete material labels remain in the DOM; step order is stable; previous/next/replay/pause-resume and Arrow Left/Right/Home/End controls exist; loop token is decorative; print and `prefers-reduced-motion` force the complete static state.
11. Size/print: all nine approved presets are generated; SVG width/height expresses the selected surface while preserving the validated viewBox; A4/Letter print rules use landscape page size and 10 mm margins.
12. PNG environment: no approved rasterizer was detected (`cairosvg`, `rsvg-convert`, ImageMagick, Chromium, Playwright, Pillow all unavailable). No installation was attempted and no real PNG was claimed. PNG request → SVG fallback and HTML+PNG → HTML fallback both pass with precise warnings. A registered-adapter test verifies PNG signature, chunk checksums, required chunks, exact preset dimensions, output limit, parity ledger, and failure fallback.
13. Safe writes: exact relative targets required; absolute/traversal, missing/extra target, suffix mismatch, and implicit overwrite fail before mutation. Successful writes use a temporary sibling followed by atomic replacement.
14. Generated motion JavaScript in all three representative animated HTML artifacts passes Node syntax compilation. DOM/security/unit checks pass.
15. Browser/cross-browser execution is `blocked / not executable`: the available browser rejected local `file://` under its URL policy in the preceding local QA attempt, and no workaround/alternate browser was used. This is not reported as a browser pass and remains for P-11/P-12 execution on an allowed local/test surface.

## Skill validation limitation

The skill-creator `quick_validate.py` helper cannot start in this environment because the optional `PyYAML` module is absent. No dependency was installed. Equivalent frontmatter validation with Ruby's YAML parser, reference-link checks, generated-reference drift checks, JSON parsing, Python imports through the full test suite, and absence of placeholder/cache files are used instead.

## Key hashes at phase close

- `output_pipeline.py`: `1d3c83c3f927f672a325b8464580df85aa5ed1ba770bb5cbbec695171f8bbd32`
- `motion_catalog.py`: `be83b6e65482743d4e4bbc0069a59c4c8a9fb734d8a68e1aec1f696da1351b56`
- `p08_coverage.py`: `4f29c006fd91827929da453008849ab5b9daf3b08951ce65411dad92d2a54413`
- `p08-coverage-map.json`: `3ef6980472e01968bed844588c5a10cd1bc8e57e905fe7f0071f788dd60339c3`
- `output-motion-manifest.json`: `7f8ad957d856e9a8716c3655ce13258dad32bb71ae8603a0d97215932d7a05b8`
- `artifact-hashes.json`: `5510de8d83009257270a64481734f09745d17a077697de644ae78bc78af8e6a3`
- `representative-static.html`: `3ea62519c7d375eb84c2c1889a7441fba5fea284d44ad0f281226a1debfd85c8`
- `representative-step.html`: `ed6f2f482ecce4640d69c72f388eb822fc32e16a81c7cb9d8fb5ec65a194fbf4`
- `representative.svg`: `b68cefc66bfb5fad1d1796b12774cba89946d1affe385a1d1b28a68f87a50f81`

P-08 satisfies its phase verification: HTML/SVG core is portable, PNG capability is conditional without auto-install, and motion cannot remove static meaning. G-04 is not evaluated; P-09 and P-11 remain `not-started` and unauthorized.
