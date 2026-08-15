# P-12 Residual Risk Log

**Date:** 2026-08-15  
**Scope:** P-12 technical benchmark and independent forward testing only  
**Current result:** P-12 `passed`; G-04 `PASS`; zero open Critical/High finding

| ID | Severity | Residual condition | Evidence / control | Gate effect |
|---|---|---|---|---|
| `P12-R01` | Medium | The in-app browser URL policy rejected the local `file://` contact sheet, so no browser or cross-browser pass can be claimed. | Static SVG/HTML validation, deterministic hashes, geometry checks and the QA-only contact sheet are available. The owner can inspect the local contact sheet manually; installed-surface/browser validation remains explicit future evidence. | Does not convert to a technical hard failure, but must remain disclosed. |
| `P12-R03` | Low | No approved preinstalled rasterizer was available to the canonical pipeline; requested PNG variants used the declared HTML/SVG fallback. A preinstalled Chrome attempt in one forward test also failed. | No dependency was installed, no fake PNG was claimed, and fallback warnings were recorded in benchmark and forward-test evidence. | Must remain a disclosed output limitation; re-evaluate on installed surfaces in P-13. |
| `P12-R04` | Low | Automatic host activation was not measured on an installed package. | Direct invocation and one adjacent negative trigger passed fresh-session tests; 27 intent routes and ambiguity handling passed contract tests. | Installed-surface discovery belongs to P-13; no automatic-trigger claim is made now. |

## Closed findings found during P-12

| ID | Original severity | Finding | Corrective evidence | Status |
|---|---|---|---|---|
| `P12-F01` | High | Pyramid/Funnel validation rejected a truthful non-monotonic increase, contradicting the approved benchmark contract. | Validation now checks rendered stage order against exact-data metadata; non-monotonic values pass, while order drift fails. Regression and E2-Q06 pass. | Closed |
| `P12-F02` | High | Bar rendering anchored negative values to the chart bottom instead of the zero baseline. | Renderer now derives the zero baseline from domains containing zero, separates positive/negative stacks, and positions negative labels correctly. Focused regression, E2-Q01 and a fresh forward retest pass. | Closed |
| `P12-R02` | Medium | Exact P-12 implementation-fixture bytes and rendered contact-sheet/golden candidates required owner approval. | The owner approved the exact candidate inputs, contact sheet/goldens, visual rubric and G-04 on 2026-08-15. `candidate-inputs.json` and `approved-p12-golden-manifest.json` lock the approved hashes. | Closed |

No P-09, packaging, logo/license, ZIP, Git initialization, commit, push or release action was performed.
