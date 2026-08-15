# P-02 canonical architecture and semantic IR contract

**Contract ID:** `P02-ARCH-IR-1`  
**Status:** approved P-02 contract  
**Schema:** `SEMANTIC-IR.schema.json`

## 1. Provider-neutral pipeline

```text
trusted request + untrusted source
  → request validator
  → bounded carrier parser
  → semantic normalizer + fidelity ledger
  → type/variant router
  → semantic validator
  → layout planner
  → renderer
  → geometry/accessibility/security validator
  → exporter + artifact ledger
```

The canonical core owns request semantics, parsing policy, IR, type routing, validation, layout intent, rendering and export. Platform overlays own only host manifests, UI metadata, installation notes and capability detection. An overlay cannot change semantic output, bypass validation or fork the core.

## 2. Component contracts

| Component | Accepts | Produces | Must fail when |
|---|---|---|---|
| request validator | `REQUEST.schema.json` | normalized request plus trusted-instruction boundary | schema invalid, conflicting selectors, unknown enum |
| carrier parser | bounded source bytes/text | source items with stable IDs and locators | malformed/encrypted/unsupported/over cap, executable feature required |
| semantic normalizer | source items | schema-valid IR plus fidelity entries | fact cannot be represented without invention or silent loss |
| router | normalized request and pre-layout IR | one canonical type, variants, evidence and alternatives | type ambiguity changes semantics or manual type conflicts |
| semantic validator | typed IR | invariant report | dangling IDs, invalid cardinality/order/domain, invented item, fidelity mismatch |
| layout planner | validated IR and design dials | abstract geometry plan | readability/complexity constraints cannot be satisfied |
| renderer | geometry plan and original visual tokens | HTML/SVG static frame; optional original motion layer | unsafe content, invalid geometry or missing required accessible data |
| output validator | artifact plus IR | semantic/geometry/a11y/security report | any hard check fails |
| exporter | validated artifact | requested artifacts or declared fallback | target ambiguous, rasterizer missing, output would diverge from IR |
| platform overlay | canonical package plus host facts | host manifest/installation adapter | host condition or official requirement is unverified |

## 3. IR invariants

The JSON Schema validates shape; a semantic validator later must additionally enforce:

1. all IDs are unique; all referenced node/group/lane/source IDs exist;
2. each source item appears exactly once across kept, merged, dropped or source-rot entries;
3. `invented_count` is zero;
4. edges reference valid endpoints and satisfy type-specific direction/order/cardinality rules;
5. group and lane membership is acyclic and every visible item has one unambiguous reading position;
6. chart values preserve source value, missing state, unit and domain; axes state scale and domain;
7. temporal values retain timezone or an explicit unknown-timezone marker before render;
8. `selection.evidence` refers to request/source semantics, never visual similarity with upstream;
9. every applied variant maps to a P-01 `CAP-*` ID;
10. accessible reading order covers every material rendered element once.

## 4. Type-specific validation boundary

P-02 defines common IR only. P-05 will add independent type grammars and validators for the 27 canonical types. Until then, no renderer implementation may claim type completeness.

The data-lake profile uses existing type semantics:

- Medallion for named quality tiers and promotion;
- DP integration for sources → platform → consumers;
- High-Level for stage/layer overview and cross-cutting concerns.

Mixed, ambiguous requests must be clarified or split. This mapping introduces no new canonical type.

## 5. Determinism and auditability

For equal normalized input, approved dials, version and environment capability record, IR and static SVG must be reproducible. Stable ordering uses explicit order first, then source order, then stable ID; never hash-map iteration. Artifact evidence records schema/version, normalized-request hash, IR hash, renderer/version, capability detection, warnings and validation results.

## 6. Platform overlay rules

- Provider-neutral `SKILL.md` and runtime references later contain no Claude/OpenAI-only fields.
- Claude `.claude-plugin/plugin.json` and OpenAI `.codex-plugin/plugin.json` are generated overlays, not handwritten alternate cores.
- `agents/openai.yaml` is OpenAI-only presentation/invocation metadata.
- Host-specific tool availability can only reduce optional output capability and must produce a transparent fallback.
- A surface marked `conditional` or `unsupported` cannot be promoted by runtime guesswork.

## 7. No-implementation boundary

P-02 produces schemas and testable contracts only. It does not create `SKILL.md`, parser, router, renderer, platform manifest, asset, fixture, golden, ZIP or dependency.
