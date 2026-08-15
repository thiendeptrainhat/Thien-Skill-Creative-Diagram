# G-05 — Packaging and cross-platform gate evidence

**Date:** 2026-08-15  
**Gate result:** `PASS`  
**Approval date:** 2026-08-16  
**Approved by:** Tran Ngoc Thien  
**Candidate:** `TCD-PACKAGES-1.0.0-RC1`, version `1.0.0`

## 1. Candidate binding

| Artifact | SHA-256 |
|---|---|
| `dist/thien-skill-creative-diagram-1.0.0-claude-plugin.zip` | `bba5b464322d8d50ec2f9b76e18581df3e5614004078ba40708f2c8cd1104fa9` |
| `dist/thien-skill-creative-diagram-1.0.0-openai-plugin.zip` | `7d7a33dbdecdd87e9f5237c3ab39b1416ba11c3b736424ba3eb0151c9d73893c` |
| `dist/thien-skill-creative-diagram-1.0.0-universal-raw-skill.zip` | `4fcccc656008dd1caba8c1605b0523b0c041afaf216f739aba7373b5d5ac748f` |

The candidate is reproducibly bound by `evidence/p13/package-build.json` and `dist/SHA256SUMS.txt`.

## 2. Mandatory-condition matrix

| G-05 condition | Evidence | Result |
|---|---|---|
| three independent archives use version `1.0.0` | three exact files and manifests above | satisfied |
| four-inventory architecture and package trees | deterministic target mappings; 23/23 verification | satisfied |
| runtime core and legal bundle parity | runtime aggregate `35ad082905d7909a1180ba1807b7de15611b447db7925dc009953fe5ec1da564`; legal aggregate `f5c9ac23fd5bff4e8303961cf309b8447243c5db4f4a5501574aafaa3545a94d` on all targets | satisfied |
| valid `SKILL.md`, name/folder/frontmatter | common `name`/`description`, exact folder identity, packaged link checks | satisfied |
| one top-level folder and current official envelopes | archive invariant checks; current official source record | satisfied |
| Universal extracts to `.agents/skills/<skill-id>` contract | one top-level skill folder with root `SKILL.md` | satisfied |
| six legal/provenance files in every package | byte-identical; exact G-06 RC2 hashes retained | satisfied |
| Claude excludes OpenAI overlay; OpenAI/Universal include it | exact target-member assertions | satisfied |
| declared brand differences only | two D-028 files in OpenAI/Universal; none in Claude | satisfied |
| no absolute path, traversal, symlink, cache, secret or development file | ZIP metadata and canonical package-inventory validator | satisfied |
| deterministic build | second build/check reproduces all ZIP bytes and checksums | satisfied |
| references and manifests | all packaged JSON parses; all relative Markdown links resolve; Claude CLI and OpenAI dependency-free manifest checks pass | satisfied |
| surface evidence rule | 0 supported, 13 conditional, 2 unsupported; no conditional row advertised as supported | satisfied |
| host capability fallback | extracted packages render HTML/SVG and return documented PNG→SVG fallback without installation | satisfied |

## 3. Blocking-failure review

- Runtime and legal bytes do not drift between targets.
- Extracted package runtime smoke passes on all three targets.
- No personal path or hidden dependency enters the payload.
- Official manifest and install-surface contracts were rechecked within P-13.
- Conditional surfaces remain explicitly conditional; no unsupported route is advertised.

No G-05 blocking failure is present in the recorded evidence.

## 4. Tooling disclosure

Claude Code `2.1.183` reports `Validation passed` for the extracted Claude plugin. Codex CLI `0.146.0` exposes plugin marketplace/install commands but no standalone plugin-validation command. The bundled OpenAI `plugin-creator` validator cannot import PyYAML in the available workspace Python runtimes, so no dependency was installed; equivalent accepted field, asset, frontmatter and path invariants were checked by the dependency-free P-13 verifier against current official documentation.

This disclosed tooling limitation does not promote any conditional surface to supported and does not conceal a failing package assertion.

## 5. Evidence

- P-13 record: `evidence/p13/P-13-EVIDENCE.md`, SHA-256 `44a994da5f1c7a5ea310b1c0ea365d3dda01f9b0727552c7e6bd845aa6dde6a0`.
- Verification report: `evidence/p13/verification-report.json`, SHA-256 `67afafb2ad5170e76e05ec6b3d16d1646bbc607a8af0e331f20ddf2fd11a4489`.
- Surface report: `evidence/p13/surface-smoke-report.json`, SHA-256 `9d71a14f6a26b6945d7e671fc7250a6ce6194e556f2911cf1294d0f929afffac`.
- Official source record: `evidence/p13/OFFICIAL-PLATFORM-SOURCES.md`, SHA-256 `42ca895b9ee0d85d434acd47cd431b8da14e220dcb4c5430d6ad4b93f8d87f98`.

## 6. Approval record

Owner statement received on 2026-08-16:

> xác nhận technical/QA review hiện tại là đủ và phê duyệt G-05 PASS.

P-13 is `passed` and G-05 is `PASS` for exact candidate `TCD-PACKAGES-1.0.0-RC1` and the three hashes bound above.

## 7. Gate boundary

This approval itself does not authorize P-14 or G-07. D-034 later authorized P-14 release-candidate preparation and read-only target verification; G-07 remains `NOT-EVALUATED`, and the three ZIP files remain local release candidates only. No Git initialization, commit, tag, push or release action is authorized or recorded by this gate action.
