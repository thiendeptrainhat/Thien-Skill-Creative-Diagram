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

## Post-gate execution condition

- The local GitHub CLI session must be re-authenticated before any authorized Git or release mutation. The currently configured token is invalid; this is an execution prerequisite, not an unresolved gate decision.

## Current target result

The workspace is not a Git repository and has no remote. The GitHub connector returned no repository for the owner filter and an explicit lookup returned API 404; local `gh` reports an invalid token and cannot reach the API. A direct read-only inspection in the authenticated owner browser session nevertheless verified the exact URL, repository title, `Private` badge, owner settings access and empty-repository quick-setup surface. Target existence and required visibility are therefore verified. No authentication change, repository creation or Git mutation was attempted.

## Current publication-mirror result

The generated record `evidence/p14/publication-mirror-manifest.json` binds the sanitized scope by repo-relative path, normalized mode and SHA-256. Its aggregate deliberately excludes only the generated manifest itself to avoid self-reference. The original workspace remains the audit source; the generated mirror under `.release-staging/TCD-RELEASE-1.0.0-RC1` is the only tree eligible for later Git publication if separately authorized.

## Evidence set

| Record | SHA-256 |
|---|---|
| `evidence/p14/release-candidate-freeze.json` | `9a1d268f061493823eac4fd8c74693a5256bcefd8b25f6c5eae7bedef29b5ab9` |
| `evidence/p14/freeze-verification-report.json` | `d68544edaabc62e6ba725e01c5d899cb7ea452fd4bdf428c7a002d5f0bb6b71e` |
| `evidence/p14/target-verification.json` | `375cdbb193eee05bec878b6154ad2ed1630ea7203d5abc39722af6fe878683a6` |
| `evidence/p14/publication-scope-scan.json` | `d3e4b0f6c525cf6177f72fd8ea875c6033fd5c2306614ac8cb40b45dc29f24e8` |
| `evidence/p14/RESIDUAL-RISK-LOG.md` | `5bdeb329c18b507e73bc7927c2fbfcd4b0667ba5a8f61377b1f0b1a709146632` |
| `evidence/p14/RELEASE-APPROVAL-PACKET.md` | `cce183ad2e7df34c2ffaf8c31c46c0c014295f32537ed4271364690a393127a4` |
| `evidence/p14/build_publication_mirror.py` | `8c62f520ade3a03666c1e2ce34036d6aabfd381c698f3b08351151cc4564ee54` |
| `README.md` | `6294ea8eb5594363ee200e7cb8c83147996baec5cd201c35f11465430c2cd055` |
| `evidence/p14/P-14-EVIDENCE.md` | `2ee0b021aff817452aacb8378cb467571b9cdde15e720ebb9cd03afec87706e4` |

## Boundary

G-07 is `PASS` and the exact D-037 release actions are authorized. P-14 is `blocked` until GitHub CLI authentication is restored, the authorized actions complete and release evidence is recorded. No Git or release mutation had occurred when this gate record was updated because the GitHub CLI authentication prerequisite was not satisfied.
