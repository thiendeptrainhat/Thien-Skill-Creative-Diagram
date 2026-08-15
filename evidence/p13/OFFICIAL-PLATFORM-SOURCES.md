# P-13 official platform sources

**Checked:** 2026-08-15  
**Scope:** current package envelope, manifest, skill metadata and local install/discovery contracts  
**Source rule:** official platform documentation only

## Claude

- <https://code.claude.com/docs/en/plugins>
- <https://code.claude.com/docs/en/plugins-reference>
- <https://code.claude.com/docs/en/skills>

Current official documentation confirms that a Claude Code plugin places its optional manifest at `.claude-plugin/plugin.json`, keeps `skills/` at plugin root, and supports local development validation through `claude plugin validate` and loading through `--plugin-dir`. The plugin manifest requires only `name`; this project also supplies version, description, author and an explicit `./skills/` component path. No undocumented Claude icon field is introduced. Standalone Claude skills remain discoverable from personal `~/.claude/skills/<skill-name>/` and project `.claude/skills/<skill-name>/` locations.

## OpenAI / ChatGPT / Codex

- <https://developers.openai.com/plugins/build/plugins>
- <https://learn.chatgpt.com/docs/build-skills>

Current official documentation confirms that an OpenAI plugin requires `.codex-plugin/plugin.json`, keeps `skills/` and presentation `assets/` at plugin root, and may declare `interface.composerIcon` and `interface.logo` using relative asset paths. The minimal skill-plugin manifest uses `name`, version, description and `skills`; this project adds only supported presentation and author fields. Standalone Codex skills remain discoverable from repository/user `.agents/skills` locations. `agents/openai.yaml` may provide skill UI metadata with icon paths relative to the skill directory.

## Open Agent Skills specification

- <https://agentskills.io/specification>

The current specification requires a skill directory with `SKILL.md`; frontmatter requires `name` and `description`, and the `name` must match the parent directory using lowercase letters, digits and hyphens. The canonical skill already uses this common subset, so P-13 does not alter its runtime frontmatter.

## P-13 application

- Claude ZIP: one top-level plugin folder, `.claude-plugin/plugin.json`, nested `skills/thien-skill-creative-diagram/`, no brand asset and no `agents/openai.yaml`.
- OpenAI ZIP: one top-level plugin folder, `.codex-plugin/plugin.json`, nested canonical skill, base `agents/openai.yaml`, and the two D-028 assets at plugin-root `assets/brand/`; the plugin manifest references those assets.
- Universal ZIP: one top-level skill folder suitable for extraction beneath `.agents/skills/`, with the same core/legal bytes, `agents/openai.yaml` generated from the canonical overlay plus relative icon fields, and the same two D-028 assets at `assets/brand/`.
- ZIP files are deterministic delivery archives. No direct-upload or marketplace compatibility is claimed without the exact installed-surface evidence required by the approved P-02 matrix.

No community schema, blog, marketplace copy, third-party template or upstream implementation material was used.
