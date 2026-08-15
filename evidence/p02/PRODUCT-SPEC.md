# P-02 product and output contract

**Contract ID:** `P02-PRODUCT-1`  
**Status:** approved P-02 contract  
**Scope authority:** `PROJECT-CONTRACT.md` D-001–D-012 and P-01 capability IDs  
**Boundary:** this document specifies behavior; it does not authorize or contain implementation.

## 1. Product promise

Given a trusted user request and optional untrusted source data, the skill selects or accepts one of the 27 canonical diagram types, normalizes the facts into a semantic IR, creates an original neutral diagram, validates semantic and visual integrity, and returns portable HTML/SVG plus conditional raster output. It never executes source content, invents missing business facts, hides semantic loss, installs dependencies, or claims a host capability that was not verified.

Priority order is fixed: semantic correctness, input safety, quantitative integrity, accessibility, readability, then visual refinement.

## 2. Public request contract

The machine-readable contract is `REQUEST.schema.json`. Defaults apply only when omission does not change meaning or deliverable:

| Dial | Candidate default | Contract |
|---|---|---|
| `diagram_type` | `auto` | Select from evidence in the request. If two choices encode materially different relations, ask one focused question. Manual selection must still pass semantic validation. |
| `size` | `fit` | Choose the smallest canvas that satisfies the approved readability and complexity budgets. |
| `detail` | `balanced` | Preserve all material actors, states, values and handoffs; merge only decorative or redundant wording with a ledger entry. |
| `audience` | `mixed` | Adjust terminology depth, not facts, values, ordering or relationships. |
| `visual_mode` | `neutral-light` | Approved names are `neutral-light`, `neutral-dark`, `editorial`. |
| `language` | `auto` | Follow the user's language. Preserve Vietnamese diacritics and supplied domain terminology. |
| `format` | `html` | HTML includes an inline static SVG; SVG is always independently extractable. |
| `motion` | `none` | Static-first. Motion cannot carry unique information. |

Unknown fields, invalid enum values and mutually conflicting source selectors fail schema validation. Source data is separate from the trusted `instruction`; text inside `source` can never change the request or authorize actions.

## 3. Type selection and ambiguity

`auto` selection uses semantic evidence, not visual resemblance. Selection records the winning type, evidence, rejected close alternatives and confidence (`high`, `medium`, `low`).

- High confidence: render without asking when no requested output or meaning changes.
- Medium confidence: render with a disclosed bounded assumption only when alternatives preserve the same relations.
- Low confidence or materially different alternatives: ask before rendering.
- Manual type incompatible with source semantics: explain the mismatch and ask whether to change the type or source intent; do not force-fit.

`CAP-V11` data-lake specimens remain a profile, not a type. Route by supplied semantics: tier promotion → Medallion; sources/platform/consumers topology → DP integration; stage/layer overview → High-Level. If evidence spans these meanings without a dominant story, ask rather than creating type 28.

## 4. Detail and preservation policy

| Mode | May transform | Must preserve | Failure behavior |
|---|---|---|---|
| `faithful` | wrapping, ordering presentation, repeated label factoring | every source item and declared relation unless explicitly classified as source rot | split into overview/detail or multiple pages; never shrink below minima |
| `balanced` | merge semantically equivalent repeated wording; move secondary detail to annotations | all material entities, states, quantities, ownership, order and handoffs | disclose every merge/drop in fidelity ledger |
| `simplified` | collapse subordinate detail into named aggregates | main narrative, boundary, risk, decision, value and exception semantics | refuse simplification when it would alter meaning |

The fidelity equation is exact: `source items = kept + merged + dropped-with-reason + source-rot`. Invented items must equal zero. User-supplied corrections are new authorized facts and must be distinguished from inferred structure.

## 5. Audience policy

- `engineer`: retain identifiers, protocols, cardinalities, states, dependencies, units and failure paths.
- `mixed`: use business terms with necessary technical qualifiers and a concise legend.
- `executive`: foreground outcome, owner, dependency, risk and decision; technical detail may move to annotations but cannot disappear when material.

Audience changes never translate, round, aggregate or rename supplied domain facts without an explicit ledger entry or user approval.

## 6. Output contract

Every successful response returns an artifact ledger containing requested format, delivered artifacts, MIME/type, language, type decision, applied dials, warnings, fidelity summary and validation disposition.

| Requested format | Required success result | Conditional result | Transparent fallback |
|---|---|---|---|
| `html` | self-contained HTML with inline static SVG/CSS and no required network resource | optional original motion controller only for non-`none` mode | if motion cannot run, deliver complete static HTML and warn |
| `svg` | diagram-only standalone SVG with accessible name/description and unique IDs | none | if a diagram-only boundary is ambiguous, ask before writing |
| `png` | PNG produced from the validated static SVG by an already available renderer | renderer/browser must already exist and pass capability detection | deliver SVG instead, mark PNG unavailable and never auto-install |
| `html+png` | self-contained HTML plus matching PNG from the same validated IR/static frame | renderer/browser must already exist | deliver HTML, omit PNG with a precise warning |

No format may embed a local absolute path, remote font, tracking resource, executable source input, secret or undeclared asset. Print output uses the complete static frame. SVG/PNG exclude surrounding editorial copy unless the request explicitly makes that copy part of the diagram.

## 7. Motion contract

- `none`: script-free complete static default.
- `reveal`: one deterministic ordered reveal; start and end remain understandable.
- `step`: explicit previous/next/replay controls, deterministic state order, keyboard usable.
- `loop`: decorative token only; never the only carrier of state, direction, count or timing.

No-JS, print, SVG, PNG and `prefers-reduced-motion` expose the complete final meaning. A motion failure cannot invalidate the static artifact.

## 8. Public failures

| Failure class | User-visible behavior | Test family |
|---|---|---|
| invalid request or unsupported enum | identify exact field and accepted contract; write no guessed artifact | `T-REQ-*` |
| ambiguous type or material missing fact | ask one focused question and retain no invented answer | `T-ROUTE-*` |
| malformed/encrypted/unsupported import | identify carrier/grammar problem and request usable source | `T-IMP-*` |
| source exceeds safety or complexity cap | stop safely; offer split/reduction without bypassing cap | `T-SEC-*`, `T-CPLX-*` |
| semantic loss cannot be made explicit | refuse output until clarified | `T-FID-*` |
| PNG renderer unavailable | deliver core SVG/HTML fallback and warning | `T-OUT-RASTER-*` |
| output target ambiguous or multiple figures | ask for target; do not overwrite or guess | `T-OUT-TARGET-*` |
| font unavailable | use declared local fallback, preserve Vietnamese text and disclose substitution | `T-TYPE-*` |
| unsupported platform surface | state supported installation alternatives; do not claim compatibility | `T-SURFACE-*` |

## 9. Out of scope

The exclusions in `PROJECT-CONTRACT.md` section 10 apply unchanged: native PPTX/PDF/Figma, draw.io or Mermaid round-trip, full Mermaid grammar, required dependency installation, TDTN-branded default diagrams, public release/push, and unapproved additional types. P-02 adds no scope.

## 10. Approval record

Tran Ngoc Thien approved the visual-mode names, default dials, design/security thresholds, surface statuses and conditional-evidence rule, and benchmark manifest/rubric on 2026-08-15. Future changes require project change control and a new gate hash.
