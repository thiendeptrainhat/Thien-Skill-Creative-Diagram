# P-02 platform surface support matrix

**Matrix ID:** `P02-SURFACE-1`  
**Verified:** 2026-08-15  
**Status:** approved P-02 support contract; later P-13 smoke evidence required  
**Source rule:** only official Agent Skills, Anthropic and OpenAI documentation.

## 1. Status semantics

- `supported`: official install path exists and the exact release artifact has passed install, trigger, representative output and fallback smoke tests on that surface.
- `conditional`: official capability exists, but an account/admin/runtime condition or exact-artifact smoke test remains. It is not counted or advertised as supported.
- `unsupported`: official documentation excludes the route or no approved installation contract exists for v1.0.0.

At P-02 no release artifact exists, so no cell may yet be `supported`. The owner approved the `conditional` statuses and evidence rule on 2026-08-15; this approves only the disclosed limits, not a compatibility claim.

## 2. Artifact envelope decision

- Universal raw-skill ZIP: one top-level `thien-skill-creative-diagram/` folder with `SKILL.md` at its root. It is a direct upload candidate only where official docs accept a skill ZIP; elsewhere it is extracted/copied into the documented skill directory.
- Claude plugin ZIP: a deterministic delivery archive containing one Claude plugin directory. Claude Code consumes the extracted plugin directory or marketplace source; the ZIP is not described as a universal direct-install envelope.
- OpenAI plugin ZIP: a deterministic delivery archive containing one OpenAI plugin directory. OpenAI's official flow consumes a plugin directory through a marketplace/source; the ZIP is not advertised as a generic direct-upload format.

This separates archive reproducibility from host install semantics and resolves the P-01 ZIP uncertainty without inventing an install method.

## 3. Approved P-02 matrix

| ID | Surface | Artifact | Install method | Trigger | Core output/fallback | Approved P-02 status | External condition and P-13 evidence rule | Official evidence |
|---|---|---|---|---|---|---|---|---|
| `SUR-CL-01` | Claude Code personal raw skill | Universal raw skill folder after extraction | copy folder to `~/.claude/skills/` | implicit description match or `/thien-skill-creative-diagram` | HTML/SVG; PNG conditional on local renderer | conditional | fresh-session discovery, direct + implicit + negative trigger, HTML/SVG and renderer-absent fallback smoke | `https://code.claude.com/docs/en/skills` |
| `SUR-CL-02` | Claude Code project raw skill | Universal raw skill folder after extraction | copy folder to `.claude/skills/` | implicit or direct slash invocation | same as above | conditional | project trust where required; repeat discovery/trigger/output/fallback smoke | `https://code.claude.com/docs/en/skills` |
| `SUR-CL-03` | Claude Code plugin | extracted Claude plugin directory | local `--plugin-dir` for test; approved marketplace/source for distribution | namespaced implicit/direct skill invocation | HTML/SVG; local PNG conditional | conditional | plugin manifest validation; install/reload; namespaced trigger; no overlay leakage; fallback smoke | `https://code.claude.com/docs/en/plugins` |
| `SUR-CL-04` | Claude Code cloud/web session using repository skill | project raw skill in repository | repository `.claude/skills/` visible to the session | implicit or direct invocation | HTML/SVG; PNG depends on hosted runtime | conditional | repository skill discovery and code-execution/file-output availability must be observed on target session | `https://code.claude.com/docs/en/skills` |
| `SUR-CL-05` | claude.ai chat custom skill | Universal raw-skill ZIP | upload ZIP containing one skill folder in Customize/Skills | automatic relevance or enabled skill workflow | HTML/SVG file output; PNG runtime-dependent | conditional | code execution/file creation enabled; account/admin permits upload; exact ZIP upload + trigger + output + fallback smoke | `https://support.claude.com/en/articles/12512180-use-skills-in-claude`; `https://platform.claude.com/docs/en/agents-and-tools/agent-skills/overview` |
| `SUR-CL-06` | Claude Cowork custom skill | account custom skill or approved Cowork plugin | Skills account upload or Cowork plugin UI, as available | automatic relevance / plugin namespaced behavior | HTML/SVG; PNG runtime-dependent | conditional | plan/admin/code-execution and exact artifact route must be verified in the target Cowork environment | `https://support.claude.com/en/articles/12512180-use-skills-in-claude`; `https://claude.com/docs/cowork/guide/plugins` |
| `SUR-CL-07` | Claude API custom skill | Universal raw-skill ZIP/files | upload through Skills API; attach `skill_id` with code execution | API container configuration plus user prompt | HTML/SVG files; PNG only if preinstalled renderer exists | conditional | API access, `skills-2025-10-02` beta header, code-execution tool, no network/runtime install; upload/invoke/download/fallback smoke | `https://platform.claude.com/docs/en/agents-and-tools/agent-skills/overview`; `https://platform.claude.com/docs/en/api/beta/skills/create` |
| `SUR-OAI-01` | ChatGPT web/mobile Chat and Work | OpenAI plugin directory delivered by ZIP | install plugin through universal plugin directory/marketplace source after extraction | `@` selection or implicit match | HTML/SVG artifact; PNG host-dependent | conditional | plugin availability/account policy plus exact marketplace install, trigger and output smoke; ZIP itself is not a claimed upload format | `https://developers.openai.com/plugins`; `https://learn.chatgpt.com/docs/build-skills` |
| `SUR-OAI-02` | ChatGPT web/mobile standalone raw skill | Universal raw-skill ZIP | no standalone route documented for these surfaces | none | none | unsupported | use plugin route `SUR-OAI-01`; reconsider only if official docs add a direct skill route | `https://learn.chatgpt.com/docs/build-skills` |
| `SUR-OAI-03` | ChatGPT desktop standalone skill | Universal raw skill folder | local skill discovery/import supported by desktop skill surface; exact UI route verified at smoke time | `@` selection or implicit match | HTML/SVG; PNG renderer-dependent | conditional | exact artifact discovery, UI metadata, direct/implicit/negative trigger and fallback smoke | `https://learn.chatgpt.com/docs/build-skills` |
| `SUR-OAI-04` | Codex in ChatGPT desktop via plugin | extracted OpenAI plugin directory | universal plugin directory/marketplace source | `@`/plugin invocation or implicit match | HTML/SVG; PNG renderer-dependent | conditional | marketplace install, plugin manifest, skill discovery, trigger/output/fallback smoke | `https://developers.openai.com/plugins`; `https://developers.openai.com/plugins/build/plugins` |
| `SUR-OAI-05` | Codex CLI raw skill | Universal raw skill folder after extraction | copy to repository `.agents/skills/` or user `$HOME/.agents/skills/` | `$thien-skill-creative-diagram`, `/skills`, or implicit match | HTML/SVG; PNG local-renderer conditional | conditional | fresh CLI discovery from repository and user scope; direct + implicit + negative trigger; output/fallback smoke | `https://learn.chatgpt.com/docs/build-skills` |
| `SUR-OAI-06` | Codex CLI plugin | extracted OpenAI plugin directory | `codex plugin marketplace add …` then install/enable through documented source | plugin skill invocation or implicit match | HTML/SVG; PNG local-renderer conditional | conditional | marketplace/source, cached install, manifest, trigger/output/fallback smoke | `https://developers.openai.com/plugins/build/plugins` |
| `SUR-OAI-07` | Codex IDE extension raw skill | Universal raw skill folder after extraction | repository/user `.agents/skills/` discovered by Codex | `$` mention, `/skills`, or implicit match | HTML/SVG; PNG environment-dependent | conditional | fresh IDE discovery, direct + implicit + negative trigger and output/fallback smoke | `https://learn.chatgpt.com/docs/build-skills` |
| `SUR-OAI-08` | Codex IDE extension plugin | OpenAI plugin | no plugin route documented for IDE extension | none | none | unsupported | use raw-skill route `SUR-OAI-07` | `https://learn.chatgpt.com/docs/build-skills`; `https://developers.openai.com/plugins` |

## 4. Approved conditional evidence rule

A conditional cell may become `supported` only when all applicable evidence is retained for the exact release candidate hash:

1. official documentation re-verified within the P-13 build window;
2. artifact installed through the matrix method without editing canonical core;
3. fresh-session discovery and direct invocation pass;
4. positive implicit trigger and a semantically adjacent negative trigger pass;
5. one representative Vietnamese diagram produces valid HTML and SVG;
6. renderer-present PNG succeeds when the surface offers a renderer, and renderer-absent behavior returns the documented fallback without installation;
7. no network, path, dependency or permission side effect occurs;
8. host limitation and tested version/account condition are recorded.

If the external condition cannot be satisfied before release, the cell stays `conditional` and is not counted/advertised as supported, or the owner may approve downgrading it to `unsupported`. Documentary evidence alone cannot promote it to `supported`.

## 5. Platform-neutrality assertions

- `SKILL.md` later uses only the approved common frontmatter subset.
- Claude and OpenAI manifests remain generated overlays.
- `agents/openai.yaml` is excluded from Claude plugin and included only in OpenAI/Universal targets as specified by `PROJECT-CONTRACT.md`.
- Runtime core and legal/provenance bytes remain equal across packages; installation notes cannot alter behavior.
- Every surface reuses the same request, IR, safety, output and validation contracts.
