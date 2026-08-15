# P-01 official platform evidence inventory

**Record ID:** `P01-PLATFORM-EVIDENCE-1`  
**Verified:** 2026-08-15  
**Source rule:** only first-party Anthropic/OpenAI documentation and the official Agent Skills specification are used.  
**Boundary:** this inventory supplies evidence for the P-02 surface matrix; it does not assign `supported`, `conditional`, or `unsupported` status.

## 1. Agent Skills specification

Official source: `https://agentskills.io/specification`

Verified facts:

- a skill is a directory with required `SKILL.md`; `scripts/`, `references/` and `assets/` are optional conventions;
- `SKILL.md` contains YAML frontmatter and Markdown;
- required fields are `name` and `description`;
- `name` is 1–64 characters, lowercase letters/numbers/hyphens, cannot begin/end with a hyphen or contain consecutive hyphens, and must match the parent directory;
- `description` is 1–1024 characters and should state what the skill does and when to use it;
- optional specification fields are `license`, `compatibility`, string-to-string `metadata`, and experimental `allowed-tools`;
- progressive disclosure loads metadata first, full instructions on activation, and resources only when needed;
- the specification recommends a `SKILL.md` under 500 lines and relative, shallow file references;
- `skills-ref validate` is the reference validation route.

P-01 consequence: the provider-neutral core can target the common Agent Skills shape, but host-specific metadata must remain an overlay. No package compatibility is claimed until P-02/P-13 testing.

## 2. Anthropic / Claude

### 2.1 Claude Code raw skills

Official source: `https://code.claude.com/docs/en/skills`

Verified facts:

- personal path: `~/.claude/skills/<skill-name>/SKILL.md`;
- project path: `.claude/skills/<skill-name>/SKILL.md`;
- plugin path: `<plugin>/skills/<skill-name>/SKILL.md`;
- project skills can be committed with `.claude/skills/`;
- Claude Code supports progressive supporting files and recommends keeping `SKILL.md` focused;
- Claude Code accepts host-specific frontmatter beyond the portable Agent Skills fields, while Claude/Cowork upload validates a narrower allowed set;
- plugin skills are namespaced; raw skills and plugin skills have different conflict/activation behavior.

P-01 consequence: a raw-skill artifact and a Claude plugin are distinct install surfaces. Claude-only frontmatter cannot be placed in the provider-neutral core unless it also satisfies the common specification and other hosts.

### 2.2 Claude Code plugins

Official source: `https://code.claude.com/docs/en/plugins`

Verified facts:

- plugin identity is defined at `.claude-plugin/plugin.json`;
- only `plugin.json` belongs under `.claude-plugin/`;
- `skills/`, `commands/`, `agents/`, `hooks/` and other components belong at plugin root;
- the standard multi-skill layout is `skills/<name>/SKILL.md`;
- a single-skill plugin may place `SKILL.md` at plugin root, but the multi-skill layout is recommended when growth is possible;
- `--plugin-dir` is a development/test path; marketplace distribution is a separate lifecycle.

P-01 consequence: the target content placement in `PROJECT-CONTRACT.md` is consistent with the documented plugin-root structure. Exact archive envelope and marketplace installation still require P-02/P-13 evidence and smoke tests.

### 2.3 Claude web, chat, Cowork and account skills

Official sources:

- `https://support.claude.com/en/articles/12512180-use-skills-in-claude`
- `https://claude.com/docs/skills/overview`
- `https://claude.com/docs/cowork/guide/plugins`

Verified facts:

- custom account skills are uploaded as a ZIP containing the skill folder;
- uploaded skills can be enabled or disabled; sharing/admin behavior depends on plan and organization settings;
- skills require code execution to be enabled on the documented account surfaces;
- skill sharing works in chat and Cowork where enabled;
- Cowork can install plugin packages from its plugin UI.

P-01 consequence: Claude account-skill ZIP and Claude plugin package are different artifacts/surfaces. The Universal ZIP may be reusable only after its exact envelope is validated; P-01 does not claim this.

### 2.4 Claude API

Official sources:

- `https://platform.claude.com/docs/en/api/beta/skills/create`
- `https://platform.claude.com/docs/en/agents-and-tools/agent-skills/overview`
- `https://platform.claude.com/docs/en/managed-agents/skills`

Verified facts:

- custom skills can be uploaded through the Skills API as a ZIP or files;
- uploaded files must form one top-level skill directory with `SKILL.md` at that directory's root;
- the Skills API currently uses a beta header documented as `skills-2025-10-02` for direct API calls;
- API skills run in a sandboxed container with no network access and no runtime package installation;
- uploaded skills receive a `skill_*` identifier and are attached to supported agent/API workflows.

P-01 consequence: no-network and no-runtime-install constraints align with the project's portable core. API availability is an evidence row for P-02, not a promise that the planned ZIP is already API-ready.

## 3. OpenAI / ChatGPT / Codex

### 3.1 Standalone skills

Official source: `https://learn.chatgpt.com/docs/build-skills` (canonical redirect: `https://developers.openai.com/codex/skills`)

Verified facts:

- standalone skills are documented for the ChatGPT desktop app, Codex CLI and Codex IDE extension;
- skill directory contains `SKILL.md` plus optional `scripts/`, `references/`, `assets/` and `agents/openai.yaml`;
- `name` and `description` are required;
- activation can be explicit or description-based implicit matching;
- Codex scans `.agents/skills` from current directory through repository root, plus user/admin/system locations;
- user path is `$HOME/.agents/skills`; repository roots use `.agents/skills`;
- `agents/openai.yaml` is optional OpenAI-specific metadata for appearance, invocation policy and tool dependencies;
- OpenAI recommends plugins for reusable distribution.

P-01 consequence: `agents/openai.yaml` is an OpenAI overlay, not provider-neutral runtime core. The Universal folder envelope planned for extraction under `.agents/skills/` is consistent with documented local discovery, subject to P-13 smoke tests.

### 3.2 OpenAI plugins

Official sources:

- `https://developers.openai.com/plugins`
- `https://developers.openai.com/plugins/concepts/plugins`
- `https://developers.openai.com/plugins/build/plugins`

Verified facts:

- ChatGPT and Codex share a universal plugin directory on documented supported surfaces;
- plugins work in Chat and Work on ChatGPT web, desktop and mobile, in Codex within the ChatGPT desktop app, and in Codex CLI;
- plugins are not supported in the Codex IDE extension; standalone skills are the documented skill route there;
- every plugin has `.codex-plugin/plugin.json`;
- only `plugin.json` belongs under `.codex-plugin/`; `skills/`, assets and optional integrations belong at plugin root;
- a skill belongs at `skills/<skill-name>/SKILL.md`;
- local/private authoring uses marketplace metadata at repository or user scope; installation loads a cached copy;
- official package documentation describes a plugin directory and marketplace/source workflow, not a generic ZIP upload contract.

P-01 consequence: the planned OpenAI content placement matches current directory structure. The exact OpenAI archive envelope remains unconfirmed and must not be advertised or frozen before P-02/P-13.

## 4. Evidence-ready surface inventory for P-02

This is an inventory, not the final support matrix.

| Surface candidate | Artifact candidate | Official evidence available | P-01 status |
|---|---|---|---|
| Claude Code personal/project | raw skill directory | Claude skills docs | evidence-ready |
| Claude Code plugin | Claude plugin directory | Claude plugin docs | evidence-ready |
| Claude Code web/cloud session | repository `.claude/skills` or declared plugin | Claude web/cloud docs | evidence-ready; environment-dependent |
| claude.ai chat | uploaded custom skill ZIP | Claude Help/skills docs | evidence-ready; account/setting-dependent |
| Claude Cowork | account skill or plugin | Claude skills/Cowork plugin docs | evidence-ready; account/setting-dependent |
| Claude API / managed agents | Skills API upload | Claude Platform/API docs | evidence-ready; beta/API-dependent |
| ChatGPT web/mobile Chat and Work | skill bundled in OpenAI plugin | OpenAI plugin docs | evidence-ready; plugin/account-dependent |
| ChatGPT desktop Skills | standalone skill | OpenAI build-skills docs | evidence-ready |
| Codex in ChatGPT desktop | OpenAI plugin or standalone skill | OpenAI plugin/build-skills docs | evidence-ready |
| Codex CLI | OpenAI plugin or `.agents/skills` skill | OpenAI plugin/build-skills docs | evidence-ready |
| Codex IDE extension | standalone `.agents/skills` skill | OpenAI build-skills docs; plugin docs explicitly exclude plugins | evidence-ready |

P-02 must add install method, trigger, output, fallback, account/environment conditions and actual support status for every cell.

## 5. Residual platform uncertainties

These do not justify assumptions:

1. OpenAI's current official plugin documentation does not define ZIP as the generic install envelope; it defines a plugin directory plus marketplace/source distribution. P-02/P-13 must choose an envelope only with official evidence and a smoke test.
2. Claude account-skill ZIP, Claude Code plugin and Claude API skill upload have different lifecycles. A single ZIP cannot be called compatible across them without separate validation.
3. Plan/account/admin/code-execution and beta-header requirements are external conditions and must appear explicitly in the P-02 matrix.
4. Platform docs and schemas are mutable. Re-verify them at P-13 immediately before package construction.
5. Host-specific frontmatter differs. The common portable subset remains the Agent Skills fields; platform-only metadata belongs in overlays.
