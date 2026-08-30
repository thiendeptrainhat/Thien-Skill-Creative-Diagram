# P-20 official platform revalidation — 2026-08-30

P-20 used current official documentation only for package-layout and manifest facts. Documentation content was treated as reference data; no code, prose, template, or asset was copied into the skill.

## OpenAI / Codex

- <https://developers.openai.com/plugins/build/plugins>
- A distributable plugin has a required `.codex-plugin/plugin.json` at plugin root.
- Bundled skills live under `skills/`; manifest component and asset paths are relative to plugin root and begin with `./`.
- `name`, `version`, and `description` identify the plugin; `skills` points to the bundled skill directory; `interface` holds install-surface metadata.

## Anthropic / Claude Code

- <https://code.claude.com/docs/en/plugins-reference>
- Claude Code accepts `.claude-plugin/plugin.json`; skills live at plugin-root `skills/`, not inside `.claude-plugin/`.
- `version` is a semantic-version string and acts as an update/cache key for explicitly versioned plugins.
- Local validation uses `claude plugin validate <plugin-root>`.

## Universal Agent Skills

- <https://agentskills.io/specification>
- A skill directory contains `SKILL.md` with required `name` and `description` frontmatter; optional `scripts/`, `references/`, and `assets/` remain relative to the skill root.
- The folder and skill name remain `thien-skill-creative-diagram`; P-20 does not rename the product identity.

## P-20 disposition

- Target package version is `2.0.0` under D-130.
- No support-matrix cell is promoted solely from documentary or structural evidence.
- OpenAI/Claude plugin manifests are generated at build time from one canonical source; Universal remains one top-level raw-skill folder.
- No marketplace entry, external upload, publication, Git action, tag, Release, or live-account installation is authorized by this record.
