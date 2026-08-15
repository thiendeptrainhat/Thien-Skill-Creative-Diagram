# P-02 current official evidence record

**Record ID:** `P02-OFFICIAL-2026-08-15`  
**Verified:** 2026-08-15, Asia/Ho_Chi_Minh  
**Rule:** current platform facts use only official specification/vendor documentation; accessibility facts use the W3C Recommendation. This record is evidence, not implementation instruction.

## 1. Common skill format

`DOC-AS-01` — `https://agentskills.io/specification`

- skill directory requires `SKILL.md`; `scripts/`, `references` and `assets` are optional;
- portable required frontmatter fields are `name` and `description`;
- name must match its directory and satisfy the documented lowercase/hyphen constraints;
- progressive disclosure and shallow relative references support a concise provider-neutral core.

Contract effect: later canonical core targets the common subset. Provider-specific UI/invocation metadata remains an overlay.

## 2. Anthropic/Claude

`DOC-CL-01` — `https://code.claude.com/docs/en/skills`

- Claude Code personal, project and plugin skill locations are documented as `~/.claude/skills/<name>/SKILL.md`, `.claude/skills/<name>/SKILL.md` and `<plugin>/skills/<name>/SKILL.md`;
- skills can activate by relevance or direct slash invocation; plugin skills are namespaced.

`DOC-CL-02` — `https://code.claude.com/docs/en/plugins`

- plugin identity is at `.claude-plugin/plugin.json`;
- `skills/` belongs at plugin root, not inside `.claude-plugin/`;
- local `--plugin-dir` is a development/test route, while marketplace/source distribution is a separate workflow.

`DOC-CL-03` — `https://support.claude.com/en/articles/12512180-use-skills-in-claude`

- claude.ai custom skills are uploaded as a ZIP containing the skill folder;
- current availability and upload permissions depend on plan/admin settings;
- code execution/file creation must be enabled.

`DOC-CL-04` — `https://platform.claude.com/docs/en/agents-and-tools/agent-skills/overview`

- Claude API custom skills require the code-execution tool and `skills-2025-10-02` beta header;
- API runtime has no network access and no runtime package installation;
- Claude Code, claude.ai and API skills are separate surfaces and do not synchronize automatically.

`DOC-CL-05` — `https://platform.claude.com/docs/en/api/beta/skills/create`

- the current Skills endpoint exists as a beta API surface; exact request schema must be rechecked at P-13.

`DOC-CL-06` — `https://claude.com/docs/cowork/guide/plugins`

- Cowork exposes a plugin installation lifecycle distinct from Claude Code raw skills; availability remains environment/account dependent.

## 3. OpenAI/ChatGPT/Codex

`DOC-OAI-01` — `https://learn.chatgpt.com/docs/build-skills`

- standalone skills are documented for ChatGPT desktop, Codex CLI and Codex IDE;
- OpenAI skill shape includes optional `agents/openai.yaml` for UI/invocation/dependency metadata;
- Codex repository/user discovery includes `.agents/skills` and `$HOME/.agents/skills`;
- plugins distribute skills across ChatGPT web/desktop/mobile and Codex supported surfaces.

`DOC-OAI-02` — `https://developers.openai.com/plugins`

- OpenAI plugins use the universal plugin directory and host skills/connectors for supported ChatGPT/Codex surfaces;
- a plugin lifecycle is distinct from a standalone raw skill.

`DOC-OAI-03` — `https://developers.openai.com/plugins/build/plugins`

- every plugin has `.codex-plugin/plugin.json` and may contain `skills/<name>/SKILL.md` at plugin root;
- official authoring/distribution uses a plugin directory and marketplace/source workflow;
- no generic ZIP-upload contract is established for OpenAI plugins.

Contract effect: the OpenAI ZIP remains a deterministic delivery archive whose extracted directory enters the official marketplace/source lifecycle; it is not described as a direct upload package.

## 4. Accessibility baseline

`DOC-A11Y-01` — `https://www.w3.org/TR/WCAG22/`

- WCAG 2.2 is a W3C Recommendation and the project targets its applicable Level AA success criteria;
- relevant requirements include text alternatives, meaningful sequence, use of color, minimum contrast, non-text contrast, keyboard access, focus visibility/order and motion control.

`DOC-A11Y-02` — `https://www.w3.org/WAI/WCAG22/Understanding/contrast-minimum.html`

- the project adopts 4.5:1 for normal text and 3:1 for large text.

`DOC-A11Y-03` — `https://www.w3.org/WAI/WCAG22/Understanding/non-text-contrast.html`

- the project adopts 3:1 for meaningful graphical/UI boundaries against adjacent colors.

`DOC-A11Y-04` — `https://www.w3.org/WAI/WCAG22/Understanding/animation-from-interactions.html`

- non-essential motion triggered by interaction must be suppressible; the project additionally requires a complete static/reduced-motion state.

## 5. Evidence limits

- Documentation proves an official route exists; it does not prove this future artifact installs or behaves correctly.
- All current P-02 surface cells therefore remain `conditional` until exact-artifact P-13 smoke evidence, except routes explicitly marked `unsupported`.
- Account, plan, admin, beta and runtime conditions remain external and must be recorded with each smoke run.
- Documentation must be re-verified at P-13 because paths, schemas and availability can change.
