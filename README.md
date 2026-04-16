# agent-setup

Universal setup for [Claude Code](https://docs.anthropic.com/en/docs/claude-code), [OpenAI Codex CLI](https://developers.openai.com/codex/cli), and [OpenCode](https://opencode.ai) — security hooks, notifications, status line, and productivity commands.

## Features

- **Security Guard** — blocks dangerous commands (`rm -rf /`, credential reads, privileged docker, etc.)
- **TTS Notifications** — cached voice alerts when Claude finishes or needs input
- **Desktop Notifications** — native OS notifications (Linux, macOS, Windows)
- **Status Line** — project, branch, model, context usage, rate limits
- **Slash Commands** — `/research`, `/ultrathink`, `/commit`, `/push-and-pr`, `/prime`, `/publish`, `/release`
- **Cross-platform** — Linux, macOS, Windows

---

## OpenCode (Fireworks + GLM-5.1)

Fastest path — one command, one API key, done.

**Linux / macOS / WSL (bash):**

```bash
curl -fsSL https://raw.githubusercontent.com/DefaultPerson/agent-setup/feat/opencode-support/scripts/install-opencode.sh | bash
```

**Windows (PowerShell 5.1+):**

```powershell
irm https://raw.githubusercontent.com/DefaultPerson/agent-setup/feat/opencode-support/scripts/install-opencode.ps1 | iex
```

If the execution policy blocks it:

```powershell
powershell -ExecutionPolicy Bypass -Command "irm https://raw.githubusercontent.com/DefaultPerson/agent-setup/feat/opencode-support/scripts/install-opencode.ps1 | iex"
```

(flip the branch segment to `master` after the PR is merged)

**What it does:**

1. Installs the `opencode` CLI if missing (via `opencode.ai/install`)
2. Writes `~/.config/opencode/opencode.json` with Fireworks as the provider, **GLM-5.1** as the default model (slug auto-resolved from Fireworks' live `/v1/models` catalog), **DeepSeek V3.2** as the small/background model
3. Copies 7 slash commands (`/commit`, `/push-and-pr`, `/prime`, `/research`, `/ultrathink`, `/publish`, `/release`) to `~/.config/opencode/commands/` — reused verbatim from `.claude/commands/` (the format is byte-compatible)
4. Installs `AGENTS.md` as global instructions at `~/.config/opencode/AGENTS.md`
5. Enables the `context7` MCP server for library docs lookup
6. Prompts once for your `FIREWORKS_API_KEY` ([get one here](https://fireworks.ai/account/api-keys)) and persists it to your shell rc file
7. Runs a smoke test against Fireworks to confirm auth + model availability

**Prerequisites:**
- Linux / macOS / WSL: `curl`, `bash`, `python3`. No `jq`.
- Windows: PowerShell 5.1 (built-in on Windows 10/11) + one of `winget` (pre-installed on Windows 10 1809+/11), `scoop`, or `npm`. No Python or bash required — the PS installer is self-contained and uses `Invoke-RestMethod` for all network/JSON work. Config lands in `%USERPROFILE%\.config\opencode\`, and `FIREWORKS_API_KEY` is persisted to the User environment via `[Environment]::SetEnvironmentVariable(..., 'User')`.

**Then:**

```bash
opencode
# /models → GLM-5.1 is already selected
# /commit, /prime, /ultrathink, etc. work identically to the Claude Code setup
```

**Shell aliases** — add to `.bashrc` / `.zshrc`:

```bash
alias oc="opencode" ocr="opencode --continue"
```

**Limitations vs. Claude Code:**

- **No `guard.py` / PreToolUse security hook** — OpenCode has no event hooks. The config sets `permission.bash: "ask"` as the minimum safeguard (every shell command asks before running).
- **No TTS notifications / custom statusline** — OpenCode has a built-in minimal statusline; no cached-MP3 voice alerts.
- Everything else (slash commands, AGENTS.md, MCP servers, multi-agent workflows) ports 1:1.

**Rollback / uninstall:**

Linux / macOS:
```bash
rm -rf ~/.config/opencode ~/.opencode
sed -i '/FIREWORKS_API_KEY/d' ~/.bashrc ~/.zshrc 2>/dev/null || true
```

Windows (PowerShell):

> [!WARNING]
> **Destructive — read before pasting.** `Remove-Item -Recurse -Force` permanently deletes the target directory with no prompt and no Recycle Bin. Double-check the path is exactly `...\.config\opencode` before running — a typo like `...\.config` (without `\opencode`) wipes every dotfile config under `.config`. Dry-run first with `-WhatIf`:
>
> ```powershell
> Remove-Item -Recurse -Force "$env:USERPROFILE\.config\opencode" -WhatIf
> ```

```powershell
Remove-Item -Recurse -Force "$env:USERPROFILE\.config\opencode"
[Environment]::SetEnvironmentVariable('FIREWORKS_API_KEY', $null, 'User')
winget uninstall --exact --id SST.opencode    # optional: removes the CLI
```

---

## Claude Code

### Setup

Paste into Claude Code — or follow the steps manually:

```
Prerequisites: Node.js 18+, uv (python package manager), ffmpeg or mpv (audio for TTS).

1. git clone https://github.com/DefaultPerson/agent-setup.git && cd agent-setup
2. cp -r .claude/hooks ~/.claude/hooks
3. cp -r .claude/commands ~/.claude/commands
4. cp .claude/settings.example.json ~/.claude/settings.json
   # Windows: cp .claude/settings.local.json.windows "$env:USERPROFILE/.claude/settings.json"
5. cp CLAUDE.md ~/.claude/CLAUDE.md (optional — author's coding style and rules)
6. Install recommended plugins (see below)
7. Add shell aliases (see below)
8. Ask me for any preferences
9. Verify everything works
10. Delete agent-setup (repo no longer needed after setup)
```

### Recommended Plugins

LSP, context7, frontend-design are available in the default marketplace — install via `/plugin` → search.

```bash
# Browser automation for AI agents
# https://github.com/vercel-labs/agent-browser
/plugin marketplace add vercel-labs/agent-browser
/plugin install agent-browser@agent-browser

/reload-plugins
```

### Shell Aliases

Add to `.bashrc` / `.zshrc`:

```bash
alias cc="claude" ccr="claude --resume" ccd="claude --dangerously-skip-permissions" ccdr="claude --dangerously-skip-permissions --resume"
```

---

## Codex CLI

### Setup

Paste into Codex — or follow the steps manually:

```
Prerequisites: Node.js 18+, uv (python package manager), ffmpeg or mpv (audio for TTS).

1. git clone https://github.com/DefaultPerson/agent-setup.git && cd agent-setup
2. cp -r .codex/hooks ~/.codex/hooks
3. cp .codex/hooks.json ~/.codex/hooks.json
4. cp .codex/config.toml.sample ~/.codex/config.toml
5. cp AGENTS.md ~/.codex/AGENTS.md (optional — author's coding style and rules)
6. Edit ~/.codex/config.toml — set API keys, model preferences
7. Add MCP servers (see below)
8. Add shell aliases (see below)
9. Verify everything works
10. Delete agent-setup (repo no longer needed after setup)
```

**Key differences from Claude Code:**
- Config: `config.toml` (TOML) instead of `settings.json`
- Instructions: `AGENTS.md` instead of `CLAUDE.md`
- Status line: built-in `/statusline` picker — no custom script needed
- Plugins: installed via interactive UI, not CLI command
- MCP: configured in `config.toml` `[mcp_servers]` section or via `codex mcp add`

### Recommended Plugins

- [agent-browser](https://github.com/vercel-labs/agent-browser) — browser automation for AI agents
- [context7](https://github.com/upstash/context7) — library documentation lookup
- [frontend-design](https://github.com/anthropics/claude-plugins-official/tree/main/plugins/frontend-design) — production-grade frontend generation

### Shell Aliases

Add to `.bashrc` / `.zshrc`:

```bash
alias cx="codex" cxr="codex resume" cxd="codex --yolo" cxdr="codex resume --yolo"
```

---

## Tips

> [!TIP]
> **Terminal as Editor Tab (VS Code)**: `Cmd/Ctrl+Shift+P` → "Terminal: Create New Terminal in Editor Area" — opens terminal as a tab next to your code, not in the bottom panel.

> [!TIP]
> **If something doesn't work — just ask Claude Code/Codex to fix it.** Describe the problem and it will diagnose and resolve it.

> [!TIP]
> **Create SKILLs for repetitive tasks.** Instead of doing any task manually, create a SKILL for it. First version gives junior-mid level results. Then iterate until it matches your quality — 100-1000x time savings.

## License

MIT
