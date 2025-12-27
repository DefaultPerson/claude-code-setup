# Claude Code Setup

Starter kit for [Claude Code](https://docs.anthropic.com/en/docs/claude-code) with hooks, MCP servers, and productivity tools.

## Features

- **Security Guard** — blocks dangerous commands (`rm -rf /`, `.env` writes, privileged docker, etc.)
- **TTS Notifications** — voice alerts when Claude finishes or needs input (ElevenLabs / OpenAI / pyttsx3)
- **Status Line** — shows project, branch, model, and context usage
- **Pre-Compact Hook** — auto-saves session backup before context compaction
- **Persistent Memory** — `.claude/memory.md` survives between sessions
- **Slash Commands** — `/research`, `/ultrathink`, `/load-context`, `/validation`
- **MCP Servers** — context7, chrome-devtool
- **Cross-platform** — Linux, macOS, Windows

---

## Prerequisites

- **Node.js** 18+
- **uv** (Python package manager)
- **ffmpeg** or **mpv** (audio player for TTS)
- **Claude Code CLI**: `npm install -g @anthropic-ai/claude-code`

---

## Quick Start

```bash
git clone https://github.com/user/claude-code-setup.git
cd claude-code-setup

cp .env.example .env
cp .mcp.json.sample .mcp.json              # Windows: .mcp.json.windows
cp .claude/settings.example.json .claude/settings.json
```

Edit files — replace paths and API keys (see `.env.example` and `.mcp.json.sample`).

Replace `/home/user/project` in `settings.json` with your path:

```bash
sed -i 's|/home/user/project|'"$(pwd)"'|g' .claude/settings.json   # Linux
sed -i '' 's|/home/user/project|'"$(pwd)"'|g' .claude/settings.json # macOS
```

Start Claude:

```bash
claude
```

---

## Global Installation (Optional)

Apply hooks to **all projects**:

```bash
cp -r .claude/hooks ~/.claude/hooks
cp .claude/settings.example.json ~/.claude/settings.json
sed -i 's|/home/user/project/.claude|'"$HOME"'/.claude|g' ~/.claude/settings.json
```

---

## Shell Aliases (Optional)

Add to `.bashrc` / `.zshrc` / PowerShell profile:

```bash
alias cc="claude"
alias ccr="claude --resume"
alias ccp='CLAUDE_CONFIG_DIR=$HOME/.claude-personal claude'
alias ccd='claude --dangerously-skip-permissions'
alias ccdr='claude --dangerously-skip-permissions --resume'

# Tmux grid for parallel sessions
tg() {
    n=${1:-2}
    tmux new-session -d -s "grid-$$"
    for ((i=1; i<n; i++)); do
        tmux split-window -t "grid-$$"
        tmux select-layout -t "grid-$$" tiled
    done
    tmux attach -t "grid-$$"
}

# Add pane to current grid
ta() {
    tmux split-window
    tmux select-layout tiled
}
```

---

## Tips

**Terminal as Editor Tab (VS Code)**: `Cmd/Ctrl+Shift+P` → "Terminal: Create New Terminal in Editor Area" — opens terminal as a tab next to your code, not in the bottom panel.

---

## Troubleshooting

If something doesn't work — just ask Claude Code to fix it. Describe the problem and Claude will diagnose and resolve it.

---

## References

- [disler/claude-code-hooks-mastery](https://github.com/disler/claude-code-hooks-mastery)
- [coleam00/context-engineering-intro](https://github.com/coleam00/context-engineering-intro)
- [DenisSergeevitch/chatgpt-custom-instructions](https://github.com/DenisSergeevitch/chatgpt-custom-instructions)

---

My tg channel >> [@agentSShit](https://t.me/agentSShit)
