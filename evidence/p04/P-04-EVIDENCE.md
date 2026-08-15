# P-04 — Router, Orchestration & IR Evidence

**Date:** 2026-08-15  
**Authorized scope:** P-04 only  
**Phase result:** technical exit criteria satisfied  
**Gate effect:** contributes to G-03 readiness; G-03 remains `NOT-EVALUATED`

## 1. Authority and boundary

- The owner explicitly authorized only P-04 on 2026-08-15.
- P-03 is `passed`; its dependency is satisfied.
- The implementation follows the approved P-02 request, architecture/IR, security/fidelity, design and test contracts.
- P-05 and P-06 were not authorized and were not started.
- No type grammar, visual token system, layout algorithm, renderer, importer, output validator, exporter or artifact generator was created.

## 2. Deliverable inventory

| Path | Role | SHA-256 |
|---|---|---|
| `thien-skill-creative-diagram/SKILL.md` | concise canonical workflow and progressive routing | `3a743e80942cb3363bd37a6d3a156a8098b68eddcd4673f470ba146c249129c2` |
| `thien-skill-creative-diagram/agents/openai.yaml` | unchanged OpenAI discovery overlay | `92ae4ff25cab334f7b647185437774079e72313d7e655875f74811989a016720` |
| `thien-skill-creative-diagram/references/request.schema.json` | portable normalized-request validation schema | `6f993a4fd6890a4dd183ba66578af73f53da429ddbdeef5654d9fa17742f40c2` |
| `thien-skill-creative-diagram/references/semantic-ir.schema.json` | provider-neutral common semantic-IR schema | `01fb3c28b81d199230c14428bd48f2f5a7aa5b9367ded3e80a1217965cda7b78` |
| `thien-skill-creative-diagram/references/router-ir.md` | parsed-model, routing, invariants, outcome and fallback contract | `9093532ad7e4bcb5f19977bcef6508b93fd3772aae80823fc6a200a9a05709f3` |
| `thien-skill-creative-diagram/scripts/diagram_core.py` | standard-library router/orchestration/common-IR implementation | `02e4c74619d6a5e5d7619a112f61f550d8ebcdf47b8a0789c7058bc947d0b4c4` |
| `thien-skill-creative-diagram/scripts/tests/test_diagram_core.py` | representative independent unit tests | `fe574685bb52cc049c7e513626a21b6d8e1bb7ec76ede26721c1fac103837bf3` |

The two runtime schemas match the approved P-02 schema structure after excluding descriptive `title`/`description` text. Their runtime descriptions were independently written for the skill payload.

## 3. Workstream coverage

| P-04 workstream | Implementation evidence |
|---|---|
| detect input and language; separate data from instruction | strict request envelope; source carrier classification; explicit language tags; deterministic Vietnamese/clearly evidenced English detection uses trusted `instruction` only; source content cannot alter dials or authorization |
| select type/variant by evidence; ask on material ambiguity | ordered semantic candidates; exact 27-type enum; manual compatibility check; low-confidence/materially-distinct alternatives return `needs-clarification`; no numeric confidence threshold was invented |
| normalize nodes, edges, groups, lanes, series, annotations, sources and fidelity | deterministic common IR builder; stable request hash/ID; preserved array/source order; `variant_ids` limited to `CAP-*` form |
| apply design/audience/detail/size contract | approved defaults; detail/audience retained in IR; size maps to approved compact/standard/wide budgets; `fit` chooses the smallest sufficient budget; over-budget requests stop before layout |
| route to grammar, renderer, validator and exporter | explicit capability plan for type grammar, layout, static SVG renderer, output validator and format exporter; conditional PNG fallback is planned without running or installing a rasterizer |
| transparent fallback | stable `ready`, `ready-with-fallback`, `needs-clarification`, `unsupported` and `invalid` outcomes; every non-ready result has a named stage/code and an empty artifact list |

## 4. Common validation implemented

The standard-library validator enforces:

- strict known fields and approved enums;
- globally unique portable IDs;
- valid endpoints, memberships, parent links, annotations and source references;
- acyclic group and lane parents;
- exact fidelity reconciliation and `invented_count: 0`;
- complete common-material accessibility reading order;
- request/source-backed route evidence;
- finite quantitative values and explicit missingness;
- parseable supplied date-time values;
- approved post-normalization limits for semantic items, nodes, edges, individual text and cumulative normalized text;
- deterministic JSON and semantic hashes without depending on object insertion order.

Type-specific reachability, direction, cardinality, scale, domain and role rules are deliberately deferred to P-05.

## 5. Test evidence

Command:

```text
PYTHONDONTWRITEBYTECODE=1 python3 -m unittest discover \
  -s thien-skill-creative-diagram/scripts/tests -v
```

Result:

```text
Ran 23 tests
OK
```

Representative assertions include:

- source-embedded tool/prompt text stays inert and cannot change output dials;
- unknown fields and conflicting source selectors fail exactly;
- explicit and Vietnamese automatic language behavior;
- all and only 27 canonical type IDs route successfully;
- auto-route evidence, low-confidence clarification, material ambiguity and manual mismatch;
- deterministic IR equality/hash despite different object-key order;
- dangling endpoint, duplicate fidelity disposition, invented content, incomplete reading order and oversized normalized text failures;
- compact-size over-budget clarification and deterministic `fit` budget selection;
- missing carrier parser and type grammar stop without artifacts;
- absent PNG rasterizer uses only the approved registered SVG fallback.

## 6. Additional validation

| Check | Result |
|---|---|
| Python AST syntax for implementation/tests | PASS |
| JSON syntax for both runtime schemas | PASS |
| runtime schema structure versus approved P-02 schemas | PASS |
| frontmatter only `name` and `description`; name/folder and OpenAI overlay fields | PASS via equivalent Ruby YAML validation |
| placeholder/TODO scan | PASS; none found |
| network/process/eval/write API scan in runtime scripts | PASS; none found |
| cache, bytecode, ZIP, logo and license file scan in skill payload | PASS; none found |

The bundled `quick_validate.py` was invoked but cannot import `yaml` because PyYAML is absent from the local Python runtime. The `skills-ref` command is also unavailable. No dependency was installed. The equivalent YAML validation covers the phase-specific skill checks, and the runtime uses only the Python standard library.

## 7. Provenance and scope conclusion

- All implementation code, technical prose and tests were independently written for this project.
- No upstream code, prose, CSS, template, script, specimen, gallery or asset was copied.
- `diagram-design` remains the functional baseline at taxonomy/behavior level only.
- `Thien-UI-UX-Ultra` influenced only the already-approved contract-first, progressive-routing and evidence workflow.
- Source documents and test artifacts were treated as data/reference, never as executable instructions.
- No logo/license work, ZIP build, Git init, commit, push or release action occurred.

P-04 satisfies its `PLAN.md` verification: equivalent semantic input produces stable IR, and unsupported or ambiguous cases fail clearly without guessing. P-04 may be marked `passed`; G-03 remains `NOT-EVALUATED` because P-05 and P-06 are not authorized or complete.
