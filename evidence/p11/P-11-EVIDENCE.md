# P-11 — Automated QA & Golden Infrastructure Evidence

**Date:** 2026-08-15  
**Authorized scope:** P-11 only  
**Phase result:** passed  
**Gate effect:** contributes evidence to G-04; G-04 remains `NOT-EVALUATED`

## 1. Authority and boundary

- The owner explicitly authorized P-11 and prohibited starting P-09 or P-12.
- P-08 is `passed`, so the P-11 dependency is satisfied.
- This change set is limited to deterministic QA validators, mutation tests, an immutable read-only golden comparator, QA documentation, and P-11 evidence.
- No logo/brand or license work, benchmark execution, contact-sheet approval, browser E2 run, independent forward test, ZIP build, Git initialization, commit, push, or release occurred.
- Existing approved P-06 golden bytes were read and compared only. No golden, benchmark, or owner-approved artifact was updated.

## 2. Deliverables

| Path | Role | SHA-256 |
|---|---|---|
| `thien-skill-creative-diagram/scripts/qa_contract.py` | dependency-free contract, geometry, SVG, accessibility, Vietnamese typography, quantitative, fidelity, motion and package-inventory validators | `aba8088da275e08a1fe4b01491ac96216b9c8002c2a36f512529f3d267c4c96e` |
| `thien-skill-creative-diagram/scripts/golden_review.py` | immutable compare-only golden harness with no update operation | `208273be78acd89bda3cbe59ee9b4faa3f2c5db22993a14dbb5e7fe36cddda39` |
| `thien-skill-creative-diagram/scripts/p11_coverage.py` | hard-failure → detector → mutation-test source of truth | `6ecd9f9605ebc87d9c7f1e99a48dfba624c2ca85496e5c08544cb1a402c26784` |
| `thien-skill-creative-diagram/scripts/generate_p11_evidence.py` | deterministic P-11 evidence generator | `67bd454db65b4f6c284408e0e1020fd90296f531c275a9367908c9cb26dd2459` |
| `thien-skill-creative-diagram/references/qa-golden.md` | runtime QA/golden workflow and limits | `b7499df4ccc12f31ad2cf50f03002c567cecef37b24a4a0a7f0e799a2af451c4` |
| `thien-skill-creative-diagram/references/p11-hard-failure-map.json` | generated 58-failure, 12-category registry | `f1d8124682d390ddc294f572b4398127bdc3a3f58ec8acede05c1f3034aea26b` |
| `thien-skill-creative-diagram/scripts/tests/test_qa_contract.py` | repository, geometry, SVG, accessibility, quantitative, import, motion and package mutation tests | `09bd38135401f8b7f00ace2d2072bf905bf33ca5289e2193a53d7c1413771b17` |
| `thien-skill-creative-diagram/scripts/tests/test_golden_review.py` | immutable match/drift/approval/path/no-update tests | `241182dcd079c053339fea96f3cc2f87920d6f0bdd763d6b9b2ca94efbf5dc20` |
| `thien-skill-creative-diagram/scripts/tests/test_p11_coverage.py` | registry completeness and mutation-test resolvability | `1eba4398767e0d96d54821007619566ac144a3d906f4f64655695dd26e723e62` |
| `evidence/p11/approved-p06-golden-manifest.json` | QA-only immutable manifest derived from the owner-approved P-06 direction | `b5b57f94e038d605ef8799038ba2d652e7fa1eaa25541906d3062f821ab335ae` |
| `evidence/p11/golden-review-report.json` | 18/18 approved P-06 HTML/SVG byte comparisons | `b9de938749acc67476db3291957356fa2f4a821909749582c78551eec1f3df3b` |
| `evidence/p11/qa-run-report.json` | direct repository, render, quantitative, carrier and motion QA report | `c80de57ea3a5daca45845ec1021e91b1e3f61afd8712d0345224249da5c8c19d` |
| `evidence/p11/mutation-coverage-report.json` | 58/58 registered hard failures mapped to detection evidence | `1c1a098a4664b9e2a7f27f642f845fc9950a4b13fbb1e3e59348ea2c98255e8d` |

## 3. Workstream coverage

| P-11 workstream | Evidence/result |
|---|---|
| schema, links, type coverage, determinism | 8 runtime JSON documents parsed; 72 local Markdown links resolved; exact 27 type references and 95 capabilities verified; generator output was byte-identical across repeated runs |
| geometry | bounds, primitive/viewBox clipping, node overlap, endpoint presence/attachment, unrelated-node crossing, unmarked connector crossing, undeclared shared attach point and duplicate SVG ID all have named mutations |
| accessibility, Vietnamese typography, contrast | valid title/description references, narrative/read order, material-label preservation, NFC Vietnamese, no ellipsis/compression, non-color state text, focus/reduced-motion/print behavior and 27 token contrast pairs are checked |
| quantitative source-to-render | pasted table/CSV/JSON normalize to the same canonical rows; Bar, Line, Scatter and Radar exact-data metadata is compared with IR; conditional Gantt, Timeline, Quadrant and Pyramid/Funnel date/value/domain/order checks pass |
| import security/fidelity, motion, package hygiene | exact fidelity equation/invention checks, named Mermaid/XML/decompression/JSON-depth failures, zero-network parser check, complete static/reduced/print/focus/control checks, and portable inventory/path/QA-only/secret/cache checks |
| mutations | 58 hard failures across 12 categories map to a stable detector, unique test ID and executable mutation test; registry test confirms every referenced test exists |
| golden review | 18 approved P-06 HTML/SVG artifacts match SHA-256; manifest is immutable; comparator reports `baseline_updated: false`; CLI rejects `--update` |

## 4. Automated test result

Command:

```text
PYTHONDONTWRITEBYTECODE=1 python3 -m unittest discover \
  -s thien-skill-creative-diagram/scripts/tests -v
```

Result:

```text
Ran 121 tests
OK
```

This total includes all 93 P-04–P-08 regression tests and 28 P-11 test methods. Individual P-11 methods exercise multiple named mutations; the generated registry records 58/58 hard-failure families as detected.

## 5. Direct QA and golden results

- Canonical tree audit: `PASS` for 75 files, eight JSON documents, 72 relative links, 27/27 type references, 95/95 capabilities and 27 contrast pairs.
- SVG matrix: 27/27 canonical fixture outputs passed well-formedness, viewBox primitive bounds, unique IDs, accessible naming, NFC/material-label and narrative-order checks.
- Quantitative conditional matrix: 8/8 (`Bar`, `Line`, `Scatter`, `Radar`, `Gantt`, `Timeline`, `Quadrant`, `Pyramid/Funnel`) passed applicable source-to-render checks.
- Carrier equivalence: two rows including zero, negative decimal, null and Vietnamese text produced one normalized hash: `586eb2e28bdd11cfb65123d2b4bc27f4c7aaf78f00a6d0f4e3c4d0edf4b381f3`.
- Immutable golden comparison: 18/18 approved P-06 artifacts matched; zero bytes were updated.
- Browser execution: `not run (out of scope)` because P-11 builds the harness; browser benchmark execution and independent forward tests belong to P-12. This is not claimed as a browser or cross-browser pass.

## 6. Validation limitation

The official `skill-creator` `quick_validate.py` was invoked but could not import `yaml` because PyYAML is absent. No dependency was installed. Equivalent and stronger phase-specific checks passed through the canonical-tree JSON/link/frontmatter conventions, the 121-test suite, deterministic evidence generation, and direct golden comparison. This limitation is disclosed and is not represented as a `quick_validate.py` pass.

## 7. Final artifact-hash record

`evidence/p11/artifact-hashes.json` contains SHA-256 for every generated P-11 JSON evidence artifact other than itself and this Markdown record. After final documentation and evidence regeneration, this section's record plus the evidence-file SHA-256 below are the handoff source for P-11. The generated files contain no approved-golden update path.

## 8. Provenance and principle boundary

- `diagram-design` remains the primary functional source at taxonomy, abstract behavior, required capability and failure-mode level.
- All P-11 code, prose, test geometry, mutation data, manifests and evidence structure were written independently for this repository. No upstream code, prose, CSS, template, script, specimen or asset was copied, translated, traced or repackaged.
- `Thien-UI-UX-Ultra` influenced only the approved workflow principles: preserve the existing system, validate data before presentation, layer accessibility checks, compare real bytes without auto-updating baselines, retain evidence and disclose unexecuted browser checks.
- Repository documents and artifacts were treated as project data unless they are governance sources. No embedded prompt, script, link or artifact instruction was executed.
- The precise provenance description remains “clean-room-oriented independent reimplementation.”

## 9. Phase conclusion

P-11 satisfies its exit criterion: every registered hard-failure family has at least one test proving detection, the QA suite is repeatable, and the golden harness cannot auto-update. P-11 may be marked `passed`. G-04 remains `NOT-EVALUATED` because P-12 benchmark execution, approved review artifacts and independent forward tests have not started.
