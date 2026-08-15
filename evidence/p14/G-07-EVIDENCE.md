# G-07 — Release Authorization Gate Record

**Date:** 2026-08-16  
**Gate ID:** G-07  
**Result:** `PASS`  
**Candidate:** `TCD-RELEASE-1.0.0-RC1`, version `1.0.0`
**Approver:** Tran Ngoc Thien under D-037 on 2026-08-16

## Satisfied prerequisites

- G-00 through G-06 are recorded `PASS`.
- Three ZIP files are frozen at the exact hashes in `release-candidate-freeze.json`.
- Version, package candidate, legal candidate, approved brand selection and approved golden manifest are hash-bound.
- No open Critical or High product/quality/legal finding is recorded.
- Under D-035, the owner approved the exact three ZIP files and overall release candidate and accepted Medium risks `P14-R01` and `P14-R02`.
- Under D-035, the owner selected Option A full private audit repository and confirmed the exact GitHub URL.
- Read-only inspection in an authenticated owner browser session verified the exact repository exists, displays `Private`, and is currently empty.
- Under D-036, the owner selected A1; deterministic mirror verification passes with five actual-path files sanitized, generic security regex/fixtures preserved, no sanitization overwrite of the local source files, and excluded metadata/cache absent.
- Root `README.md` provides detailed checksum, Claude Code, Codex raw-skill, OpenAI local-marketplace and post-install instructions, plus explicit commercial source-available license information and links to the complete legal/provenance bundle.
- Under D-037, the owner approved G-07 `PASS` and separately authorized the exact init/commit/tag/push/release actions for this candidate and target.

## Post-gate execution outcome

- GitHub CLI device authentication was restored; the authorized init/commit/tag/push/release actions completed and remote verification matched the frozen candidate.

## Current target result

The workspace is not a Git repository and has no remote. The GitHub connector returned no repository for the owner filter and an explicit lookup returned API 404; local `gh` reports an invalid token and cannot reach the API. A direct read-only inspection in the authenticated owner browser session nevertheless verified the exact URL, repository title, `Private` badge, owner settings access and empty-repository quick-setup surface. Target existence and required visibility are therefore verified. No authentication change, repository creation or Git mutation was attempted.

## Current publication-mirror result

The generated record `evidence/p14/publication-mirror-manifest.json` binds the sanitized scope by repo-relative path, normalized mode and SHA-256. Its aggregate deliberately excludes only the generated manifest itself to avoid self-reference. The original workspace remains the audit source; the generated mirror under `.release-staging/TCD-RELEASE-1.0.0-RC1` is the only tree eligible for later Git publication if separately authorized.

## Evidence set

| Record | SHA-256 |
|---|---|
| `evidence/p14/release-candidate-freeze.json` | `e0595c4196fe73ec769d5c6b86f0d2a3d5ba6a9de8d93177f9443bb06f46bd6e` |
| `evidence/p14/freeze-verification-report.json` | `1a46219c5d296e93cf5048927e1947275152eab55b4e22337d6a95b11baf2a29` |
| `evidence/p14/target-verification.json` | `375cdbb193eee05bec878b6154ad2ed1630ea7203d5abc39722af6fe878683a6` |
| `evidence/p14/publication-scope-scan.json` | `d3e4b0f6c525cf6177f72fd8ea875c6033fd5c2306614ac8cb40b45dc29f24e8` |
| `evidence/p14/RESIDUAL-RISK-LOG.md` | `2c4c544502d6b28410cbd0f59e9d92894fdb9a1eaf2816872fabae98352473de` |
| `evidence/p14/RELEASE-APPROVAL-PACKET.md` | `04ed8932f0335071eacd26b17abd21f2005d73b76fc88c8f61f867323c7a0d42` |
| `evidence/p14/RELEASE-EVIDENCE.json` | `50acdd840c77acab7ef5ad092ff01150b8467abb61dc2e1cc89ef9503697941e` |
| `evidence/p14/build_publication_mirror.py` | `a688c81534e872737ba83b33d5d69b39e52bb57ef61aa0d87ab3d68803aa6dcb` |
| `README.md` | `6294ea8eb5594363ee200e7cb8c83147996baec5cd201c35f11465430c2cd055` |
| `evidence/p14/P-14-EVIDENCE.md` | `3ce5f34201bcebde991f46aa7fe2c16cc795be86c8f42192127698e69db53857` |

## Boundary

G-07 is `PASS`; D-037 release authorization was executed and verified under D-038. P-14 is `passed`. Tag `v1.0.0` remains bound to release commit `1aae0a0073dd685af1341554f27554eb44c42f63`; subsequent audit-closure evidence on `main` does not alter the tagged release.
