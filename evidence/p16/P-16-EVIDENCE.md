# P-16 — Upstream Delta & Contract Lock Evidence

**Record ID:** `P16-EVIDENCE-2026-08-22`  
**Date:** 2026-08-22 through 2026-08-23, Asia/Ho_Chi_Minh  
**Authorized scope:** P-16 only, under D-046; owner gate approval/closure under D-047  
**Phase result:** `passed` on 2026-08-23  
**Gate effect:** `G-01@1.5.0` and `G-02@1.5.0` are `PASS`; P-17 remains unauthorized

## 1. Outcome

P-16 produced and remediated a version-scoped governance/evidence/contract candidate for target `1.5.0` without changing the canonical skill, gallery, packages or release. The project keeps its existing name and ID, expands the proposed canonical taxonomy from 27 to 39, includes four new capabilities under existing parents, and stops the current target at source/gallery.

The factual snapshot manifest is `UPSTREAM-DELTA.json`. Its exact source is `diagram-design@648c2a597839301e06df1e7434a08bde9f42eed3`, resolved from `main` again on 2026-08-22. Permanent evidence locators:

- `https://github.com/cathrynlavery/diagram-design/commit/648c2a597839301e06df1e7434a08bde9f42eed3`
- `https://github.com/cathrynlavery/diagram-design/blob/648c2a597839301e06df1e7434a08bde9f42eed3/skills/diagram-design/SKILL.md`
- `https://github.com/cathrynlavery/diagram-design/tree/648c2a597839301e06df1e7434a08bde9f42eed3/skills/diagram-design/references`
- `https://github.com/cathrynlavery/diagram-design/tree/648c2a597839301e06df1e7434a08bde9f42eed3/skills/diagram-design/assets`
- `https://github.com/cathrynlavery/diagram-design/blob/648c2a597839301e06df1e7434a08bde9f42eed3/LICENSE`

## 2. Authority and scope checks

| Assertion | Result | Evidence |
|---|---|---|
| Display name and technical ID remain unchanged | PASS candidate | D-041; `PROJECT-CONTRACT.md` |
| Target maintenance version is v1.5.0 | PASS candidate | D-042 |
| All analyzed visual delta is in scope | PASS candidate | D-043; manifest sections `canonical_additions_12` and `new_capabilities_4` |
| Gallery follows the recommended QA-only model | PASS candidate | D-044; gallery contract in `PROJECT-CONTRACT.md` §3.4 |
| Current target stops at source/gallery | PASS candidate | D-045 |
| P-16 closure, without downstream phase authorization | PASS | D-047; `PLAN.md` |
| P-17/runtime or P-18/P-19/gallery work started | NO | canonical source and dist aggregate checks below |
| Package/build/Git/release work occurred | NO | no build command; `dist/` aggregate unchanged; workspace is not a Git working tree |

## 3. Delta result

| Item | Baseline P-01 | P-16 candidate | Delta |
|---|---:|---:|---:|
| Canonical visual types | 27 | 39 | +12 |
| Canonical base gallery examples observed upstream | 81 | 117 | +36 |
| New named capability families in this change | 0 | 4 | +4 |
| Shipped upstream examples for those four capabilities | 0 | 9 | +9; Dumbbell has no shipped example at this exact snapshot |
| All upstream `example-*.html` specimens | 97 | 142 | +45 |
| All upstream HTML files in `assets/` | 104 | 149 | +45 |

The exact 12 canonical additions are Polar chart, Treemap, Sankey, Fishbone, Wardley map, Kanban, User journey, Deployment, Dependency graph, UML class, Story map and Database schema.

The four capability families are:

- Dumbbell → Bar chart;
- Slopegraph → Line chart;
- Ridgeline → Line chart;
- Bubble → Scatter plot.

They are not canonical types 40–43. The target arithmetic is exactly `27 + 12 = 39`.

The complete whole-repository upstream range is 170 changed paths (`+23895/-244`) and is dispositioned path-for-path in `UPSTREAM-FULL-RANGE-LEDGER.json`; 74 paths are under `skills/diagram-design/**` and 96 are outside that pathscope. `UPSTREAM-CAPABILITY-DELTA.md` explains the 74-path skill subset and the repository-level boundary. Only the 12 canonical additions, four variants and conceptual-ER/physical-schema distinction are adopted at an abstract requirement level. Changed commands, Mermaid grammar, Korean typography, onboarding/Factory Droid, doctor diagnostics, provider manifests, scripts, templates and gallery expression are inherited unchanged at project level or explicitly excluded.

## 4. Version-scoped contract lock

`G02-1.5.0-CONTRACT-MANIFEST.json` is the frozen exact byte-bound candidate packet approved under D-047. It composes ten unchanged P-02 historical artifacts with nine P-16 delta artifacts. Its embedded pre-approval status fields remain historical candidate metadata; current gate status is recorded only in `PLAN.md` and the P-16 gate-closure records. The target additions are not inferred by reading P-02 alone.

Contract amendments include:

- `REQUEST-1.5.schema.json`: schema version 1.5, exactly 39 canonical values plus `auto`, optional explicit `CAP-V17..V20` with parent compatibility;
- `SEMANTIC-IR-1.5.schema.json`: 39-type enum, direct Sankey `amount/unit`, Bubble `x/y/size`, structured Ridgeline transformation metadata, Treemap parent/declared-total fields, database index column order/uniqueness and valid unassigned Story-map representation;
- `CAPABILITY-PROVENANCE-MATRIX.md`: requirement → exact abstract source/hash → planned independent implementation → stable test family for 12+4;
- `PRODUCT-ARCHITECTURE-TEST-DELTA.md`: routing, IR, validator, exact numeric/unit/geometry/boundary policies, stable test IDs, coverage and no-circular-gate amendment;
- `PLATFORM-SURFACE-REVALIDATION.md`: current official Agent Skills/Claude/OpenAI documentation receipt and explicit inheritance with zero support-status promotion.

P-17, if later separately authorized, implements a G-02 contract already approved at P-16 and contributes only G-04 readiness; it cannot complete G-02 retroactively.

## 5. Gallery contract candidate

The project does not copy upstream assets. It uses only the abstract fact that all canonical types are demonstrated in three static presentations and that a browsable gallery helps owner review.

The target project gallery is independently authored and QA-only:

- P-18 exact pilot candidate: 12 stable case families (8 canonical + 4 new capabilities) × 3 project modes = 36 standalone HTML, plus an index/contact sheet;
- P-19 full candidate: 39 canonical types × 3 modes = 117 HTML, plus 4 capabilities × 3 modes = 12 HTML, for a minimum of 129 standalone specimen HTML;
- modes stay `neutral-light`, `neutral-dark`, `editorial` unless the owner approves a contract change;
- every scenario, label, dataset, layout, SVG, CSS, prose and page composition must be original;
- gallery files remain under `evidence/p18/` and `evidence/p19/` and are excluded from package payload in the current scope;
- owner approval is bound to an exact manifest/hash; file existence alone does not create a golden or gate pass.

The stable case IDs, exact original data/semantics/assertions, inherited rubric hash and owner workflow are in `PILOT-GALLERY-CONTRACT.md`. D-047 approves this exact contract for later use, but P-16 creates no HTML and D-047 does not authorize P-18 execution or approve any rendered visual.

## 6. Provenance and independent implementation boundary

- The upstream repository is evidence for taxonomy, abstract behavior, inventory and failure/integrity requirements only.
- No upstream HTML, CSS, SVG, JavaScript, Python, prose, template, coordinates, example data, gallery page or pixels were copied into this workspace.
- The upstream MIT declaration is recorded, but the project's stricter D-006/D-022 independent-reimplementation policy remains controlling.
- Upstream `THIRD_PARTY_LICENSES.md` is byte-unchanged across the two snapshots, SHA-256 `22f5afcea56373e84d7f7eff93d8d4d6e4b81c5375bb1c996e78b91e53fa0b37`; no listed third-party asset/code is imported.
- `Thien-UI-UX-Ultra` and `skill-creator` influenced only workflow, progressive disclosure, design-contract discipline and evidence handling; no implementation asset was reused.
- The inherited `Thien-UI-UX-Ultra` binding remains commit `fb4e57758f525827e04004737d779f4c93b9b3a0`, tag `v2.0.0`, principles only.
- Upstream onboarding, network fonts/resources, profiles, doctor, commands/prompts and packaging changes are explicitly excluded from this target absent a new owner decision.

## 7. No-runtime/no-release evidence

Before governance/evidence edits, the sorted SHA-256 listing aggregates were:

| Scope | File count | Aggregate SHA-256 |
|---|---:|---|
| `thien-skill-creative-diagram/` excluding `.DS_Store` | 82 | `27ccde0a1b5ee97d2943fa58166f513ec697dcfbe58750c155148e0f34e4cc22` |
| `dist/` excluding `.DS_Store` | 4 | `188526fdf60b53183723bb231a6940896a42cf90db5df71094eebc66ac45c065` |

P-16 verification reproduced both aggregates after remediation, with the same file counts: canonical runtime `82`, dist `4`. No build command was used. JSON/schema/count/path/hash checks passed, the 170-entry ledger matched the pinned upstream `git diff --name-status` set exactly, `evidence/p16/` contained zero HTML files, and exact-byte contamination scanning found no byte-identical non-empty regular file between the project workspace and the exact upstream tree. Because the audit-source root is not a Git worktree, local changed-path completeness is established through the explicit P-16 path inventory plus immutable runtime/dist aggregates rather than a root Git diff. Machine-readable results are recorded in `P-16-VERIFICATION.json`.

## 8. Remediation and review separation

`REMEDIATION-REVIEW-NOTES.md` maps every initial and re-review finding to a remediation artifact. The primary agent authored both the candidate and remediation, so self-review risk is explicitly high. Three read-only agent roles completed G-01, G-02 and cross-document review plus final delta confirmation. Each reported zero remaining Critical/High/Medium/Low finding and recommended READY for owner decision. Tran Ngoc Thien then explicitly approved both gate instances and P-16 closure under D-047. Agent review remains technical challenge evidence, not external assurance.

## 9. Gate assessment and handoff

Owner approval is explicit and recorded under D-047 after the three independent agent review roles reported zero open finding:

- `G-01@1.5.0`: `PASS`; exact source/taxonomy/provenance scope approved.
- `G-02@1.5.0`: `PASS`; exact source/gallery product, architecture, test, pilot/rubric and three-mode QA-only workflow approved.
- P-16: `passed`.

Evidence of the transition is recorded in `P-16-GATE-CLOSURE.json` SHA-256 `21f8a71772c96d9ab3f4409c8d87c7dbddd966cff75d8b64c993dbde483bf081`, `G-01-1.5.0-EVIDENCE.md` SHA-256 `d2adb35d8f60d925e2869236a473f6f41a0a4161c92f79d24b97bd8af436c0d7` and `G-02-1.5.0-EVIDENCE.md` SHA-256 `ca43ab807eb6e70229b6be4ac2d6ec2b5868f526b3186240ea2652f99152830f`. D-047 explicitly withholds P-17/P-18/P-19 and all runtime/gallery/build/package/Git/release authorization.
