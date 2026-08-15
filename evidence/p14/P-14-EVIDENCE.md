# P-14 — Owner Release Approval & Private Release Evidence

**Date:** 2026-08-16  
**Authorized scope:** P-14 under D-034  
**Phase disposition:** `passed`  
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
13. Re-ran the frozen-candidate/release verifier at 27/27 and the complete regression suite at 127/127 after release evidence closure.
14. Added root `README.md` with detailed installation, checksum, host limitations, license and provenance information based only on current official Anthropic/OpenAI platform documentation and the approved legal bundle.
15. Recorded D-037: owner approval of G-07 `PASS` and exact authorization for init, commit to `main`, tag/push `v1.0.0`, and GitHub Release creation with the three frozen ZIPs plus `SHA256SUMS.txt`.
16. Restored GitHub CLI device authentication without exposing the token, initialized only the sanitized mirror, committed it to `main` at `1aae0a0073dd685af1341554f27554eb44c42f63`, and pushed the branch.
17. Created and pushed annotated tag `v1.0.0`; remote tag object `c91194cb454e7e04eafd2636f98a87a6b32fe24f` peels to the exact release commit.
18. Created the non-draft, non-prerelease GitHub Release and uploaded the three frozen ZIPs plus `SHA256SUMS.txt`; remote names, sizes and GitHub-reported SHA-256 digests all match.

## Closure state

- Exact ZIP/overall release-candidate approval and Medium-risk acceptance are complete under D-035.
- Option A/A1 sanitized publication scope is ready under D-035/D-036; local originals are preserved and the mirror manifest binds every published file except its non-self-hashed manifest record.
- Target repository existence and private visibility are verified; local Git is not initialized.
- No release blocker remains for v1.0.0. P-15 remains outside authorization.

## Evidence set

| Path | SHA-256 |
|---|---|
| `evidence/p14/release-candidate-freeze.json` | `e0595c4196fe73ec769d5c6b86f0d2a3d5ba6a9de8d93177f9443bb06f46bd6e` |
| `evidence/p14/freeze-verification-report.json` | `1a46219c5d296e93cf5048927e1947275152eab55b4e22337d6a95b11baf2a29` |
| `evidence/p14/target-verification.json` | `375cdbb193eee05bec878b6154ad2ed1630ea7203d5abc39722af6fe878683a6` |
| `evidence/p14/publication-scope-scan.json` | `d3e4b0f6c525cf6177f72fd8ea875c6033fd5c2306614ac8cb40b45dc29f24e8` |
| `evidence/p14/RESIDUAL-RISK-LOG.md` | `2c4c544502d6b28410cbd0f59e9d92894fdb9a1eaf2816872fabae98352473de` |
| `evidence/p14/RELEASE-APPROVAL-PACKET.md` | `04ed8932f0335071eacd26b17abd21f2005d73b76fc88c8f61f867323c7a0d42` |
| `evidence/p14/RELEASE-EVIDENCE.json` | `50acdd840c77acab7ef5ad092ff01150b8467abb61dc2e1cc89ef9503697941e` |
| `evidence/p14/build_publication_mirror.py` | `a688c81534e872737ba83b33d5d69b39e52bb57ef61aa0d87ab3d68803aa6dcb` |
| `evidence/p14/verify_release_candidate.py` | `cc1758a082a82af5c5eac09c800f6e3f24f1e6b8964dbfbec8839f14fc9eb851` |
| `README.md` | `6294ea8eb5594363ee200e7cb8c83147996baec5cd201c35f11465430c2cd055` |

The unsanitized local audit source was not initialized as Git and was not pushed. Only the deterministic sanitized mirror was published. Tag `v1.0.0` remains fixed at the release commit; the audit-closure update on `main` does not change tagged/package/legal/brand bytes.
