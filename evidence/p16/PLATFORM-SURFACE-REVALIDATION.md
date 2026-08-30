# P-16 official platform and Agent Skills revalidation

**Record ID:** `P16-PLATFORM-REVALIDATION-2026-08-22`  
**Checked:** 2026-08-22, Asia/Ho_Chi_Minh  
**Purpose:** satisfy current-documentation revalidation for `G-01@1.5.0` without changing packaging or support claims  
**Status:** evidence receipt; owner/technical review still required

## 1. Official sources checked

Only official documentation was used for this platform check.

| Authority | Official URL | HTTP result | Retrieved body SHA-256 | Relevant abstract conclusion |
|---|---|---:|---|---|
| Agent Skills open specification | `https://agentskills.io/specification` | 200 | `07a16530d733f55e9359c983aeb7477919bafbf2d60c146ed8edc3f6c3535b0d` | A skill is a directory containing at minimum `SKILL.md`; the specification defines the skill file/frontmatter format and supports progressive resources. |
| Anthropic Claude Code skills | `https://code.claude.com/docs/en/slash-commands` (canonical page presents as “Extend Claude with skills”) | 200 | `7313abbb172f8ead13d6a32431891c88bb3c6975b93db8f80465c78e7c128f55` | Claude Code recognizes personal, project and plugin skill locations; plugin skills are namespaced; Claude states alignment with the Agent Skills standard plus Claude-specific extensions. |
| Anthropic Claude Code plugin reference | `https://code.claude.com/docs/en/plugins-reference` | 200 | `d25090c95ad2a6310effb4f2444ef41bfc805102d8d6e4b0f9e639c1ccc98749` | Claude plugins remain a distribution/container surface distinct from the provider-neutral skill core. Exact plugin installation and validation must still be smoke-tested for a release candidate. |
| OpenAI skill documentation | `https://learn.chatgpt.com/docs/build-skills` | 200 | `0d005cd91b5d7b8052e45e91031686fa10f78c10969676f2052b46915c7df35e` | OpenAI documents skills as reusable instruction bundles built on the Agent Skills standard and exposes skills on stated ChatGPT Desktop/Codex surfaces. Surface availability and account/environment conditions remain host-dependent. |
| OpenAI plugin documentation | `https://learn.chatgpt.com/docs/plugins` | 200 | `e4553a89baf0affb0c1195c83c693c50f3c456a1eddbb98857e5949418299eb6` | OpenAI plugins can bundle skills/connectors; documented availability covers supported ChatGPT and Codex surfaces, while the IDE extension is documented as not supporting plugins. |

HTTP body hashes are volatile receipts, not normative source identifiers. The URLs and the recorded access date are the normative locators. A future packaging/release phase must retrieve the then-current pages again.

## 2. v1.5.0 inheritance decision

The approved P-02 support matrix at `evidence/p02/SURFACE-SUPPORT-MATRIX.md` is inherited **unchanged** for the source/gallery-only `1.5.0` candidate:

- no row is promoted from `conditional` to `supported`;
- no `unsupported` row is promoted;
- no new Claude, OpenAI, Agent Skills, Factory Droid or other provider surface is added;
- no installation method, ZIP envelope, plugin manifest or `agents/openai.yaml` claim is changed;
- P-18/P-19 gallery HTML is QA-only and is not a platform installation artifact;
- the public product request, semantic IR and visual source remain provider-neutral; platform overlays remain outside the current authorized phase.

This is an explicit no-change disposition, not a claim that the 2026-08-15 matrix is permanently current. If packaging is later proposed, G-05 must reverify exact official packaging/install requirements and run surface smoke evidence against the exact release candidate.

## 3. Security and support-status safeguards

- Documentation is evidence, not authorization to install, publish or add a platform.
- No page content, example, code block, manifest or template was copied into the project runtime.
- Official documentary evidence alone cannot promote a P-02 `conditional` cell to `supported`; the approved installation/discovery/trigger/output/fallback smoke rule still controls.
- Source/gallery work can proceed independently of packaging only after owner approval of G-01/G-02 and a separate phase authorization.

## 4. Gate conclusion

Current-documentation revalidation is complete as a P-16 candidate. It supports the conclusion that no platform contract amendment is necessary for the user-authorized source/gallery target. It does not itself pass G-01/G-02, authorize P-17, or authorize packaging/release.
