# P-22 Step 3 — pilot evidence

**Disposition:** NOT READY — GLOBAL STOP AFTER R01  
**Decision:** D-144  
**Date:** 2026-08-31  
**Target:** 2.1.0, measured against exact released OpenAI plugin 2.0.0 on Codex local

## Outcome

The planned pilot contained 20 pre-frozen explicit-activation cases: 14 layout-engine representatives, four capability profiles and two presentation profiles. R01 was the sentinel and the only case executed. Its structural verdict triggered the mandatory P-22 global stop; R02–R20 were therefore not launched.

This is not a 1/20 pass-rate claim. The phase disposition is NOT READY, the remaining 19 cases are not evaluated, and G-00…G-07@2.1.0 remain NOT-EVALUATED.

## Frozen inputs and isolation

- Exact archive: dist/thien-skill-creative-diagram-2.0.0-openai-plugin.zip
- Archive SHA-256: 65c2d6fbc33dc6d3065c5d6ae44a5b4fe02e5f7e8838b7f05eede07766124315
- Casebook SHA-256: 780bbb70ae3bf520d7023810ea350f08b1280c8789b4205d9ef3d43b61a946f9
- Roster SHA-256: 2f921c66b0c11ad6ff9c0ca84ad94a84cb69516c71f1ded0f9ade2762cc3c066
- Generator protocol SHA-256: beb5712316bfc3555d4fc01e01cbf1492803a5f9315cfb91ccb7d6272336717e

All 20 raw-prompt and invariant-oracle hashes were frozen before R01. The complete row binding is in P-22-PILOT-RECORD.json.

R01 ran in a fresh projectless Codex task, received only the exact extracted package, its raw prompt and a run-specific OS-temp output directory, and produced two immutable 0444 files. The receipt and access manifest show no network, install, connector, browser, other task or out-of-scope path use. Initial failed path probes addressed non-existent locations inside the allowed package root and caused no mutation. Provider-side cache absence is not claimed because it is not controller-observable.

## R01 evidence

| Item | Result |
|---|---|
| Expected profile / engine | architecture / topology-and-zones |
| Prompt SHA-256 | d4e3273eed381d26621044c9bb2d6abada5a97fb32d94be20b89c2dd178a8346 |
| Oracle SHA-256 | a8c2a786f5ceef99f2013fee6080f91c935ac25be9610cd69b478bf8e5abfbad |
| SVG | 10,123 bytes; f00a90c45cf1682e4e3a5e897d1c2230bc084dd1a616566e21f8ecc307a3a03e |
| Ledger | 17,229 bytes; d4107f0cc2ea97d731bee74a4a714293824052b182048b4b326084cfb7e8a6b5 |
| Corrected rendered visual | 1600×900; f0b95f650f06d6d299380a7df6a1b9f9387cd3ead7119e1cd9e164e63f878b43 |
| Structural judge | HARD-FAIL |
| Blind visual reviewer | PASS; overall 4/5 |
| Reconciliation | Global stop required; no oracle ambiguity; no evidenced isolation breach |

The structural judge found the semantic graph, topology, containment, relative placement, shape checks, connector grammar and requested content faithful. Legacy signals also converged unambiguously on architecture / topology-and-zones.

The hard failure is contractual: the schema-version-1.0 ledger does not declare selected_profile, canonical_parent or structural_override and does not bind a canonical machine-readable structural-profile record before rendering. This is failure code V21_PROFILE_LEDGER_CONTRACT_MISSING. Establishing the missing target-v2.1 binding requires remediation outside D-144, so continuing the pilot was prohibited.

The accepted blind visual review used a preinstalled AppKit renderer at the SVG's full 1600×900 viewBox. It scored recognizability 5, hierarchy 5, connector clarity 3, label legibility 5, spacing 4 and overall 4, with no serious clipping, overlap or covered label. The post-freeze comparison noted that arrowheads were not reliably visible in this PNG even though the SVG source carries marker-end on all seven edges; the blind verdict is therefore craft/recognizability evidence, not proof of arrow-direction conformance. An earlier square Quick Look thumbnail fill-cropped the 16:9 SVG; that renderer result and its review were invalidated and excluded rather than treated as an output defect.

## Owner-observed template gap

After the R01 bytes and oracle were frozen, the owner observed that the generated diagram did not follow the approved template in the skill/assets. A read-only post-freeze comparison confirmed NON-CONFORMING at the approved structural-signature level, although the output did match the broad topology-and-zones family.

The comparison excluded permitted changes to content, node count, color and font. It found these structural divergences:

- the node mark changed from inset badge plus centered title/subtitle to accent rail plus left-aligned role/title;
- the approved single/row/column child-layout grammar became converging and hub/branch sub-layouts;
- direct successors of API Gateway drifted across different ranks;
- rounded-orthogonal route construction and endpoint vocabulary changed;
- selected profile, rank/order grammar, child layout, port distribution, route family and structural override were not declared.

The approved reference used for this diagnostic was assets/diagrams/01-topology-and-zones--neutral-light.html (SHA-256 fbccfe372b9917a8679f8a295298d08ebb1e0bb576f70244e6a2992f587aa08c) with its PNG (SHA-256 5368d76841b013bcb7866a2e6e7a59701f9201126ff937823405c7ed6cf1de11).

The exact OpenAI package contains no approved diagram HTML/PNG. Its architecture reference explicitly limits itself to semantic behavior and excludes layout, visual tokens, rendering and export; its adapter binds only a broad engine/silhouette. Therefore the released package does not contain the canonical profile-level record needed to enforce the approved template's abstract placement, mark and connector grammar.

This owner observation and comparison are recorded as post-freeze diagnostic evidence. They do not alter the frozen R01 oracle or create a retroactive failure. They expose a QA coverage and product-binding gap that must be resolved under separate authorization before any later step.

## Disposition and boundaries

- R02–R20 were not run.
- R01 was not rerun and its oracle was not changed.
- No skill, reference, schema, script, test, asset, golden, package or dist byte was modified.
- No gate was passed and Steps 4–7 were not opened.
- No raw SVG, ledger, screenshot corpus or task log is retained in the repository.
- The only durable P-22 artifacts are this human summary and P-22-PILOT-RECORD.json.

The next permissible work is a separately authorized contract/QA clarification and remediation scope. Step 4 cannot begin from this disposition.
