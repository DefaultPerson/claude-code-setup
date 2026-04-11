# .opencode/

Template source consumed by `scripts/install-opencode.sh`. You don't read or copy files from here directly — run the one-liner from the repo root README instead:

```bash
curl -fsSL https://raw.githubusercontent.com/DefaultPerson/agent-setup/master/scripts/install-opencode.sh | bash
```

Files:

- `opencode.json` — OpenCode config template. `{{GLM_MODEL_ID}}` placeholders are rewritten by the installer with the live GLM-5.1 slug from Fireworks' `/v1/models` catalog (slugs bump every few weeks; pinning would rot).

Slash commands and global instructions are **not duplicated** here: the installer copies them from `../.claude/commands/` and `../AGENTS.md` because the OpenCode command format is byte-compatible with the Claude Code one.

See `../README.md` → "OpenCode (Fireworks + GLM-5.1)" for full docs.
