# P-16 product, architecture and test contract delta

**Contract ID:** `G02-1.5.0-DELTA-CANDIDATE`  
**Target:** `1.5.0` source/gallery only  
**Base contract:** approved P-02 `1.0.0` packet, hash-bound by `G02-1.5.0-CONTRACT-MANIFEST.json`  
**Status:** candidate; owner and technical approval required; implementation remains unauthorized

## 1. Contract composition

The exact `G-02@1.5.0` candidate is the immutable P-02 packet plus this version-scoped delta and the other P-16 files named in `G02-1.5.0-CONTRACT-MANIFEST.json`. P-02 files are not edited because they are historical approved evidence for v1.0.0.

Rules not expressly amended here are inherited unchanged, including priority order, input safety, fidelity equation, output/fallback behavior, design system, accessibility thresholds, security caps, motion, platform support statuses and benchmark scoring.

## 2. Product amendments

The first sentence of P-02 product promise is amended for the candidate as follows at the requirement level:

- selection is from 39 canonical types, not 27;
- `CAP-T28..T39` and `CAP-V17..V20` are in target scope;
- the public request candidate is `REQUEST-1.5.schema.json` with `schema_version = 1.5`, 39 canonical enum values plus `auto`, and optional explicit `variant_ids` for the four new capabilities;
- an explicit new capability is valid only with its parent or `auto`: Dumbbell→Bar, Slopegraph/Ridgeline→Line, Bubble→Scatter;
- routing distinguishes conceptual/logical `er-data-model` from physical `database-schema` and does not create types 40–43;
- low-confidence or materially different selection still asks one focused question rather than guessing;
- output remains portable HTML/SVG with conditional raster fallback; gallery HTML is QA-only evidence, not a new public output/package promise.

Out of scope remains unchanged except that the previously unapproved additional types are now limited to types beyond the exact 39 target. New platform surfaces, import grammar, onboarding, network resources, packaging and release remain out of scope.

## 3. Architecture and IR amendments

The approved router → normalized IR → renderer → validator → platform-overlay architecture is inherited. The candidate machine-readable IR is `SEMANTIC-IR-1.5.schema.json`.

Required architecture changes for a separately authorized P-17 are:

1. Router registry: 39 canonical IDs; `CAP-V17..V20` remain variants with parent compatibility checks.
2. IR type enum: 39 exact values; schema version `1.5`.
3. Quantitative IR:
   - Sankey edges use direct `amount` and `unit` fields;
   - Bubble observations use direct `x_value`, `y_value`, `size_value`, `size_unit` fields;
   - Ridgeline observations use `distribution_samples` plus required structured `distribution` metadata: method, common domain, ordered bin/sample-grid edges, bin count, explicit bandwidth/null, global-max amplitude normalization and shared-domain/shared-bin flags;
   - Treemap leaf nodes bind to `parent_group_id`; every quantitative hierarchy group carries `declared_total` and `unit` for reconciliation;
   - Polar uses angular/radial axes; Bubble may use the `size` dimension.
4. Structured semantics:
   - UML/physical schema nodes use typed `members` and column/member endpoints;
   - Deployment uses `placement`;
   - Kanban uses `work` plus group WIP limit;
   - User journey uses `journey`;
   - Wardley uses normalized `strategy` coordinates;
   - Story map uses `story` and release-slice metadata; an unassigned story uses `release_slice = null` together with `cut_status = unassigned`;
   - a physical database `index` member carries ordered `indexed_member_ids` and explicit `index_unique`; array order is index-column order;
   - Fishbone may classify cause groups explicitly.
5. Type validators, not JSON structure alone, enforce conservation, parent/variant compatibility, hierarchy, ordering, area/scale integrity and type-specific cardinality.
6. Renderer receives only validated IR and must not infer missing business facts or execute source content.

The security/fidelity contract is unchanged and applies to all new fields. Every value remains untrusted content and must be escaped for its output context. Additional nested fields count toward existing depth/size caps; no network, execution or dependency-install permission is created.

## 4. Routing and test-family amendments

P-02 routing ranges `01..27` become `01..39` for the target candidate. Existing IDs and results remain stable; new IDs append without renumbering.

### 4.1 Normative numeric and boundary policy

The following rules are the single source of truth for all P-17 validators and P-18/P-19 quantitative assertions. Other P-16 files reference this section instead of redefining tolerances.

**Numeric equality and units**

- Source lexical numbers are preserved in the accessible data ledger. Semantic arithmetic uses decimal values; where a binary floating-point implementation is unavoidable, equality passes only when absolute error is at most `E(expected) = max(1e-12, 1e-9 × max(1, |expected|))`.
- Unit strings are normalized only by Unicode NFC and trimming outer whitespace, then compared case-sensitively. There is no implicit conversion. A mismatch is a hard failure requiring corrected input or an explicit future conversion contract; P-17 may not invent a factor.
- Missing means absent or JSON `null`; `NaN`, infinities and numeric strings are invalid quantitative values. A value of zero is not missing.

**Source-to-SVG geometry tolerances**

- coordinate/end-point placement: absolute error `≤ 0.5 CSS px` against the deterministic expected coordinate;
- length, band width and dumbbell-gap ratios: absolute error `≤ 0.5 CSS px` **or** relative ratio error `≤ 1%`; an expected zero must render zero data-bearing length/width;
- area-encoded ratios for Treemap and Bubble: relative area-ratio error `≤ 2%`; an expected zero must render zero data-bearing area;
- visible hit targets, labels or zero locators may aid access but must be marked non-data-bearing and cannot be counted as quantitative geometry.

**Per-capability zero/negative/missing and conservation rules**

| Capability | Locked policy |
|---|---|
| Polar | Radius values must be finite and non-negative. Zero stays on the declared radial baseline. Missing creates a disclosed gap and accessible missing entry; it is never coerced to zero or interpolated. Radius geometry uses the length tolerance above. |
| Treemap | Leaf values and declared group totals must be finite, non-negative and unit-compatible. Missing quantitative leaves/totals are hard failures. Zero leaves remain in the accessible hierarchy but receive zero data-bearing area. Each group's child sum must equal its `declared_total` within `E`; leaf-parent bindings must form one rooted acyclic hierarchy. Area ratios use the 2% tolerance. |
| Sankey | Edge amounts must be finite and non-negative; missing amount is a hard failure. Zero flows remain in the ledger but receive zero data-bearing band width. Every non-source/non-sink node must conserve same-unit incoming/outgoing totals within `E`; mixed units are a hard failure. Band ratios use the 1%/0.5 px rule. |
| Dumbbell | Exactly two finite values per category are required. Negative and zero endpoints are allowed only on one declared shared linear domain that contains both; a domain crossing zero shows a zero reference. Missing endpoint is a hard failure. Signed gap is `second − first`; endpoints use 0.5 px and gap ratios use 1%/0.5 px tolerance. |
| Slopegraph | Exactly two finite states per series are required. Negative and zero values are allowed on a declared shared unit/domain; missing endpoint and unit mismatch are hard failures. Direction, rank, tie and crossing are computed from source values; endpoints use 0.5 px tolerance. |
| Bubble | `x_value`, `y_value` and `size_value` must be finite. Missing any field is a hard failure. Negative size is a hard failure; zero size stays in the accessible table and receives zero data-bearing area plus an optional non-data-bearing locator. Negative x/y values are allowed only when their declared axes contain them. Bubble **area** ratios use 2% tolerance. |
| Ridgeline | Samples must be finite, non-missing and inside one declared common domain; negative samples are allowed when inside that domain, but negative derived density is a hard failure. All series use identical strictly increasing `bin_edges`, `bin_count = len(bin_edges) − 1`, `shared_domain = true`, `shared_bins = true`, and `amplitude_normalization = global-max`. Histogram bins are `[edge_i, edge_i+1)`, with the final bin right-closed, and density is `count / (sample_count × bin_width)`. Gaussian KDE is allowed only with a supplied `bandwidth > 0` and uses `f(x) = Σ exp(-0.5 × ((x − sample)/bandwidth)^2) / (n × bandwidth × sqrt(2π))`; automatic bandwidth selection is forbidden. Display amplitude is divided by the maximum derived density across all series on the common grid. Peak/amplitude ratios use 1%/0.5 px tolerance. |

**Structural hard rules closing schema/semantic boundaries**

- Story map: `release_slice = null` is valid only with `cut_status = unassigned`, and `cut_status = unassigned` requires `release_slice = null`; non-null release slices use only `above`, `below` or `at`.
- Database schema: every `member.kind = index` requires a non-empty, duplicate-free ordered `indexed_member_ids` list referencing column members of the same table and an explicit `index_unique` boolean. Reordered IDs represent a different physical index. A missing/foreign/non-column reference is a hard failure.
- Treemap: every quantitative leaf has exactly one `parent_group_id`; every non-root group has exactly one valid `parent_group_id`; group `member_ids` and child parent bindings must agree exactly.

### 4.2 Stable test identifiers and coverage

Every canonical row has immutable tests `T-TYPE-NN-POS-01`, `T-TYPE-NN-BOUND-01`, `T-TYPE-NN-HARD-01`, `T-TYPE-NN-RENDER-01` and `T-TYPE-NN-A11Y-01`; quantitative rows add `T-QUANT-TOKEN-QUANT-01`. Every variant row has the same suffixes under `T-VAR-CAP-VNN-*`, plus `T-VAR-CAP-VNN-HARD-PARENT-01`. Further cases append `-02`, `-03`, and so on; IDs are never repurposed or renumbered.

| New capability | Required test family | Minimum semantic/quantitative assertions |
|---|---|---|
| `CAP-T28` Polar | `T-TYPE-28-*`, `T-QUANT-POLAR-*` | cyclic category order, angular/radial axes, exact radius value/domain/unit, zero/missing handling |
| `CAP-T29` Treemap | `T-TYPE-29-*`, `T-QUANT-TREEMAP-*` | rooted hierarchy, leaf/parent sum reconciliation, area proportionality, zero/missing policy |
| `CAP-T30` Sankey | `T-TYPE-30-*`, `T-QUANT-SANKEY-*` | stage/endpoints, non-negative edge amount/unit, internal flow conservation, band-width proportionality |
| `CAP-T31` Fishbone | `T-TYPE-31-*` | exactly one effect, cause category membership, convergence direction, no causal overclaim |
| `CAP-T32` Wardley map | `T-TYPE-32-*`, `T-QUANT-WARDLEY-*` | bounded evolution/value-chain coordinates, dependency endpoints, axis disclosure |
| `CAP-T33` Kanban | `T-TYPE-33-*` | state/column/order, WIP count and limit, blocked non-color encoding |
| `CAP-T34` User journey | `T-TYPE-34-*`, `T-QUANT-JOURNEY-*` | stage/action/touchpoint order, declared sentiment scale/bounds, accessible alternative |
| `CAP-T35` Deployment | `T-TYPE-35-*` | zone/host/artifact containment, replicas/ports, runtime edge correctness |
| `CAP-T36` Dependency graph | `T-TYPE-36-*` | dependency endpoint, fan-in/rank, cycles/SCCs, disconnected components |
| `CAP-T37` UML class | `T-TYPE-37-*` | attributes/operations, typed relationship, multiplicity/visibility/signature |
| `CAP-T38` Story map | `T-TYPE-38-*` | backbone/story order, release-slice/cut membership, unassigned-story handling |
| `CAP-T39` Database schema | `T-TYPE-39-*` | table/column/type/constraint/index, column-level FK, physical-vs-ER routing |
| `CAP-V17` Dumbbell | `T-VAR-CAP-V17-*`, `T-QUANT-DUMBBELL-*` | exactly two values/category, shared domain, exact gap, baseline exception |
| `CAP-V18` Slopegraph | `T-VAR-CAP-V18-*`, `T-QUANT-SLOPE-*` | exactly two states/series, direction, rank, crossings/ties, shared scale |
| `CAP-V19` Ridgeline | `T-VAR-CAP-V19-*`, `T-QUANT-RIDGE-*` | shared domain/bin/sample conservation, disclosed amplitude normalization, non-negative density |
| `CAP-V20` Bubble | `T-VAR-CAP-V20-*`, `T-QUANT-BUBBLE-*` | x/y/size count and units, area proportionality, size legend, non-positive/missing policy |

Every row requires the stable positive, boundary, hard-failure, accessibility and later render IDs above, an original fixture per applicable case, and direct semantic assertions. `CAP-V17..V20` also require the named parent-compatibility hard-failure test. No upstream specimen is a fixture, expected output or golden.

## 5. Coverage and combination amendments

- Canonical semantic/route coverage is exhaustive at 39/39.
- New capability coverage is exhaustive at 4/4.
- Existing P-01 capability classes remain exhaustive under their approved rules.
- Pairwise reduction applies only to cross-dimensional dials after every type/capability and each value has a direct test.
- Security, fidelity, type invariants and quantitative integrity are never pairwise-reduced.
- P-17 contributes implementation readiness/evidence for `G-04@1.5.0`; it does **not** complete or retroactively contribute to `G-02@1.5.0`. G-02 must be approved in P-16 before P-17 can start.

## 6. Gallery and pilot amendment

The exact P-18 candidate case set, data/assertion boundary and inherited scoring rubric are locked in `PILOT-GALLERY-CONTRACT.md`. Gallery custody/count/originality are:

- P-18: 12 families × three modes = 36 standalone HTML plus non-counted index/contact sheet;
- P-19: 39 canonical × three = 117 plus four capabilities × three = 12; total minimum 129 standalone HTML;
- all files are QA-only/non-package, self-contained and independently authored;
- existence is not approval; owner visual approval binds an exact manifest/hash before expansion;
- zero hard failure is mandatory; visual score cannot offset semantic, security, quantitative, geometry or accessibility failure.

## 7. G-02 candidate acceptance

`G-02@1.5.0` is ready for owner/technical decision only when:

- both candidate JSON schemas are syntactically valid and enumerate exactly 39 canonical types;
- capability/provenance and test mappings cover 12 additions plus four variants;
- exact inherited and delta files are hash-bound in the contract manifest;
- platform status is explicitly inherited with no promotion;
- the exact pilot case set/rubric and owner workflow are accepted;
- no runtime/gallery/package/release work has started.

Meeting these document checks does not self-pass the gate. Owner approval remains necessary for product/test/pilot scope; technical review remains necessary for architecture/security/testability.
