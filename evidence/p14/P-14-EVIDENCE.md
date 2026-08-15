# P-14 — Owner Release Approval & Private Release Evidence

**Date:** 2026-08-16  
**Authorized scope:** P-14 under D-034  
**Phase disposition:** `blocked` — GitHub CLI authentication invalid  
**Gate disposition:** G-07 `PASS` under D-037

## Work completed

1. Frozen exact release candidate `TCD-RELEASE-1.0.0-RC1` without rebuilding or changing any ZIP, legal or packaged brand byte.
2. Bound the three package hashes, checksum manifest, G-01 through G-06 evidence, legal RC2, approved golden manifest, approved brand selection and surface-status record.
3. Rechecked deterministic package integrity and package verification.
4. Reconciled residual risks and confirmed zero open Critical/High product/quality/legal finding.
5. Performed read-only local and GitHub target checks.
6. Prepared the owner release-approval packet and G-07 record.
7. Recorded D-035 owner approval for the three ZIP files/overall candidate, acceptance of both Medium risks, Option-A repository scope and the exact GitHub URL.
8. Rechecked the explicit URL through the GitHub connector; the API returned 404, which cannot distinguish an absent repository from a private repository inaccessible to the connector.
9. Scanned Option-A publication scope and identified seven broad absolute-path pattern hits; no file was staged or sanitized without a new owner decision.
10. Used read-only inspection in the authenticated owner browser session to verify the exact repository exists, displays `Private`, exposes owner settings, and is currently empty; no browser mutation was performed.
11. Recorded D-036/A1 and refined the seven initial pattern hits into five actual owner-machine-path files plus two generic security regex/fixture files.
12. Built and verified the deterministic sanitized publication mirror without overwriting local source files; only the five actual-path files changed in the mirror, and no personal owner path remains there.
13. Re-ran the frozen-candidate verifier at 26/26 and the complete regression suite at 127/127 after the A1/README evidence changes.
14. Added root `README.md` with detailed installation, checksum, host limitations, license and provenance information based only on current official Anthropic/OpenAI platform documentation and the approved legal bundle.
15. Recorded D-037: owner approval of G-07 `PASS` and exact authorization for init, commit to `main`, tag/push `v1.0.0`, and GitHub Release creation with the three frozen ZIPs plus `SHA256SUMS.txt`.

## Current blockers

- Exact ZIP/overall release-candidate approval and Medium-risk acceptance are complete under D-035.
- Option A/A1 sanitized publication scope is ready under D-035/D-036; local originals are preserved and the mirror manifest binds every published file except its non-self-hashed manifest record.
- Target repository existence and private visibility are verified; local Git is not initialized.
- GitHub CLI authentication is invalid and must be restored before executing the authorized Git/release actions.

## Evidence set

| Path | SHA-256 |
|---|---|
| `evidence/p14/release-candidate-freeze.json` | `9a1d268f061493823eac4fd8c74693a5256bcefd8b25f6c5eae7bedef29b5ab9` |
| `evidence/p14/freeze-verification-report.json` | `d68544edaabc62e6ba725e01c5d899cb7ea452fd4bdf428c7a002d5f0bb6b71e` |
| `evidence/p14/target-verification.json` | `375cdbb193eee05bec878b6154ad2ed1630ea7203d5abc39722af6fe878683a6` |
| `evidence/p14/publication-scope-scan.json` | `d3e4b0f6c525cf6177f72fd8ea875c6033fd5c2306614ac8cb40b45dc29f24e8` |
| `evidence/p14/RESIDUAL-RISK-LOG.md` | `5bdeb329c18b507e73bc7927c2fbfcd4b0667ba5a8f61377b1f0b1a709146632` |
| `evidence/p14/RELEASE-APPROVAL-PACKET.md` | `cce183ad2e7df34c2ffaf8c31c46c0c014295f32537ed4271364690a393127a4` |
| `evidence/p14/build_publication_mirror.py` | `8c62f520ade3a03666c1e2ce34036d6aabfd381c698f3b08351151cc4564ee54` |
| `evidence/p14/verify_release_candidate.py` | `2983fe3763e14cfb48b24b6c5db58791cc1f506d6c85411f22439c5e844e2f3e` |
| `README.md` | `6294ea8eb5594363ee200e7cb8c83147996baec5cd201c35f11465430c2cd055` |

No Git initialization, commit, tag, push, GitHub repository creation or release had been performed when this record was updated; execution paused at the invalid GitHub CLI authentication prerequisite.
