# P-20 — v2.0.0 package/release preparation evidence

**Record ID:** `P20-EVIDENCE-2026-08-30`  
**Authorization:** D-130  
**Target release version:** `2.0.0`  
**Technical candidate:** `TCD-PACKAGES-2.0.0-RC1`  
**Phase result:** technical preparation complete; D-131 subsequently approved all v2.0.0 gates and the exact release candidate with execution hold

## Outcome

P-20 rebound the exact passed source/gallery lineage into a local-only v2.0.0 package candidate without renaming or mutating the frozen P-18/P-19 artifacts. It prepared one exact legal/provenance/brand candidate, generated three deterministic package ZIPs under `evidence/p20/candidate-dist/`, and completed package/parity/hygiene/manifest/smoke/regression verification.

This is not a release and is not stored in historical `dist/`.

## Immutable source/gallery lineage

| Artifact | SHA-256 | Result |
|---|---|---|
| P-17 source manifest | `efabfb7e9e485449947ce98bc8e2fc5078a4c7d2593521c115b309c9aef24c57` | preserved |
| P-18 review-17 manifest | `7925c1ab0515a59057851bb3888ff4d9974e5f5701b873b1f11468a5fd64a03a` | preserved |
| P-19B review-45 gallery manifest | `ae95aca927ec69904483441db6b85de0381c1c1d85f4f01ee07a21a40aed0ba2` | preserved |
| P-19C freeze manifest | `5c98b8f56987ed69e65a93e01ca05dc2fd95c6d4e288007ffaa7fd615c8180ed` | preserved |
| G-04@1.5.0 record | `0d3720f9ff9bfc658a1477fa6d487bdabb32e99aa7a9a0e42f0ebd02869c5d63` | preserved lineage |

The evidence comparison remains two distinct sets with exactly `14 P-18 + 93 P-19 = 107`. No P-19 artifact substitutes, overwrites, regenerates, renames, or removes P-18.

D-128 remains mandatory in the package-facing skill guidance: the 31 masked silhouettes are QA samples, not a fixed registry, catalog, template set, or output boundary. A safe and semantically valid explicit user request takes precedence over diagram type, content, structure, layout, visual treatment, and presentation.

## Exact legal/provenance candidate

- Candidate ID: `TCD-LEGAL-2.0.0-RC1`
- Logical six-file aggregate SHA-256: `93643da0d3183db68f1f70730840bd1bcae5935b130e405179f14284501f29c0`
- Build record: `evidence/p20/legal-candidate-build.json`, file SHA-256 `53c21781030ab3598b3c3bc78707ac3bd1ef70618d5b7017f13d4d1bd3555922`
- Exact unchanged legal bytes: `LICENSE.md`, `THIRD_PARTY_NOTICES.md`
- Candidate-updated bytes requiring exact review: `LICENSE-APPLICATION.md`, `NOTICE`, `SOURCE_MANIFEST.json`, `ASSET_MANIFEST.json`
- Brand proposal carries forward the exact D-027/D-028 light-plate 64px and 400px bytes only for OpenAI and Universal; Claude contains no brand asset.

At the technical-preparation freeze, the candidate was not release-eligible pending owner and Vietnamese-lawyer decisions. D-131 subsequently supplied owner approval and an explicit owner waiver of independent lawyer review for this exact version/hash.

## Exact package candidate

| Target | Files | Bytes | SHA-256 |
|---|---:|---:|---|
| Claude plugin | 113 | 377788 | `7ef52b21be9dcc96caae5621e7788f9eb31cd46ae26ef94e47e3a75889ce99f6` |
| OpenAI plugin | 116 | 468849 | `65c2d6fbc33dc6d3065c5d6ae44a5b4fe02e5f7e8838b7f05eede07766124315` |
| Universal raw skill | 115 | 460534 | `88e22caee1f7df7ff8893dbd5cb461c6117921765e56c349e3da6c6452f15f93` |

`candidate-dist/SHA256SUMS.txt` SHA-256: `96246d4d62153b82c9e3505ebe904433225f15b106e002d026fa069e8a4a8f17`.

Package build record: `evidence/p20/package-build.json`, SHA-256 `e83cecff0be25cebcd85ffcaf7a58c25d8c0388bdd534ff17345ae4be6716b7f`.

## Technical verification

- P-20 package checks: `26/26 PASS`
- Full canonical regression: `414/414 PASS`
- Deterministic legal and package regeneration: `PASS`
- Three extracted runtime smoke tests: `PASS`
- Claude Code `2.1.183` plugin manifest/layout validation: `PASS`
- Dependency-free OpenAI manifest, relative-path, UI asset, JSON and Markdown-link validation: `PASS`
- Historical `dist/` v1.0.0 exact hashes and four-file inventory: `PASS`
- Frozen P-18/P-19 lineage and 107-diagram coexistence: `PASS`
- Gallery, masked-review files, tests, evidence, caches, secrets, absolute development paths and nested ZIPs excluded from package payload: `PASS`

Verification record: `evidence/p20/verification-report.json`, SHA-256 `8d147d5affb25597125771bf15c458fb5563d2828294e531c49d0f14eb91bc44`.

The optional `skill-creator`/`plugin-creator` Python validators could not import `PyYAML` from either available Python runtime. P-20 did not install dependencies. Equivalent dependency-free manifest/frontmatter/path checks ran, and the installed Claude validator passed.

## Platform-source revalidation

P-20 rechecked current official OpenAI plugin, Claude Code plugin, and Agent Skills specifications. Record: `evidence/p20/OFFICIAL-PLATFORM-SOURCES.md`, SHA-256 `ccebc7fd39b26add7eb647831ab20aa3018c88e418ff012688597a92600736f9`.

No documentary evidence alone promoted a support-matrix cell.

## Authority boundary at P-20 technical freeze

P-20 prepared local candidates and evidence only. It did not:

- mark any `G-00…G-07@2.0.0` gate `PASS`;
- approve legal wording, provenance manifest, brand mapping, ZIPs, or release candidate;
- copy v2 candidates into `dist/`;
- modify the publication mirror;
- commit, push, tag, create or change a Release, upload, or publish anything.

## Post-technical owner decision — D-131

On 2026-08-31, owner Tran Ngoc Thien approved all `G-00…G-07@2.0.0` inputs and exact `TCD-RELEASE-2.0.0-RC1`, manifest SHA-256 `2905d4d3945a75ba9b644aece005bcb6de5bb2278ca8f7e47a4247189c77be72`.

For exact `G-06@2.0.0`, the owner waived independent Vietnamese-lawyer review and accepted that risk. This is an owner waiver, not a claim of lawyer sign-off. D-128 and the separate `14 P-18 + 93 P-19 = 107` evidence sets remain mandatory.

All v2.0.0 gates are `PASS`, but execution remains on hold: no v2 artifact was promoted into `dist`, and no publication, commit, push, tag or Release action was performed or authorized without a separate explicit command.
