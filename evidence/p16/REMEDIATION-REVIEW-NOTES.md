# P-16 remediation and review notes

**Record ID:** `P16-REMEDIATION-2026-08-22`  
**Authority:** owner request to remediate all P-16 review findings and obtain agent re-review  
**Scope:** P-16 governance/evidence only  
**Status:** remediation/re-review complete; owner approved both gates and P-16 closure under D-047

## 1. Initial review outcome

Three independent read-only agent roles reviewed the initial P-16 candidate: G-01/provenance, G-02/product-architecture-test and cross-document consistency. They found no Critical issue, but recommended against gate readiness because High/Medium/Low findings remained. No reviewer edited files.

The first post-remediation re-review cleared the broad consistency findings but found two substantive residual gaps: the provenance analysis covered only the 74-path skill subtree rather than the entire 170-path repository range, and the G-02 packet still lacked exact quantitative policies plus three schema/semantic bindings. Those findings triggered the second remediation rows below. Final post-second-remediation review and delta confirmation then closed all findings without changing either gate.

## 2. Finding closure map

| Finding | Initial severity | Remediation | Evidence | Closure status |
|---|---|---|---|---|
| Missing version-scoped mapping for 12 canonical additions + four variants | High | Added stable IDs `CAP-T28..T39`, `CAP-V17..V20`, exact source/hash, requirement, independent implementation plan, test family, invariants and copying-risk boundary. | `CAPABILITY-PROVENANCE-MATRIX.md` | REMEDIATED |
| Capability-bearing upstream delta incomplete | High | First classified the 74-path skill subset, then after re-review added an exact whole-repository 170-path status/disposition ledger, including all 96 paths outside `skills/diagram-design/**`, full `+23895/-244` stats and set-equality verification. | `UPSTREAM-FULL-RANGE-LEDGER.json`; `UPSTREAM-CAPABILITY-DELTA.md`; `UPSTREAM-DELTA.json` | REMEDIATED |
| P-02 product/request/IR/test still 27 and insufficient for Sankey/Bubble | High | Preserved P-02 as historical v1.0.0; added exact 1.5 request and IR schemas, 39-type enum, direct Sankey amount/unit and Bubble x/y/size fields, structured semantics and appended test families. | `REQUEST-1.5.schema.json`; `SEMANTIC-IR-1.5.schema.json`; `PRODUCT-ARCHITECTURE-TEST-DELTA.md` | REMEDIATED |
| Circular G-02 dependency through P-17 | High | Made G-02 completely lockable in P-16; changed P-17 to contribute only G-04 readiness. | `PLAN.md`; `PHASE-GATES.md`; `ROADMAP.md` | REMEDIATED |
| Missing exact version-bound G-02 packet | High | Hash-bound ten inherited P-02 artifacts and nine P-16 delta artifacts, including the full-range ledger, in one machine-readable packet. | `G02-1.5.0-CONTRACT-MANIFEST.json` | REMEDIATED |
| Quantitative/boundary policies and tolerances were not exact | High | Locked one semantic epsilon, unit normalization/no-conversion rule, SVG coordinate/length/area tolerances, and explicit zero/negative/missing policy for Polar, Treemap, Sankey, Dumbbell, Slopegraph, Bubble and Ridgeline. Added immutable positive/boundary/hard/render/accessibility/quantitative test suffixes. | `PRODUCT-ARCHITECTURE-TEST-DELTA.md` §4.1–4.2; `CAPABILITY-PROVENANCE-MATRIX.md`; `PILOT-GALLERY-CONTRACT.md` | REMEDIATED |
| Treemap and Ridgeline IR under-specified | High | Added Treemap leaf-parent binding plus group declared total/unit; added structured Ridgeline method/domain/bin edges/bin count/bandwidth/global-max/shared flags and exact histogram/KDE contracts. | `SEMANTIC-IR-1.5.schema.json`; `PRODUCT-ARCHITECTURE-TEST-DELTA.md` | REMEDIATED |
| Story-map unassigned case and DB index structure mismatched contract | High | Allowed and schema-bound only the null/unassigned Story-map pair; required ordered indexed column/member IDs plus explicit uniqueness for physical DB index members. | `SEMANTIC-IR-1.5.schema.json`; `PRODUCT-ARCHITECTURE-TEST-DELTA.md` | REMEDIATED |
| Current official platform revalidation missing | Medium | Rechecked official Agent Skills, Claude and OpenAI documentation; recorded access/hash receipt and explicit no-promotion inheritance. | `PLATFORM-SURFACE-REVALIDATION.md` | REMEDIATED |
| Verification too narrow | Medium | Expanded verification to source hashes/counts, exact 170-path upstream set equality, 74/96 pathscope partition, schema/type/field/policy checks, manifest hashes, pilot counts, provenance/license/UIUX binding, duplicates and unchanged runtime/dist. | `P-16-VERIFICATION.json`; `P-16-EVIDENCE.md` | REMEDIATED / VERIFIED |
| Pilot case/rubric not exact | Medium | Locked 12 stable case IDs with concrete data/semantics/assertions and inherited exact rubric/hash; execution still requires owner approval and separate authorization. | `PILOT-GALLERY-CONTRACT.md` | REMEDIATED |
| Surface matrix inheritance ambiguous | Medium | Declared byte-bound P-02 matrix inheritance, no support-status promotion and mandatory recheck if packaging is ever proposed. | `PLATFORM-SURFACE-REVALIDATION.md`; `PRODUCT-ARCHITECTURE-TEST-DELTA.md` | REMEDIATED |
| PLAN historical paragraphs looked current | Medium | Labeled detailed P-00–P-15 evidence as historical-at-phase-close and corrected stale table notes. | `PLAN.md` | REMEDIATED |
| HANDOFF-CURRENT stale at P-15/27 types and later decision-range wording stopped at D-040 | Low | Updated handoff to P-16 in-progress, 39+4 candidate, D-001..D-046 with P-16 decisions called out, exact packet/170-path ledger and unchanged authorization boundary. | `HANDOFF-CURRENT.md` | REMEDIATED |
| Upstream third-party ledger not bound | Low | Recorded unchanged `THIRD_PARTY_LICENSES.md` hash `22f5afcea56373e84d7f7eff93d8d4d6e4b81c5375bb1c996e78b91e53fa0b37`. | `UPSTREAM-CAPABILITY-DELTA.md`; `UPSTREAM-DELTA.json` | REMEDIATED |
| Thien-UI-UX-Ultra inheritance not explicit | Low | Bound P-01 snapshot `fb4e577...`, tag v2.0.0/tree and principles-only disposition. | `UPSTREAM-CAPABILITY-DELTA.md`; `UPSTREAM-DELTA.json` | REMEDIATED |
| Exact-byte contamination scan not recorded | Low | Added verification assertion for no byte-identical regular file between project and upstream exact tree, with explicit exclusions for empty files and hash collision interpretation. | `P-16-VERIFICATION.json`; `P-16-EVIDENCE.md` | REMEDIATED / VERIFIED |
| Workspace not a Git worktree limits changed-path proof | Low | Retained the limitation; use explicit P-16 path inventory plus before/after runtime/dist byte aggregates. No claim of Git-diff completeness is made. | `P-16-VERIFICATION.json`; `P-16-EVIDENCE.md` | MITIGATED / truthful limitation |
| Final consistency review found ambiguous artifact-location wording | Low | Split the P-16 deliverable sentence so 13 evidence files are explicitly under `evidence/p16/` and the five governance/handoff candidates are explicitly named at repository root. | `PLAN.md` | REMEDIATED / CONFIRMED CLOSED |
| Final G-01 review found normalized supplemental-context class ambiguity | Low | Made the ledger use rule explicitly include `supplemental-abstract-*` as abstract context only and state that its prose/expression remains excluded. | `UPSTREAM-FULL-RANGE-LEDGER.json` | REMEDIATED / CONFIRMED CLOSED |

## 3. Orchestration and independence record

- `engagement_mode`: P-16 remediation and gate-readiness evidence preparation.
- `prior_advisory_involvement`: primary agent authored the initial P-16 candidate and the remediation; therefore self-review risk is material.
- `self_review_risk`: High for gate recommendation if assessed only by the authoring agent.
- `independence_threat`: reviewers share the workspace and project context but are instructed to use fresh-context read-only review and not edit artifacts.
- `safeguards`: three separate review roles; exact file/hash packet; read-only reviewer instructions; no self-PASS; owner retained and exercised gate authority under D-047.
- `reviewer_independence`: agent review is an independent technical challenge within the collaboration system, not external professional assurance; owner approval is separately attributable to Tran Ngoc Thien.

## 4. Scope integrity

Remediation changed only root governance/handoff and `evidence/p16/`. It did not edit `thien-skill-creative-diagram/`, `dist/`, v1.0.0 golden/benchmark bytes, legal/brand bytes, publication mirror, Git tag or GitHub Release. No HTML/gallery, build, commit, push, tag or release action was performed.

## 5. Final independent agent review and next decision

Three read-only agent roles completed final review and post-Low delta confirmation:

- G-01/provenance: zero Critical/High/Medium/Low; recommends `READY` for owner decision.
- G-02/product-architecture-test: zero Critical/High/Medium/Low; recommends `READY` for owner decision.
- Cross-document consistency: zero Critical/High/Medium/Low; recommends `READY` for owner decision.

This is technical challenge evidence, not external assurance. Tran Ngoc Thien subsequently approved `G-01@1.5.0`/`G-02@1.5.0` `PASS` and P-16 closure under D-047 on 2026-08-23. P-17 remains unauthorized.
