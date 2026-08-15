# G-06 — Brand, provenance and legal gate evidence

**Date:** 2026-08-15  
**Gate result:** `PASS` under D-031  
**Candidate:** `TCD-LEGAL-1.0.0-RC2`, version `1.0.0`  
**Aggregate SHA-256:** `8f16380761cd6026166daa12ee36227d96e0e3b92ce605f4d9057624de8292c6`

## 1. Approval binding

- Brand derivative selection was approved by owner Tran Ngoc Thien under D-027.
- The exact legal release candidate was approved by owner Tran Ngoc Thien under D-029.
- Tran Ngoc Thien explicitly self-identified as a Vietnamese lawyer and approved the same exact legal candidate without conditions under D-030.
- D-030 is bound to the candidate ID, version, aggregate hash and all six artifact hashes in `evidence/p10/LAWYER-APPROVAL-RECORD.json`.
- Owner Tran Ngoc Thien explicitly approved G-06 `PASS` under D-031 for the D-027 brand selection and exact D-029/D-030 legal candidate.
- The stated lawyer capacity is recorded from the user's express self-attestation. The project did not independently authenticate identity, bar admission or a digital signature.

## 2. Mandatory-condition matrix

| G-06 condition | Evidence | Result |
|---|---|---|
| logo master unchanged; source hash and AI provenance recorded | P-09 master/evidence byte identity; SHA-256 `020a47a3c831664c700c9e4491c7ae00cf5a8f330e6c3c57422ee246df56d69e`; D-016 | satisfied |
| derivative recipe/hash and mask/background/small-size tests | deterministic P-09 generator, 22/22 hash/PNG checks, contact sheet and actual-size findings | satisfied |
| owner approval of contact sheet and final derivatives | D-027; `APPROVED-BRAND-SELECTION.json` | satisfied |
| lawyer-approved logo/brand carve-out | exact lawyer-approved `LICENSE-APPLICATION.md` includes bilingual brand carve-out; D-030 binds its hash | satisfied |
| exact bilingual license name and Vietnamese priority | `LICENSE.md` and `LICENSE-APPLICATION.md`; checks V-P10-009, V-P10-010 and V-P10-014A | satisfied |
| rights only via paid order, written permission/email or commercial agreement | exact approved license candidate; check V-P10-010 | satisfied |
| Vietnamese law and competent Vietnamese court | exact approved license candidate; check V-P10-010 | satisfied |
| six legal/provenance artifacts mutually consistent | deterministic projections plus 29/29 checks; exact six-file aggregate hash | satisfied |
| lawyer sign-off bound to exact release candidate | D-030; checks V-P10-023 through V-P10-025 | satisfied |

## 3. Blocking-failure review

- Logo and third-party rights are expressly separated from the general skill/code grant.
- `NOTICE` and `THIRD_PARTY_NOTICES.md` are deterministic manifest projections and match their manifests.
- Provenance wording uses the approved description “clean-room-oriented independent reimplementation”; it does not claim absolute clean-room isolation.
- The legal wording is approved under D-030 for the exact bytes identified above.
- No legal or brand byte changed after the recorded approvals.

No G-06 blocking failure is present in the recorded evidence.

## 4. Verification snapshot

- P-09 brand phase: `passed`; 127-test regression `OK`.
- P-10 legal/provenance phase: `passed`; 29/29 focused checks and 127-test regression `OK`.
- Deterministic legal candidate check reproduces aggregate SHA-256 `8f16380761cd6026166daa12ee36227d96e0e3b92ce605f4d9057624de8292c6`.
- P-13 package construction, ZIP building, install testing, Git actions and release were not performed.

## 5. Primary evidence

| Path | SHA-256 |
|---|---|
| `evidence/p09/P-09-EVIDENCE.md` | `89ac01ae05b4ac541598510b52b486a099928215d0d10ac9462237eea4204eec` |
| `evidence/p09/APPROVED-BRAND-SELECTION.json` | `b38a922d42cb21d20e9d5bc316d0d17fe368ed6080528868a3537ab691aa2437` |
| `evidence/p10/P-10-EVIDENCE.md` | `36ec653200fe7ac588839bc684e16104474fa3d51113b889e7bcb177d91778a1` |
| `evidence/p10/LAWYER-APPROVAL-RECORD.json` | `688a588587f4458baa8386f7e6af3507fce4a1dd3f6dc2d7ede57ef701714cd1` |
| `evidence/p10/legal-candidate-build.json` | `be641233d6017ca22b8d4416df254591a2c03a345bb7bceb91128d318ee9616d` |
| `evidence/p10/verification-report.json` | `65bea1f20fc421f46b33879a748fdc953c4105c932060ddbfdf60d2dd74daee1` |

## 6. Gate boundary

G-06 is `PASS` under the owner's explicit D-031 decision. This gate result is bound to the exact brand and legal bytes identified above. It does not authorize P-13 or release; those require separate authority under `PLAN.md` and G-07.
