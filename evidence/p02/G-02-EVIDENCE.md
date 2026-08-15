# G-02 evidence record

**Gate:** G-02 — Product, architecture and test contract lock  
**Prepared:** 2026-08-15  
**Gate result in `PLAN.md`:** `PASS`  
**Disposition:** contract set approved by the owner; owner designated the current architecture/IR/security technical review as sufficient.

## 1. Artifact set

| Artifact | SHA-256 | Purpose |
|---|---|---|
| `PRODUCT-SPEC.md` | `fb9c9cf550f0187000d8baf52cf9f1ff724f88f5d461a0e57915564a3348b971` | approved product, dials, output/fallback, motion and failure contract |
| `REQUEST.schema.json` | `b884ecc3543cda6722a3671e279b279808461bcc13447510ea44d784d86b66f8` | approved strict public request schema |
| `ARCHITECTURE-IR-CONTRACT.md` | `bcc2a5de095037a094fc2fd1c5fe9e375d2d076a3be78c2f98dd8471184b08af` | approved provider-neutral component boundaries and semantic invariants |
| `SEMANTIC-IR.schema.json` | `748f9668b53b2f42fcaa31ee1ed2b74b039b902e13a10df6d0335bd59c5a2c81` | approved machine-readable common semantic IR |
| `DESIGN-CONTRACT.md` | `36178574aef4d4b4d5c4085dc2b022dc1284a27e4114aa41efa12dc54d02b444` | approved hierarchy, canvas, typography, color, connector, complexity, accessibility and quantitative rules |
| `SECURITY-FIDELITY-CONTRACT.md` | `9f3f8409cd34ebed432676f48b32c341f03578141ae52b28bdd1c114c225e026` | approved untrusted-input, resource-cap, escaping and fidelity contract |
| `TEST-CONTRACT.md` | `6b86af372a3ed877596008d8c1b44e9d40c4a87879d79591480033a137240e64` | approved behavior/failure/test mapping and 27-type capability coverage |
| `SURFACE-SUPPORT-MATRIX.md` | `69a826cf6b9c5e6324b3ce77193301e03b05a1517d1ffa6090e80c1dc7e237b7` | approved surface × artifact × install × trigger × output × fallback × status matrix |
| `OFFICIAL-EVIDENCE.md` | `63c513008f88bde321399e396f719cc68f2b82f47d5c853c79ef9358b1ddd9f5` | current official Agent Skills, Claude, OpenAI and W3C evidence |
| `BENCHMARK-MANIFEST.md` | `333afc1b66c238e41276274dfc4317a1b1d472e27b0a9be0bdfd38073cbebc0b` | approved E2 case inventory, must-pass reference and scoring contract |
| `QA-ASSET-RECORD.md` | `0d44ab4ed66ba01621d578f8e9c499ca82407574685e07027e43e9cb296d2c74` | QA-only custody, provenance and package exclusion rules |
| `qa-only/REF-SWIMLANE-CASH-RECEIPTS-001-r2.png` | `a7dfa484b5d324dcb4269aec5dcae68154dec1947ab1b78c75b12f11a4fb6113` | owner-authorized QA-only benchmark source; prohibited from packages |

## 2. Gate assertion review

| G-02 condition | Evidence | Review |
|---|---|---|
| product input/output/dials/errors/out-of-scope | product spec plus request schema | satisfied; owner approved values on 2026-08-15 |
| design hierarchy/grid/type/color/connectors/complexity/responsive/accessibility | design contract | satisfied; modes and numeric thresholds approved |
| provider-neutral router/IR/renderer/validator/overlay architecture | architecture contract plus IR schema | satisfied; current technical review accepted by owner |
| all input/import treated as untrusted data | security/fidelity contract | satisfied; ceilings and technical review approved |
| complete surface matrix with status | surface matrix and official evidence | satisfied; owner approved statuses and conditional-evidence rule |
| benchmark input/type/assertions/dials/hard failures/rubric | benchmark manifest and QA-only R2 source | satisfied; manifest/rubric/custody approved |
| public behaviors map to expected result/failure/test | test contract, product failure table and security threat mapping | satisfied |
| no implementation before contract lock | workspace file inventory | satisfied; only Markdown/JSON contract evidence and one explicitly QA-only PNG exist |

## 3. Verification performed

- read governance sources in the mandatory order and applied only authorized P-02 scope;
- retained the P-01 clean-room-oriented independent-reimplementation boundary;
- re-verified platform facts against official Agent Skills, Anthropic and OpenAI documentation on 2026-08-15;
- verified applicable accessibility criteria against W3C WCAG 2.2 sources;
- `python3 -m json.tool` passed for both approved JSON schemas;
- confirmed 27 unique canonical `CAP-T01..CAP-T27` test mappings and seven semantic-pattern cases;
- confirmed 15 surface rows with explicit `conditional`/`unsupported` status and promotion evidence rules;
- inspected R2 as PNG 2096 × 1150 RGBA and verified its repository hash;
- recorded the R1/R2 hash difference without claiming byte identity;
- verified QA-only exclusion rules and absence of `SKILL.md`, runtime code, parser, renderer, platform manifest, logo/license, ZIP and Git action.

The environment does not contain a JSON Schema metaschema validator dependency. JSON syntax and contract consistency are verified; draft-2020-12 metaschema validation remains a non-blocking P-03 validation task using an already available validator or separately authorized dependency. No dependency was installed.

## 4. Approval and limits

- Owner: Tran Ngoc Thien.
- Approval date: 2026-08-15.
- Approved: P-02 defaults, visual-mode names, canvas/complexity/security limits, surface statuses and evidence rule, benchmark manifest/rubric, and QA-only R2 custody.
- Technical review: owner explicitly designated the current architecture/IR/security review as sufficient.
- Visual preference: professional/editorial clarity admired in `diagram-design` is approved only as an abstract quality outcome under D-022; no upstream expression or material may transfer.
- Result: `G-02 PASS`.
- Limit: P-03 is not authorized by this approval and remains `not-started`.

## 5. Residual non-blocking obligations

1. Re-verify mutable platform documentation and exact artifact installation at P-13.
2. Run metaschema validation when an approved validator is available.
3. P-06/P-12 must produce original fixtures/goldens and obtain their separate owner approvals.
4. P-13 package tests must prove the QA-only image and its hash are absent from every archive.
