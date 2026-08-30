# P-18R4 evidence — contract and visual-foundation relock

**Date:** 2026-08-24  
**Authority:** D-051, D-052 and D-053  
**Target:** `1.5.0`, source/gallery planning boundary only  
**Subphase result:** `passed`  
**Parent phase:** P-18 `in-progress`  
**Gate:** `G-03@1.5.0 NOT-EVALUATED`

## Outcome

P-18R4 replaced the rejected one-size-fits-all visual foundation with a locked contract for the next candidate. No renderer, runtime, gallery, package or release artifact was implemented.

Exact bindings:

- contract ID: `P18R4-VISUAL-FOUNDATION-1.5.0`;
- `P-18R4-VISUAL-FOUNDATION-CONTRACT.md` SHA-256: `addf6793a9670d5a76b48c3835f2e2e08750b0bfca7cc27b210210acaa9f95a5`;
- `P-18R4-VISUAL-FOUNDATION.json` SHA-256: `37e0c955cc814d10dc393f148a4a55c2d5ef141e547c370171d176cc2efd7be9`.

## What is locked

- The rejected P-18R3 replacement remains historical evidence and is not a golden.
- The canonical pipeline measures resolved fonts before node sizing/layout/routing; global transforms, fixed cards and character-count wrapping are retired.
- Typography precedence is explicit user font → user brand profile → explicitly requested source-font fidelity → skill default → disclosed fallback.
- Default direction is Instrument Serif for display/editorial, Geist for human-facing sans and Geist Mono for technical metadata. P-18R4 downloaded, installed and embedded no font.
- Fourteen layout engines cover exactly 39 unique canonical types and four unique capability variants.
- The eventual full matrix remains `39×3 + 4×3 = 129` standalone HTML specimens.
- The interface, primitive/node anatomy, content-fit artboard, port/obstacle routing, ≥8px label clearance, bridge/hop and uncontaminated visual-review requirements are explicit.
- All inherited semantic, quantitative, accessibility, security, standalone, provenance and D-050 visual-craft minima remain blocking.

## Verification

| Check | Result |
|---|---|
| Contract JSON parse | PASS |
| Layout-engine count | PASS — 14 |
| Canonical coverage | PASS — 39 unique; exact set equals request schema |
| Capability coverage | PASS — 4 unique |
| Full-gallery formula | PASS — 129 |
| User-font precedence/default profile | PASS |
| Only P-18R4 authorized | PASS |
| Historical manifest and 40 bound output/index/anchor hashes | PASS — zero mismatch |
| Full canonical regression | PASS — 148/148 |
| `skill-creator` quick validator | DEFERRED — available Python lacks PyYAML; no dependency installed |
| Runtime/renderer/gallery regeneration/package/`dist/`/Git/release/font-fetch boundary | PASS — none performed |

Machine-readable result: `P-18R4-VERIFICATION.json`.

## Historical limitation

A read-only check of the rejected P-18R3 generator recomputes source bundle `67db0772ebd4086c5115a6bc5236098a00b705a3ba5aefc4b2a312221c7f853b`, not its historical frozen source-bundle value `30fc0ce7c5721a21fbe42cf5dd742ef3b23895e6f45070069cfa7dc34c3388c2`. The frozen manifest SHA-256 remains `4fb00b7f1b898a4a59b6fd4092b8f15f35ddd5b4a51c14124911b42a145ed5a7`, and all 40 files it binds still match their recorded hashes.

This is recorded as `P18R4-L01` and is non-blocking for the contract-only P-18R4 result because the candidate is rejected and no regeneration/re-baselining is authorized. A future authorized candidate must start from the new P-18R4 contract and freeze a new manifest; the rejected manifest must never be edited merely to make a check green.

## Boundary and next authorization

P-18R5, P-18R6 and all P-19 subphases remain unauthorized. The next proposed step is P-18R5: implement the canonical visual kernel and exactly one `neutral-light` Swimlane anchor, then stop for owner review. It requires a separate explicit owner authorization.
