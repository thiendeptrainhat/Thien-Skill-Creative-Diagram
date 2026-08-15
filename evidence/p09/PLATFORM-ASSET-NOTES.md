# P-09 Platform Asset Notes

**Checked:** 2026-08-15  
**Scope:** current official background used only to avoid inventing package destinations in P-09

## Claude

Anthropic's official Claude Code plugin reference documents `name` as the only required `plugin.json` field and lists current metadata fields such as `displayName`, version, description, author, homepage, repository, license and keywords. It does not document a plugin icon field in that manifest. P-09 therefore does not invent a Claude icon key or final destination.

Official sources:

- <https://code.claude.com/docs/en/plugins>
- <https://code.claude.com/docs/en/plugins-reference>

## OpenAI/Codex

The official bundled `skill-creator` runtime reference for `agents/openai.yaml` supports relative `interface.icon_small` and `interface.icon_large` paths, recommends the skill's `./assets/` directory, and gives a 400px PNG only as an example. The reference does not establish the rendered UI pixel size or final marketplace/package mapping.

Evidence snapshot:

- `skill-creator/references/openai_yaml.md` SHA-256 `ffac39318e408108141d40f820968e59f70434a891694f9bf1d25be8237b150c`.

P-09 consequently includes a 400px candidate but does not edit `agents/openai.yaml`. Exact `icon_small`/`icon_large`, Claude/OpenAI/Universal destination mapping and installed-surface behavior remain P-13 responsibilities after owner approval and G-06.

No community schema, blog, copied marketplace asset or third-party icon source was used.
