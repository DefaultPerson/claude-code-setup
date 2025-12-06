# Claude Code Setup

Starter kit for [Claude Code](https://docs.anthropic.com/en/docs/claude-code) with security hooks, TTS notifications, and MCP servers.

## Features

- **Security Guard** - blocks dangerous commands (`rm -rf /`, `.env` writes, privileged docker, etc.)
- **TTS Notifications** - voice alerts when Claude finishes or needs input (ElevenLabs/OpenAI/pyttsx3)
- **Status Line** - shows project, branch, model, and context usage
- **MCP Servers** - sequential-thinking, context7, linear integration
- **Cross-platform** - works on Linux, macOS, and Windows

## Prerequisites

- [Claude Code CLI](https://docs.anthropic.com/en/docs/claude-code/getting-started)
- [uv](https://docs.astral.sh/uv/) (Python package manager)
- Node.js (for MCP servers via npx)
- Audio player: `ffplay` (ffmpeg), `mpv`, or `sox` for TTS

## Installation

### 1. Install Claude Code

```bash
npm install -g @anthropic-ai/claude-code
```

### 2. Clone this repository

```bash
git clone https://github.com/DefaultPerson/claude-code-setup.git
cd claude-code-setup
```

### 3. Configure environment

```bash
cp .env.example .env
# Edit .env with your API keys
```

### 4. Configure MCP servers

Linux/macOS:
```bash
cp .mcp.json.sample .mcp.json
```

Windows:
```powershell
copy .mcp.json.windows .mcp.json
copy .claude\settings.local.json.windows .claude\settings.local.json
```

Edit `.mcp.json` with your API keys.

## Configuration

### `.env` file

```bash
TTS_LANGUAGE=en                    # en or ru
TTS_MODE=static                    # static or dynamic
ELEVENLABS_API_KEY=                # Best quality TTS
OPENAI_API_KEY=                    # Required for dynamic mode
```

### `.mcp.json` file

```json
{
  "mcpServers": {
    "sequential-thinking": {
      "command": "npx",
      "args": ["-y", "@modelcontextprotocol/server-sequential-thinking"]
    },
    "context7": {
      "command": "npx",
      "args": ["-y", "@upstash/context7-mcp", "--api-key", "YOUR_KEY"]
    }
  }
}
```

## Hooks

| Hook | Purpose |
|------|---------|
| `guard.py` | PreToolUse - blocks dangerous bash commands |
| `notification.py` | Stop/Notification - TTS voice alerts |
| `statusline.py` | Status line with context usage |

## TTS Providers

Priority order:
1. **ElevenLabs** - best quality, requires `ELEVENLABS_API_KEY`
2. **OpenAI** - good quality, requires `OPENAI_API_KEY`
3. **pyttsx3** - offline fallback, no API key needed

## License

MIT

---

https://t.me/agentSShit
