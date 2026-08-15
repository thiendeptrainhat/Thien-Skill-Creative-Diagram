# P-10 — License, notices and provenance evidence

**Date:** 2026-08-15  
**Authorized scope:** P-10 only; P-13 prohibited  
**Phase disposition:** `passed`  
**Gate disposition:** G-06 `PASS` under D-031

**Owner approval:** approved under D-029 on 2026-08-15 for exact candidate `TCD-LEGAL-1.0.0-RC2`, version `1.0.0`, aggregate SHA-256 `8f16380761cd6026166daa12ee36227d96e0e3b92ce605f4d9057624de8292c6`.

**Vietnamese-lawyer approval:** Tran Ngoc Thien explicitly self-identified as a Vietnamese lawyer and approved the same exact candidate without conditions under D-030 on 2026-08-15. The project records that professional capacity from the user's express self-attestation; it did not independently authenticate identity, bar admission or a digital signature.

## 1. Exact candidate outcome

Owner decision D-028 resolved both material P-10 questions. The resulting legal release candidate is:

- Candidate ID: `TCD-LEGAL-1.0.0-RC2`
- Version: `1.0.0`
- Aggregate SHA-256: `8f16380761cd6026166daa12ee36227d96e0e3b92ce605f4d9057624de8292c6`
- Status: owner- and Vietnamese-lawyer-approved exact candidate; G-06 `PASS`; not release-authorized

The locked template source has SHA-256 `ced33214d371fabe382d3ca303042af7219ad96fb98acdd1b858d0d89478d4b5`. D-028 authorizes only `SKILLS` → `SKILL` in both bilingual title lines. The resulting `LICENSE.md` has SHA-256 `64d88634fe7ad212049799d7febdbe574bd64574c1f75cfe065f2952a2906f31`; no other template clause is changed.

## 2. Work completed within P-10

- `LICENSE.md` uses the exact singular license name and retains the approved bilingual template body.
- `LICENSE-APPLICATION.md` identifies the skill/version, Vietnamese-prevails rule, private repository intent, three granting mechanisms, professional limits and exact-hash review condition.
- Skill/code rights are separated from TDTN logo, crest, marks, identity, goodwill and third-party material.
- `SOURCE_MANIFEST.json` is the machine-readable source ledger under the P-01 clean-room-oriented independent-reimplementation boundary.
- `ASSET_MANIFEST.json` records the immutable logo master, recipe, hashes, D-027 approval and D-028 package scope.
- `NOTICE` and `THIRD_PARTY_NOTICES.md` are deterministic manifest projections.
- `legal-candidate-build.json` binds the exact six files to RC2/version/aggregate hash.
- `LAWYER-REVIEW-PACKET.md` provided the exact review questions and sign-off binding without transmitting the candidate externally.
- `LAWYER-APPROVAL-RECORD.json` binds D-030 to the same candidate ID, version, aggregate hash and six artifact hashes.
- Current-law background was checked only against official Vietnamese state publication systems and recorded in `OFFICIAL-LEGAL-SOURCES.md`.

The legal/IP workflow controlled source hierarchy, IP-asset separation, ownership caution, bilingual alignment, exact-candidate review and non-overstatement. The canonical-skill workflow kept the legal bundle aligned with one canonical source and the future three-package architecture. No code, prose, CSS, template, script, specimen or asset was copied from `diagram-design` or `Thien-UI-UX-Ultra`.

## 3. Exact six-file hashes

| Artifact | SHA-256 |
|---|---|
| `thien-skill-creative-diagram/LICENSE.md` | `64d88634fe7ad212049799d7febdbe574bd64574c1f75cfe065f2952a2906f31` |
| `thien-skill-creative-diagram/LICENSE-APPLICATION.md` | `b791650dbf143e6f5aac9144e9c69b1f44ce62aface1ebe3a7e7e61bba999381` |
| `thien-skill-creative-diagram/NOTICE` | `f834519493b5393bd2ae43be7389813c3c72f9bf6e236c5f60f48a2bfda63cb0` |
| `thien-skill-creative-diagram/THIRD_PARTY_NOTICES.md` | `6b89ecddda5b7aecee3cf5d1203cdf9ada12da90d794f3a86af16cffabab14d0` |
| `thien-skill-creative-diagram/SOURCE_MANIFEST.json` | `f534b3ec80bb69923a4a692a35abecc1ab327677077aadcc90c24231c5d5dcb7` |
| `thien-skill-creative-diagram/ASSET_MANIFEST.json` | `549651fd285035d31823e1020552011c69bf76c6a84dbe6e957fc03152897b2e` |

## 4. D-028 asset scope

- Only `AST-TDTN-LIGHT-64` and `AST-TDTN-LIGHT-400` target `openai-plugin` and `universal-raw-skill` at `assets/brand/`.
- No brand asset targets `claude-plugin`.
- The other 14 owner-approved derivatives are retained as provenance-only and are not packaged in v1.0.0.
- Six 32/48px derivatives remain QA-only and excluded under D-027.
- Every candidate remains `release_eligible: false` until G-06 and authorized P-13 execution.
- P-13 official host-field verification, asset copying, overlays, package build and smoke tests were not performed.

## 5. Verification results

| Check | Result |
|---|---|
| deterministic build/check | pass |
| singular-name transform limited to two bilingual title lines | pass |
| JSON syntax | pass for both manifests and evidence records |
| dependency-free legal/provenance checks | 29/29 pass |
| manifest → third-party notice projection | exact match |
| manifest → NOTICE projection | exact match |
| grant channels | paid order, written permission/email and commercial agreement present in both languages |
| Vietnamese priority and Vietnam forum | present in the license candidate |
| brand/third-party carve-out | present and bilingual |
| P-09 inventory reconciliation | 16 approved ≥64px; 6 QA-only at 32/48px; 22/22 hashes resolve |
| D-028 package-scope reconciliation | exactly 2 targeted; 14 provenance-only; 0 Claude target |
| absolute development paths in legal bundle | none |
| full regression | 127 tests, `OK` |
| package/ZIP/Git/release actions | not performed |
| Vietnamese-lawyer sign-off | present under D-030; exact candidate/hash binding passes; capacity is self-attested and not independently credential-verified |

`jsonschema` is not installed in the workspace. No dependency was installed. JSON syntax and the candidate's P-01 schema invariants were verified with dependency-free checks; this tooling limit remains disclosed in `verification-report.json`.

## 6. Gate readiness

There is no unresolved owner or lawyer decision in P-10. The owner approved exact RC2 under D-029, and Tran Ngoc Thien approved the same exact RC2 in the expressly stated capacity of Vietnamese lawyer under D-030. Technical drafting, manifest reconciliation, exact hashing, review binding and regression verification are complete. P-10 is therefore `passed`.

The D-030 record identifies:

- candidate ID `TCD-LEGAL-1.0.0-RC2`;
- version `1.0.0`;
- aggregate SHA-256 `8f16380761cd6026166daa12ee36227d96e0e3b92ce605f4d9057624de8292c6`;
- reviewer identity, stated professional capacity, review date and absence of conditions;
- all six reviewed artifact paths and hashes.

The owner explicitly approved G-06 `PASS` under D-031 for this exact candidate and the D-027 brand selection. D-031 does not start P-13 or authorize release. If any legal byte changes after D-030 or any approved brand byte changes after D-027, G-06 must be reviewed again.

## 7. Evidence artifacts

| Path | Role | SHA-256 |
|---|---|---|
| `evidence/p10/build_legal_candidate.py` | deterministic legal/provenance builder | `891320230cd89e70547d7e005ee706480ecf8e1f45a0df1637a77223f35edf98` |
| `evidence/p10/verify_legal_candidate.py` | dependency-free consistency and exact-sign-off verifier | `db17bfd5e88bff2e094964cf75b51797ec36bfe7c647b69437e5efda2eddb2f5` |
| `evidence/p10/legal-candidate-build.json` | exact RC2/version/hash binding | `be641233d6017ca22b8d4416df254591a2c03a345bb7bceb91128d318ee9616d` |
| `evidence/p10/verification-report.json` | 29-check report, sign-off binding and runtime inventory digest | `65bea1f20fc421f46b33879a748fdc953c4105c932060ddbfdf60d2dd74daee1` |
| `evidence/p10/OFFICIAL-LEGAL-SOURCES.md` | official Vietnamese legal-source record | `8864faee6735234ffe36dee559d744b3b05e53e7cc620c3855b26f1b792e722c` |
| `evidence/p10/OPEN-DECISIONS.md` | resolved D-028 decision record | `75edba3ef6686c74df6b37ee0000fbca086ee9f1cb9e9986219bafb1a41d32d1` |
| `evidence/p10/LAWYER-REVIEW-PACKET.md` | exact lawyer-review handoff packet | `ed138502aea598df37cc6a4dbccdca7c67356f925fb8216abb0fc722a34ba606` |
| `evidence/p10/LAWYER-APPROVAL-RECORD.json` | D-030 exact-candidate Vietnamese-lawyer approval record | `688a588587f4458baa8386f7e6af3507fce4a1dd3f6dc2d7ede57ef701714cd1` |

P-13 remains `not-started` and unauthorized throughout this record.
