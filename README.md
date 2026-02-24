# Claude Code Setup

My universal setup for [Claude Code](https://docs.anthropic.com/en/docs/claude-code) with hooks, MCPs, etc...

## 📑 Contents

- [Claude Code Setup](#claude-code-setup)
  - [📑 Contents](#-contents)
  - [🚀 Features](#-features)
  - [📋 Prerequisites](#-prerequisites)
  - [⚡ Quick Start](#-quick-start)
  - [🔌 LSP Plugins (Optional)](#-lsp-plugins-optional)
  - [🌍 Global Installation (Optional+Recommended)](#-global-installation-optionalrecommended)
  - [💻 Shell Aliases (Optional)](#-shell-aliases-optional)
  - [💡 Tips](#-tips)
  - [🌐 Agent Browser](#-agent-browser)

## 🚀 Features

- **Security Guard** — blocks dangerous commands (`rm -rf /`, `.env` writes, privileged docker, etc.)
- **TTS Notifications** — voice alerts when Claude finishes or needs input (ElevenLabs / OpenAI / pyttsx3)
- **Desktop Notifications** — native OS notifications (Linux, macOS, Windows)
- **Status Line** — shows project, branch, model, and context usage
- **Slash Commands** — `/research`, `/ultrathink`, `/commit`, `/push-and-pr`, `/prime`, `/publish`, `/release`
- **MCP Servers** — context7
- **LSP Plugins** — TypeScript, Python (Pyright), Go (gopls) for better code understanding
- **Cross-platform** — Linux, macOS, Windows

---

## 📋 Prerequisites

- **Node.js** 18+
- **uv** (Python package manager)
- **ffmpeg** or **mpv** (audio player for TTS)
- **Claude Code CLI**: `npm install -g @anthropic-ai/claude-code`

---

## ⚡ Quick Start

```bash
git clone https://github.com/user/claude-code-setup.git
cd claude-code-setup

cp .env.example .env
cp .mcp.json.sample .mcp.json              # Windows: .mcp.json.windows
cp .claude/settings.example.json .claude/settings.json
```

Edit files — replace paths and API keys (see `.env.example` and `.mcp.json.sample`).

> [!NOTE]
> `.env` is optional — without it, cached TTS phrases will be used. Safe to delete if you don't need dynamic TTS or custom API keys.

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

## 🔌 LSP Plugins (Optional)

Enable LSP for better code analysis (types, definitions, errors):

```bash
claude /install-plugin typescript-lsp@claude-plugins-official
claude /install-plugin pyright-lsp@claude-plugins-official
claude /install-plugin gopls-lsp@claude-plugins-official
```

Requires language servers installed: `npm i -g typescript`, `pip install pyright`, `go install golang.org/x/tools/gopls@latest`.

---

## 🌍 Global Installation (Optional+Recommended)

Apply hooks to **all projects**:

```bash
cp -r .claude/hooks ~/.claude/hooks
cp .claude/settings.example.json ~/.claude/settings.json
sed -i 's|/home/user/project/.claude|'"$HOME"'/.claude|g' ~/.claude/settings.json
```

---

## 💻 Shell Aliases (Optional)

Add to `.bashrc` / `.zshrc` / PowerShell profile:

```bash
alias cc="claude"
alias ccr="claude --resume"
alias ccd='claude --dangerously-skip-permissions'
alias ccdr='claude --dangerously-skip-permissions --resume'

# Tmux grid: tg (4 panes), tg -n 3 (3 panes)
tg() {
    local n=4
    while getopts "n:" opt; do
        case $opt in n) n=$OPTARG ;; esac
    done
    tmux new-session -d -s "grid-$$"
    for ((i=1; i<n; i++)); do
        tmux split-window -t "grid-$$"
        tmux select-layout -t "grid-$$" tiled
    done
    tmux attach -t "grid-$$"
}

# 2 panes side-by-side
tg2() {
    tmux new-session -d -s "split-$$"
    tmux split-window -h -t "split-$$"
    tmux attach -t "split-$$"
}

# Add pane to current grid
ta() {
    tmux split-window
    tmux select-layout tiled
}

alias tg3='tg -n 3'
```

---

## 💡 Tips

> [!TIP]
> **Terminal as Editor Tab (VS Code)**: `Cmd/Ctrl+Shift+P` → "Terminal: Create New Terminal in Editor Area" — opens terminal as a tab next to your code, not in the bottom panel.

> [!TIP]
> **If something doesn't work — just ask Claude Code to fix it.** Describe the problem and Claude will diagnose and resolve it.

---

## 🌐 Agent Browser

Better alternative to Playwright MCP: **[agent-browser](https://github.com/vercel-labs/agent-browser)** | [skill](https://github.com/vercel-labs/agent-browser/tree/main/skills/agent-browser)

---

🤙 My tg channel >> [link](https://t.me/agentSShit)
