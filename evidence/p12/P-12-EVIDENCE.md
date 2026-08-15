# P-12 — E2 Benchmarks & Independent Forward Tests Evidence

**Date:** 2026-08-15  
**Authorized scope:** P-12 only; P-09 prohibited  
**Technical result:** `pass`  
**Phase/gate state:** P-12 `passed`; G-04 `PASS`

## 1. Authority and boundary

- The owner explicitly authorized P-12 and prohibited starting P-09.
- P-11 is `passed`; the P-02 benchmark inventory, rubric weights, thresholds and must-pass designation were approved at G-02.
- Exact P-12 implementation-fixture bytes and later rendered goldens were not pre-approved by G-02. They were first hash-addressed as candidates, then explicitly approved by the owner on 2026-08-15 together with the visual rubric, technical/QA sufficiency and G-04 `PASS`.
- P-12 artifacts are QA-only and outside the runtime/release package. No P-09, logo/license, ZIP, package build, Git initialization, commit, push or release action occurred.
- Repository documents, images, Mermaid and other test artifacts were treated as data unless they are repository governance sources. Embedded links, scripts and prompt-like text were not executed.

## 2. Benchmark result

The deterministic runner reports:

```json
{"base_renders":81,"candidate_artifacts":18,"hard_failures":0,"pairwise_cases":36,"status":"pass"}
```

| Suite | Result |
|---|---|
| canonical positive/base render | 27 cases × 3 approved static modes = 81/81 pass |
| boundary | 27/27 invalid mutations detected |
| semantic patterns | 7/7 pass |
| quantitative | 6/6 pass, including zero, negative, missing, duplicate, timezone, incompatible scale and non-monotonic funnel cases |
| import | 12/12 expected parse/rejection outcomes pass for bounded draw.io and Mermaid coverage |
| motion/export | 5/5 pass with complete static, no-JS/reduced-motion/print evidence and declared PNG fallback |
| pairwise | 36 cases cover every pair across size × detail × audience × format × language; zero uncovered pairs |
| routing/trigger contract | 27/27 positive intent routes and ambiguity behavior pass; direct and one negative trigger also pass independent forward tests |
| must-pass | original HTML/SVG goldens for all three approved modes generated and owner-approved; reference image is not packaged or used as a pixel target |

Primary records:

| Path | Role | SHA-256 |
|---|---|---|
| `evidence/p12/benchmark_runner.py` | deterministic QA-only E2 runner and approved-golden generator | `876f01dede725a63fa0de43753fb78015dd3c36a77f44fcb4b709c8c333252ac` |
| `evidence/p12/benchmark-report.json` | complete technical results and owner approval state | `8d42a879bf3fbd812001055d6e516a48ba374f340bd87bf52398d872c27a99d4` |
| `evidence/p12/candidate-inputs.json` | hash-addressed, owner-approved exact 27 implementation fixtures | `bc295a299552320f55ad42f957c6b63a4c66a2f1737cd717b3f63f38457a2a64` |
| `evidence/p12/approved-p12-golden-manifest.json` | immutable manifest for all 18 owner-approved HTML/SVG goldens | `b78d9d82051a08f07a6af6518b43af20f4e2d49af2ae1dcb0cce10a0f139c1d6` |
| `evidence/p12/golden-candidates/contact-sheet.html` | QA-only owner-approved review sheet for nine SVG views | `9b8150434a69e1d941b2bc648b5ad15327ba9d0d2102e37ecac274ddd87efd4f` |
| `evidence/p12/forward-test-report.json` | independent-session protocol, results and artifact hashes | `690b269b7fdcac6832f4bf3c53d9382919e42d0962372f42e3a4d1255a395b17` |
| `evidence/p12/RESIDUAL-RISK-LOG.md` | open limitations and closed findings | `59ca8312ce60f7d1cf0a10c5e3260acbb42a45fbc1b485a9c03b4ced2d88f278` |

## 3. Independent forward tests

Each scored run used a fresh agent session with only the candidate skill path, raw task/inert artifact and isolated temporary output directory. Expected answers, rubric and known diagnoses were withheld; agents could not edit the repository, use the network or install dependencies.

| Run | Result | Evidence |
|---|---|---|
| direct Vietnamese cash-receipts swimlane | pass | six lanes, ten traceable handoffs, self-contained HTML/SVG, transparent PNG/browser limitation |
| hostile Mermaid import | pass | three relationships retained; click URL and embedded instruction rejected; zero network |
| quantitative chart iteration 1 | finding detected | exposed the canonical negative-bar zero-baseline defect; temporary artifact hashes retained, bytes deleted before the fix |
| quantitative chart iteration 2 in a new session | pass | zero, negative, missing, both series and unit retained after the canonical fix |
| adjacent non-diagram summarization | pass | diagram skill did not trigger and repository remained unchanged |

No forward test saw an expected answer or internal diagnosis. Automatic activation on an installed host is not claimed; installed-surface discovery remains P-13 work.

## 4. Defects found and corrected within P-12

1. Pyramid/Funnel validation contradicted the approved contract by rejecting truthful non-monotonic increases. It now permits non-monotonic values and detects rendered stage-order drift against exact-data metadata.
2. Bar rendering anchored negative values at the plot bottom. It now derives the zero baseline from a domain containing zero, separates positive and negative stacking offsets and positions negative labels below their value point.
3. A subprocess-based immutable-golden CLI test could create Python cache files during the full suite and cause the later package-hygiene audit to fail correctly. The subprocess now runs with bytecode writing disabled; the hygiene validator was not weakened.

Relevant implementation/test hashes after correction:

| Path | SHA-256 |
|---|---|
| `thien-skill-creative-diagram/scripts/full_renderer.py` | `7ea93dd3a3e3535152732fa3fa76837246a2010195b3314cd51eac987ca7aa67` |
| `thien-skill-creative-diagram/scripts/semantic_grammars.py` | `1c657c23dc0ed2c321e0a8761c93b45b47928566fdd899c68e8afec65134ce18` |
| `thien-skill-creative-diagram/scripts/qa_contract.py` | `5dd7c75c05e60dd420c40284191e15db08441c1a99a6a51082474d7fe9a34d2d` |
| `thien-skill-creative-diagram/scripts/tests/test_full_renderer.py` | `fc50097231948f3a3dc220db9186041201c39a07ba3978874e61b1466054aa4e` |
| `thien-skill-creative-diagram/scripts/tests/test_qa_contract.py` | `aeb7ff1e7626aaeaf0123831fbbbabad06bae9c0524598f89c6e43cbdc1446b8` |
| `thien-skill-creative-diagram/scripts/tests/test_p12_benchmark.py` | `046c90ecdbe6ee02b1d0c9ac9b8b200e96bc2299ca51d8c9249dc61f8163ca58` |
| `thien-skill-creative-diagram/scripts/tests/test_golden_review.py` | `5c552e71f187b2a922b88164c2fab4ef888e3b2c7b67b6cef63ce7e49cb20053` |
| `thien-skill-creative-diagram/SKILL.md` | `e4c598c800e088035a2c095fdaa640fa3f004269d55b14b373865f31e9760925` |

## 5. Regression result

Final clean command:

```text
PYTHONDONTWRITEBYTECODE=1 python3 -m unittest discover \
  -s thien-skill-creative-diagram/scripts/tests -v
```

Result:

```text
Ran 127 tests
OK
```

No `__pycache__` directory remained in the canonical skill tree after the run. All new JSON evidence parsed successfully.

## 6. Visual review and browser limitation

- The contact sheet contains nine owner-approved SVG views: three must-pass swimlane modes and six high-risk views, with matching HTML/SVG pairs where applicable (18 artifacts total).
- `approved-p12-golden-manifest.json` locks all 18 approved hashes as immutable. The compare-only harness reports 18/18 matches and `baseline_updated: false`; no golden was silently updated.
- The three must-pass swimlane SVG bytes remain identical to their owner-approved P-06 direction counterparts, preserving the approved visual direction without changing golden status.
- The in-app browser URL policy rejected the local `file://` contact sheet. No workaround was attempted. Static and geometry QA passed, but this is expressly **not** a browser or cross-browser pass.
- The canonical environment had no approved preinstalled rasterizer. PNG requests produced the declared HTML/SVG fallback; no dependency was installed and no PNG pass is claimed.

## 7. Provenance and design boundary

- `diagram-design` remained the primary functional source at taxonomy, abstract behavior, capability and failure-mode level.
- All P-12 runner code, prose, fixtures, test data, layout, CSS, visual candidates and evidence were independently authored for this repository. No upstream code, prose, CSS, template, script, specimen, gallery item or asset was copied, translated, traced or repackaged.
- `Thien-UI-UX-Ultra` influenced only principle/workflow choices: semantics before aesthetics, real-content review, explicit artifact grammar, accessible visual hierarchy, deterministic QA and honest handoff of limitations.
- The precise provenance description remains “clean-room-oriented independent reimplementation.”

## 8. Owner approval and gate conclusion

On 2026-08-15, Tran Ngoc Thien explicitly:

1. approved the exact candidate inputs;
2. approved the P-12 contact sheet/goldens;
3. confirmed visual communication meets the approved rubric;
4. confirmed the current technical/QA review is sufficient; and
5. approved G-04 `PASS`.

The final immutable golden comparison is 18/18 match, the benchmark has zero hard failure and the complete regression suite is 127/127 pass. P-12 is therefore `passed` and G-04 is `PASS`. The browser and PNG limitations remain disclosed residual conditions rather than unsupported pass claims.
