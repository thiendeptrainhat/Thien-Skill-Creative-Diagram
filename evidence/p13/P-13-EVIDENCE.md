# P-13 — Deterministic three-package build evidence

**Date:** 2026-08-15  
**Authorized scope:** P-13 only under D-032; P-14 prohibited  
**Phase disposition:** `passed`  
**Gate disposition:** G-05 `PASS` under D-033  
**Package candidate:** `TCD-PACKAGES-1.0.0-RC1`

## 1. Outcome

One canonical source produced three versioned delivery archives without changing the canonical runtime core or any G-06-approved legal/brand byte:

| Target | File | Members | Bytes | SHA-256 |
|---|---|---:|---:|---|
| Claude plugin | `dist/thien-skill-creative-diagram-1.0.0-claude-plugin.zip` | 63 | 178105 | `bba5b464322d8d50ec2f9b76e18581df3e5614004078ba40708f2c8cd1104fa9` |
| OpenAI plugin | `dist/thien-skill-creative-diagram-1.0.0-openai-plugin.zip` | 66 | 269167 | `7d7a33dbdecdd87e9f5237c3ab39b1416ba11c3b736424ba3eb0151c9d73893c` |
| Universal raw skill | `dist/thien-skill-creative-diagram-1.0.0-universal-raw-skill.zip` | 65 | 264452 | `4fcccc656008dd1caba8c1605b0523b0c041afaf216f739aba7373b5d5ac748f` |

All archives use one top-level `thien-skill-creative-diagram/` folder, sorted member order, normalized `2026-08-15 00:00:00` ZIP timestamps, regular-file mode `0644`, UTF-8 names and deterministic DEFLATE level 9.

## 2. Package boundaries

- Runtime core logical aggregate SHA-256 across all packages: `35ad082905d7909a1180ba1807b7de15611b447db7925dc009953fe5ec1da564`.
- Legal/provenance logical aggregate SHA-256 across all packages: `f5c9ac23fd5bff4e8303961cf309b8447243c5db4f4a5501574aafaa3545a94d`.
- The six legal files match exact approved candidate `TCD-LEGAL-1.0.0-RC2`, aggregate SHA-256 `8f16380761cd6026166daa12ee36227d96e0e3b92ce605f4d9057624de8292c6`.
- Claude receives `.claude-plugin/plugin.json`, nested canonical runtime core, the legal/provenance bundle, no TDTN brand asset and no `agents/openai.yaml`.
- OpenAI receives `.codex-plugin/plugin.json`, nested canonical runtime core, base `agents/openai.yaml`, the legal/provenance bundle and exactly the approved light-plate 64px/400px files at `assets/brand/`; its manifest references them as composer icon and logo.
- Universal receives the canonical runtime at the top-level skill folder, the legal/provenance bundle, the same two brand files, and a deterministic OpenAI overlay derived from canonical `agents/openai.yaml` with relative icon fields.
- Tests, evidence generators, coverage generators, QA-only benchmarks/contact sheets, caches, secrets and source master/logo candidates outside D-028 are excluded.

The `skill-creator` workflow kept the published skill concise and excluded development-only resources. The `plugin-creator` workflow controlled the OpenAI manifest shape and asset-path contract. No marketplace entry or mutable second canonical skill source was created.

## 3. Current official platform verification

Only current official Anthropic, OpenAI and Agent Skills sources were used. They confirm the two distinct plugin manifests, skills-at-plugin-root convention, Codex `.agents/skills` discovery, Claude skill/plugin discovery and OpenAI skill UI icon fields. The source record is `evidence/p13/OFFICIAL-PLATFORM-SOURCES.md`.

No optional support/privacy/terms URL was invented: current OpenAI fields are optional and the package is not yet at P-14 release authorization. No undocumented Claude icon field was introduced.

## 4. Verification

| Check | Result |
|---|---|
| deterministic rebuild/check | pass; 3/3 ZIP bytes reproduce |
| focused package verification | 23/23 pass |
| full regression | 127 tests, `OK` |
| archive ordering/timestamp/mode/compression | pass for every member |
| member path/byte mapping | exact match to deterministic builder |
| one top-level folder | pass for all three ZIP files |
| core parity | same logical aggregate across all packages |
| legal parity and G-06 byte freeze | all six hashes and RC2 aggregate match |
| brand mapping | exactly two D-028 assets in OpenAI/Universal; zero in Claude |
| JSON and relative Markdown links | all parse/resolve |
| package hygiene | canonical inventory validator passes all three archives |
| Claude manifest | `claude plugin validate` passes with Claude Code `2.1.183` |
| OpenAI manifest | dependency-free official-field/path validation passes |
| extracted runtime smoke | all three render Vietnamese HTML and SVG; PNG request falls back to SVG without installation |
| surface status accounting | 0 supported, 13 conditional, 2 unsupported; no status improperly promoted |

The local OpenAI `plugin-creator` validator imports PyYAML, which is unavailable in both workspace Python runtimes. No dependency was installed. Equivalent accepted manifest, frontmatter, path and asset invariants were checked dependency-free; the official OpenAI documentation does not provide a separate `codex plugin validate` command in the installed Codex CLI `0.146.0`.

## 5. Surface boundary

The approved P-02 matrix contains no `supported` row before exact host evidence. P-13 therefore does not claim a live platform compatibility pass from documentary or structural evidence alone:

- all 13 account/runtime/marketplace-dependent rows remain `conditional`;
- the two routes lacking an approved official install contract remain `unsupported`;
- local extraction, manifest validation and representative runtime smoke are retained as package evidence but do not substitute for fresh-session host discovery/trigger evidence.

This satisfies the approved conditional evidence rule without inflating support claims.

## 6. Primary evidence

| Path | Role | SHA-256 |
|---|---|---|
| `evidence/p13/build_packages.py` | deterministic three-target builder | `18c083d2c732aa710c7fff9b4d5273eec7e55af6a764be636a5c41919624e8db` |
| `evidence/p13/verify_packages.py` | package parity/hygiene/smoke verifier | `02646a0bc42acb96ff8e40ab9d4e61d1da0c3080a9b8de103dc46fe41cf4d925` |
| `evidence/p13/package-build.json` | exact candidate/member/hash record | `45ee2d69e10b8efa517e1ab4755445f89eacff689da80723da080790fbc78694` |
| `evidence/p13/verification-report.json` | 23-check report and smoke details | `67afafb2ad5170e76e05ec6b3d16d1646bbc607a8af0e331f20ddf2fd11a4489` |
| `evidence/p13/surface-smoke-report.json` | 15-row status/evidence reconciliation | `9d71a14f6a26b6945d7e671fc7250a6ce6194e556f2911cf1294d0f929afffac` |
| `evidence/p13/OFFICIAL-PLATFORM-SOURCES.md` | official current platform record | `42ca895b9ee0d85d434acd47cd431b8da14e220dcb4c5430d6ad4b93f8d87f98` |
| `dist/SHA256SUMS.txt` | exact three-archive checksum file | `af491f8f0dc9f3dd86ca9158a5456fb36e34acc14aa70030c4e46f6d5ed17596` |

On 2026-08-16, Tran Ngoc Thien confirmed the current technical/QA review was sufficient and approved G-05 `PASS` for the exact three-hash candidate under D-033. D-034 later authorized P-14 release-candidate preparation, but not G-07, Git initialization, commit, tag, push or release; none of those mutation/release actions was performed in P-13.
