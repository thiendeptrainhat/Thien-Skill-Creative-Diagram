# P-06 — Original Visual System & Pilot Evidence

**Date:** 2026-08-15  
**Authorized scope:** P-06 only  
**Phase result:** passed  
**Gate effect:** G-03 `PASS`

## 1. Authority and boundary

- The owner explicitly authorized only P-06 on 2026-08-15.
- P-05 is `passed`; the P-06 dependency is satisfied.
- This change set is limited to an original visual token/rule system, pilot-only layout/routing/render behavior, original pilot fixtures, static HTML/SVG candidates, QA-only raster evidence, tests, and this evidence record.
- The implementation supports exactly three pilot families and refuses other visual families. P-07 full visual coverage, safe import, general renderer/export behavior, and motion were not started.
- No logo or license work, ZIP build, Git initialization, commit, push, release, external dependency installation, or network-fetched runtime asset occurred.
- The owner-authorized reference image remains QA-only and is not part of any release payload.

## 2. Deliverable inventory

| Path | Role | SHA-256 |
|---|---|---|
| `thien-skill-creative-diagram/SKILL.md` | progressive routing to the exact P-06 pilot handler and honest non-pilot fallback boundary | `c5c1eea5e779ef00ab6c39b2e1617868e259711b7e95edf1eb3d23e6d36473a2` |
| `thien-skill-creative-diagram/references/visual-system.json` | canonical exact tokens for the three approved static modes | `77ab0f8c4e65bf213342aa07dd09445b3b1f8b5745e026c0aac637e993a8c2a8` |
| `thien-skill-creative-diagram/references/visual-system.md` | original hierarchy, type, spacing, shape, connector, legend, annotation, density, accessibility, and pilot-support rules | `10c54653c324630e167a442512498a5bd0a3eb14c64cd6b3ea8a598c91357196` |
| `thien-skill-creative-diagram/scripts/visual_system.py` | token loader, contrast verification, geometry primitives, and overlap/crossing checks | `48dbaaa91dd719fa128ac1bd6a17df495b7bf14799542588419dce6d49f0f5db` |
| `thien-skill-creative-diagram/scripts/pilot_cases.py` | independently written and semantically validated pilot IR fixtures | `038af6eedec83c38b6f6ce57f3efc53d27e103dfdc86932a929629373c02e8f2` |
| `thien-skill-creative-diagram/scripts/pilot_renderer.py` | deterministic, self-contained pilot layout/routing and HTML/SVG renderer | `e79a4d9586a9e8e0adab9d177bfa873607c0ae6b676acc5e3d3a0738ba89f0ee` |
| `thien-skill-creative-diagram/scripts/tests/test_pilot_renderer.py` | P-06 mode, contrast, determinism, serialization, geometry, chart, and benchmark tests | `d01726af91e8f6f17716784fecc3f6f04a12c5f43e9ee24341fef0bd62fc03f5` |
| `evidence/p06/golden-candidates/pilot-manifest.json` | hashes and validation results for 18 HTML/SVG artifacts | `556aa495565e41f9bae28f656e37483f6e1a81fb8e47300adc0725b944691d5f` |
| `evidence/p06/golden-candidates/contact-sheet.html` | owner-review contact sheet for all nine visual candidates | `456004a2c64ae97029f4fe2d7fe2713221c2d2df03fb2aaa5de4460dfa485274` |
| `evidence/p06/golden-candidates/contact-sheet-browser.jpg` | QA-only browser capture of the contact sheet; not a release artifact | `7b8a7e814afb35af2059025e523821fd9dbc7bda84eb386c91a716a31ed11824` |

The manifest covers three families × three modes × two core formats: 18 deterministic HTML/SVG artifacts. The browser contact-sheet image and the preliminary Quick Look previews under `golden-candidates/previews/` are QA-only and excluded from release packaging.

## 3. Workstream coverage

| P-06 workstream | Evidence |
|---|---|
| three approved static modes | exact `neutral-light`, `neutral-dark`, and `editorial` token sets; no brand palette or logo |
| visual behavior rules | system font fallback, 8 px spacing rhythm, hierarchy, semantic shape vocabulary, connector/routing rules, legends, annotations, density limits, and contrast pairs are recorded in the canonical visual-system reference |
| representative pilot subset | architecture exercises semantic pattern `CAP-P05`; grouped bar exercises variant `CAP-V05`; grouped Vietnamese swimlane exercises the approved benchmark semantics |
| non-single-case layout/routing | shared geometry primitives and validation support three distinct families, nine mode/case combinations, orthogonal relationship routing, bounds checks, endpoint checks, node-overlap checks, and unrelated-node crossing checks |
| multi-connector diagram | architecture pilot renders eight nodes, eight relationships, three grouped boundaries, a standard route, and a visibly denied bypass |
| quantitative chart | grouped bar preserves all eight exact values, unit, direct labels, legend, zero baseline, and an accessible exact-data table |
| Vietnamese grouped swimlane | six lanes, two grouped ownership headers, semantic check/document/listing/file shapes, independently traceable handoff badges, consistent legend, and Vietnamese diacritics |
| render–inspect–revise–verify | all nine candidates were inspected as rendered browser output; representative light, dark, and editorial cases were visually reviewed at 1600×900; architecture was also checked at 1024×768; font tokens were revised to use only local system fallback |
| owner review artifact | contact sheet presents all nine golden candidates and explicitly marks owner review as required |

## 4. G-03 technical and QA assessment

| Assertion | Result | Evidence |
|---|---|---|
| one multi-connector diagram | PASS candidate | architecture pilot and geometry tests |
| one quantitative chart | PASS candidate | grouped bar, exact-data table, and quantitative tests |
| approved Vietnamese grouped benchmark | PASS candidate | grouped swimlane semantic and geometry tests |
| all three approved static modes | PASS candidate | nine deterministic combinations and contact sheet |
| HTML and SVG | PASS candidate | 9 self-contained HTML plus 9 SVG artifacts |
| PNG when renderer is available | CONDITIONAL / disclosed | no suitable installed standalone rasterizer; browser capture retained only for QA, while cropped Quick Look thumbnails are not accepted as per-artifact PNG parity |
| correct lanes and ownership groups | PASS candidate | six lanes and two ownership headers |
| semantic check/document/listing/file shapes | PASS candidate | original role-specific shape vocabulary and benchmark test |
| independently traceable steps/handoffs | PASS candidate | numbered connector badges and semantic assertions |
| correct connector endpoints and no unrelated-node crossing | PASS candidate | route validation and rendered inspection |
| consistent legend and Vietnamese diacritics | PASS candidate | serialized content checks and rendered inspection |
| no clipping, unintended overlap, or hidden complexity | PASS candidate | geometry checks and browser checks at 1600×900 and 1024×768 |
| accessible SVG and non-color-only meaning | PASS candidate | title/description/image role, unique IDs, shapes/hatching/line-style redundancy, contrast tests |
| original output, not a pixel clone | PASS candidate | independent fixtures, tokens, shapes, layout, prose, and code; provenance statement below |
| owner approval of golden direction | PASS | Tran Ngoc Thien approved the P-06 golden direction, confirmed the current technical/QA review as sufficient, and approved G-03 `PASS` on 2026-08-15 |

## 5. Automated test evidence

Command:

```text
PYTHONDONTWRITEBYTECODE=1 python3 -m unittest discover \
  -s thien-skill-creative-diagram/scripts/tests -v
```

Result:

```text
Ran 47 tests
OK
```

The 47 tests include the 37 passing P-04/P-05 regression tests and 10 P-06 tests. P-06 coverage verifies exactly three modes, material text size, all required contrast pairs, exactly three authorized pilot families, deterministic rendering for all nine combinations, valid self-contained serialization with accessible naming and unique IDs, relationship geometry, exact grouped-bar values and zero baseline, and the approved swimlane semantics.

Additional checks:

| Check | Result |
|---|---|
| browser render audit of all nine HTML candidates | PASS: one SVG each, accessible title/description, unique IDs, no external asset, and viewport fit |
| contact sheet | PASS: nine cards and all images loaded |
| 1024×768 responsive check | PASS: no horizontal overflow; SVG scaled to 992×620; print rule present |
| Python syntax | PASS |
| JSON syntax | PASS |
| `SKILL.md` relative links | PASS: 34 unique targets resolve |
| Ruby YAML/frontmatter validation | PASS |
| unfinished-marker scan | PASS |
| ZIP, bytecode/cache, logo, and license scan | PASS |

The bundled `quick_validate.py` was invoked but cannot import `yaml` because PyYAML is absent from the local runtime. No dependency was installed. Equivalent Ruby YAML/frontmatter validation and the phase-specific Python, JSON, link, render, geometry, and browser checks passed.

## 6. Raster limitation

No suitable standalone SVG-to-PNG renderer is installed. Quick Look can create thumbnails but crops the wide pilot canvas, so those previews are explicitly not accepted as core PNG output or golden parity evidence. The in-app browser produced a complete contact-sheet capture for QA only. HTML and SVG remain the P-06 core artifacts, matching the approved conditional-output contract without silently installing a dependency.

## 7. Provenance conclusion

- `diagram-design` remains the primary functional baseline at taxonomy, abstract behavior, quality target, and failure-mode level only.
- All P-06 code, prose, CSS, tokens, fixtures, shapes, layouts, routes, annotations, data, and examples were independently written for this repository.
- No upstream code, prose, CSS, template, script, specimen, gallery, or asset was copied, translated, traced, or repackaged. The grouped swimlane preserves the locked benchmark semantics while using a distinct layout and visual expression.
- `Thien-UI-UX-Ultra` influenced only the approved design-contract, design-judgment, accessibility, localization, and render–inspect–revise–verify workflow.
- Repository files, the QA-only reference image, and generated artifacts were treated as data; no embedded instruction, prompt, script, or link was executed.
- The precise boundary remains “clean-room-oriented independent reimplementation,” not an absolute clean-room claim.

## 8. Approval record

On 2026-08-15, Tran Ngoc Thien approved the P-06 golden direction, confirmed the current technical/QA review as sufficient, and approved G-03 `PASS`. P-06 therefore satisfies its exit criteria and may be marked `passed`. This approval does not authorize P-07; P-07 remains `not-started`.
