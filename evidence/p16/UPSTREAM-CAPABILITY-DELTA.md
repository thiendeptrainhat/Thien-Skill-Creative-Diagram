# P-16 upstream capability-bearing delta disposition

**Record ID:** `P16-UPSTREAM-CAPABILITY-DELTA-2026-08-22`  
**Range:** `09df49d8d1a1c7fb2efdfcdc7a2a0713534350a6..648c2a597839301e06df1e7434a08bde9f42eed3`  
**Scope rule:** only D-043 visual taxonomy/capability delta is adopted into the `1.5.0` candidate; all other changed upstream behavior is either inherited unchanged from the approved project contract or explicitly excluded.

## 1. Complete repository-range and skill-pathscope grouping

Read-only `git diff --name-status` and `git diff --shortstat` over the exact **whole-repository** range produced 170 changed paths, `+23895/-244`. The exact ordered `status + path` set and per-path disposition are machine-readable in `UPSTREAM-FULL-RANGE-LEDGER.json`; its set-equality rule permits neither omission nor extra path.

| Top-level group | Count | Project disposition boundary |
|---|---:|---|
| `.claude-plugin` | 2 | Provider/package expression excluded. |
| `.codex-plugin` | 1 | Provider/package expression excluded. |
| `.factory-plugin` | 2 | New provider surface explicitly excluded. |
| `.github` | 3 | Workflow/template excluded; preview image is inventory-only expression. |
| repository root | 3 | README claims are inventory-only; maintainer/package prose and metadata excluded. |
| `commands` | 4 | Provider command surface excluded. |
| `docs` | 46 | Screenshots are inventory-only; layout-grammar/spec planning may provide abstract context only; all expression remains excluded. |
| `prompts` | 1 | Provider prompt excluded. |
| `scripts` | 34 | Code excluded; 14 capability verifier/test paths contribute abstract test lessons only. |
| `skills` | 74 | Detailed skill pathscope disposition follows below. |
| **Whole range** | **170** | **Every changed path is represented in the exact ledger.** |

The 74-path `skills/diagram-design/**` subset has `+9048/-108` and is classified as follows:

| Skill-pathscope group | Count | Upstream change | Project disposition |
|---|---:|---|---|
| Top-level skill instruction | 1 modified | `skills/diagram-design/SKILL.md` | Adopt only the abstract 39-type inventory and four named capability relationships recorded in the P-16 matrix. Do not adopt upstream prose, workflow, style or provider behavior. |
| Gallery expression | 47 files: 45 added, 2 modified | 36 HTML files for 12 canonical additions, 9 HTML files for Slopegraph/Ridgeline/Bubble, plus `assets/index.html` and `assets/template-full.html` changes | Count/name presence is factual inventory evidence only. Every byte of upstream HTML/CSS/SVG/JS/prose/data/layout/template/pixels is excluded. Dumbbell has no upstream example at this exact snapshot. |
| New canonical references | 12 added | `type-polar`, `type-treemap`, `type-sankey`, `type-fishbone`, `type-wardley`, `type-kanban`, `type-journey`, `type-deployment`, `type-dependency`, `type-uml-class`, `type-story-map`, `type-db-schema` | Adopt abstract functional/semantic requirements only through `CAP-T28..T39`; implementation and tests must be original. |
| Existing visual references | 5 modified | `type-bar`, `type-line`, `type-scatter`, `type-er`, `type-high-level` | Adopt abstract Dumbbell/Slopegraph/Ridgeline/Bubble behavior and the conceptual-ER versus physical-schema distinction. The unrelated High-Level correction/data-lake expression and all concrete formulas/specimens are not adopted; existing v1.0 behavior remains authoritative. |
| Existing cross-cutting references | 6 modified | `export`, `import-drawio`, `import-mermaid`, `onboarding`, `output-spec`, `semantic-patterns` | See the file-level table below. No new output/import/onboarding/platform capability is added by D-043. |
| New environment diagnostic reference | 1 added | `doctor.md` | Explicitly excluded by `PROJECT-CONTRACT.md` §3.3 and D-043 boundary. |
| Upstream implementation scripts | 2 modified | `drawio_extract.py`, `mermaid_extract.py` | Excluded implementation material. No code is copied, adapted or executed as project implementation. P-16 does not change project runtime/import support. |
| **Skill subset** | **74** |  | Complete pathscope disposition; the other 96 repository paths are covered by the exact ledger above. |

## 2. Capability-bearing file hashes and disposition

Hashes are SHA-256 of exact Git blob content rendered as file bytes.

| Path | P-01 hash | P-16 candidate hash | Disposition for target 1.5.0 |
|---|---|---|---|
| `references/semantic-patterns.md` | `6df3d41cafea6a0f16f8921a50af732e34f6172d4ba6fb9f05ec8f92bc27e472` | `c56d7b9dc95066dcea2ecb0810d92fd7b56afd62aaf48ca0971129de0e28bdfa` | Change is only the upstream count 27→39. The project's seven `CAP-P01..P07` behaviors are inherited unchanged; no new pattern is added. |
| `references/animation.md` | `24ce83341aee976680cb69d43b2afab40efcfa97edcd394e5b17183eb58fc94a` | `24ce83341aee976680cb69d43b2afab40efcfa97edcd394e5b17183eb58fc94a` | Byte-unchanged. `CAP-M01..M12` and static-first contract are inherited unchanged. |
| `references/import-drawio.md` | `106d29f5501fe39d423f9145c04ab1e1ffa747d6cd453ee8ffa58a604413c4c5` | `2615ba8efb300ecc498df72223a91c6c712411efb38892fc779b583ad8b7b4ce` | Upstream command name changed. Provider command naming is excluded; project `CAP-I01..I04/I11/I12` behavior is inherited unchanged. |
| `references/import-mermaid.md` | `491ff83440fc995401b5ba20f63325f976732bf1669003c1840b4137072cc274` | `952de5fb9e0f24178cbbbfd784e9838ad6770d00e5e5550842f4f38f44f75474` | Upstream adds grammar cases. They are outside D-043 visual delta; project approved Mermaid subset remains unchanged unless separately authorized. |
| `references/output-spec.md` | `d8fa916f523b99ada083a652f4440d3f0d086a8af61ae333bac50153338f42a3` | `35ffeca80b5760cdc20614fcb95f82dae64a501ea75db885cb8d62819b883de9` | Upstream adds Korean font/width guidance. Target v1.5.0 adds no language/font/output surface; existing Vietnamese/accessibility/output contract is inherited unchanged. |
| `references/export.md` | `75f6fbcafe53899fadfa10ace59a6338f81e96ad5069a0b03513cba8ad65aa7a` | `ca672e5c74bc1540df108541efed0cea080db7df3bfc69991f297ab604fec97e` | Upstream command rename only. Provider command/packaging surface is explicitly excluded. `CAP-O01/O05/O06` remain unchanged. |
| `references/onboarding.md` | `7b9ef85e8f79c6f32e7c92c785d65b9abbaa5036e678a4eb056764a04b0f887a` | `320e09ccf1073f19e759592c3bb8e770c90abfc7f7cea71e5d543ad552efb019` | Count wording and Factory Droid paths changed. Onboarding, style mutation and new platform surfaces are excluded. |
| `references/type-er.md` | `61ee3643c9e3a1e2c3a329640132ede2c193bfabaebbbb5fa486be800b6afa29` | `0f4a718b202edec593e4555e0353a4080d4be6d98328209db083898f2f01302c` | Adopt only abstract routing distinction: `CAP-T06` conceptual/logical ER vs `CAP-T39` physical schema. No prose or layout expression reused. |
| `references/type-high-level.md` | `035a0eac7d4b38452a324d9421457400dfe1a109d43f6acd377ba2c47f873a89` | `86e9e681189b013752edc512a8efb651e67aba52e9ddfbfe46d1fc117f1d5248` | Formula correction and specimen links are not part of D-043. Existing project High-Level/data-lake behavior and tests remain authoritative. |
| `scripts/drawio_extract.py` | `a262c2515c81a54e67b1ea71178da5e1784b813e9f8b16efa70c6bd994bcf1d6` | `302b357688de234e5a46818a25120fd8fe5a58e5c3338f1f027ec269f24424d9` | Excluded code. The abstract safety lesson is already covered by the v1.0 security/fidelity contract; no source change in P-16. |
| `scripts/mermaid_extract.py` | `297ff6a8042c33d33df72ac4384bf666b2ab045f74030269adb45a89a7a2e0f8` | `e7f5f45b2cff600c7c1079e76f9aa1836686ee3f3e5003686dff8af98912a1da` | Excluded code and new grammar implementation. No project parser delta is authorized. |

## 3. License and principle-source bindings

| Source | Exact binding | P-16 disposition |
|---|---|---|
| Upstream repository license | MIT `LICENSE`, SHA-256 `bb7e12e91fecef43024111123ff784cec6c485585561d8b552557c0173b3ed29` | Recorded for provenance; the stricter project no-copy/independent-reimplementation policy remains controlling. |
| Upstream third-party ledger | `THIRD_PARTY_LICENSES.md`, SHA-256 `22f5afcea56373e84d7f7eff93d8d4d6e4b81c5375bb1c996e78b91e53fa0b37` at both commits | Byte-unchanged. No third-party upstream asset/code is imported into the project. |
| `Thien-UI-UX-Ultra` | commit `fb4e57758f525827e04004737d779f4c93b9b3a0`, tag `v2.0.0`, tree `96e55f4693b81af594cfb9190fc66321a3b5fecb` | P-01 principle-only binding is inherited unchanged: design contract, progressive routing, render–inspect–revise–verify, accessibility and evidence discipline. No code, prose, script, template, token, data or asset reuse. |

## 4. No-expansion conclusion

The candidate adopts exactly 12 canonical additions and four capability variants. It does not silently add upstream command renames, Mermaid extensions, Korean typography, onboarding, Factory Droid support, doctor diagnostics, resource loading, profiles, provider manifests, implementation scripts or gallery expression. Any later request to add those behaviors requires a new owner decision, contract delta and affected gate review.
