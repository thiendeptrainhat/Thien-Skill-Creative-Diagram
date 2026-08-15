# G-01 evidence record

**Gate:** G-01 — Source, taxonomy and provenance lock  
**Prepared:** 2026-08-15  
**Gate result in `PLAN.md`:** `PASS`  
**Technical disposition:** owner designated the current technical review as sufficient and approved G-01 on 2026-08-15.

## Artifact set

| Artifact | SHA-256 | Purpose |
|---|---|---|
| `SNAPSHOT-RECORD.md` | `f6544d36e078a0dae784fd1b63881df907d484b9bd79f8a2a3ee8ecea2480a6f` | immutable source snapshots, taxonomy count, specimen inventory and custody record |
| `CAPABILITY-PROVENANCE-MATRIX.md` | `62ff1bbe5513a483b80f8e932967373a38b85c1220e5e989b14e73d6757d263c` | requirement → source → independent boundary → planned test mapping |
| `PLATFORM-EVIDENCE.md` | `4a75aa8db7c9116a232a239603a671afb9d23d46296641ff0d91f12b61e2e7b6` | current official Claude/OpenAI/Agent Skills evidence inventory |
| `PROVENANCE-POLICY.md` | `6813f4bfdb02905d2443105fd40e1b4d6b6de4d0a823d5c2014bca8a8015bb55` | clean-room-oriented independent-reimplementation boundary and notice rules |
| `SOURCE-MANIFEST.schema.json` | `1dcf7e023a23197adc0c240b30fbf2459421a495d4d7442ab46a3a82e82c3ad0` | machine-readable draft schema for a single source ledger and deterministic notice projection |

## Gate assertion review

| G-01 condition | Evidence | Review |
|---|---|---|
| diagram-design commit/tag/date locked | commit `09df49d8d1a1c7fb2efdfcdc7a2a0713534350a6`, no exact tag, commit timestamp/tree/hashes in snapshot record | satisfied |
| exactly 27 canonical types; 29 not promoted | canonical `SKILL.md` table plus 27 `type-*.md`; mutable repository metadata discrepancy documented | satisfied |
| variant/specimen/pattern/import/motion classified | 97 specimens accounted for; 27 type mappings, variant, seven pattern, import, output, motion and failure sections in matrix | satisfied |
| capability → source → independent plan → test | capability matrix contains source locator, independent boundary and planned evidence for every scoped class | satisfied |
| Thien-UI-UX-Ultra snapshot and principles only | commit/tag/tree and five hashed principle/workflow files recorded; prohibited material stated | satisfied |
| official platform requirements verified | first-party Anthropic/OpenAI docs and official Agent Skills spec, verified 2026-08-15 | satisfied for P-01 inventory; support status intentionally deferred to P-02 |
| source/provenance ledger and manifest-driven notice rule | snapshot ledger, provenance policy and draft JSON Schema with exact notice projection | satisfied as P-01 design evidence |
| no upstream implementation material in workspace | file-type scan found no `SKILL.md`, HTML, SVG, CSS, JS or Python implementation file; whole-file SHA comparison found no byte-identical upstream file | satisfied |
| no absolute clean-room claim | every artifact uses the exact phrase “clean-room-oriented independent reimplementation” | satisfied |

## Verification commands and results

Read-only checks executed against the exact temporary snapshot and workspace:

- `git ls-remote ... refs/heads/main` resolved the locked full commit.
- detached exact-commit checkout reported 320 repository files and Git tree `aa59393dfabbbcbb4bcb62a7cf9f43c1ce26c9c2`.
- reference count: 27 `type-*.md` files.
- specimen count: 97 `example-*.html` files = 81 base static + 16 additional.
- capability row count checks: 27 canonical type rows and seven semantic pattern rows.
- `python3 -m json.tool evidence/p01/SOURCE-MANIFEST.schema.json` passed.
- implementation-extension scan returned no files.
- intersection of workspace and upstream whole-file SHA-256 sets was empty.

## Residual findings and limits

1. `example-datalake*` is an additional specimen family without its own canonical type reference. It remains a specimen requirement and must be mapped to an existing type before implementation; it cannot become type 28.
2. OpenAI's current official plugin documentation defines directory/marketplace distribution but does not establish a generic ZIP envelope. P-02/P-13 must resolve this with current official evidence and smoke testing.
3. Platform account, plan, admin, code-execution and beta requirements are external conditions. P-02 must encode them in the surface matrix before assigning support status.
4. Brand onboarding and named client profiles exist in the upstream 2.4 snapshot but are outside the classes locked by D-005. They were inventoried but not added to scope.
5. Platform documentation is time-sensitive and must be re-verified at P-13.

None of these findings authorizes P-02 or implementation.

## Approval state

- Technical evidence preparation: complete.
- Owner approval of G-01 scope lock: approved by Tran Ngoc Thien on 2026-08-15 through the project conversation.
- Technical review: accepted as sufficient by explicit owner designation on 2026-08-15.
- G-01 result: `PASS`; the owner separately authorized P-02 to begin in the same project decision.
