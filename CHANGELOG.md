# Changelog

All notable changes to this project will be documented in this file.

## [0.2.0] - 2025-12-27

### Added

- **Sandbox Agent** — isolated development in separate git worktree for safe experimentation
- **Worktree-Dev Agent** — parallel feature development with automatic worktree management
- **`/load-context`** — slash command to load project context and memory on session start
- **`/validation`** — validation commands suite:
  - `/validation:example-validate` — comprehensive codebase validation
  - `/validation:ultimate_validate_command` — generate validation command for any project
- **`pre_compact.py`** — hook that auto-backups conversation transcript before compaction
- **`settings.example.json`** — template with placeholder paths for easy setup
- **`memory.md`** — persistent memory file that survives between sessions
- **Tips section in README** — VS Code terminal-as-tab tip
- **New TTS phrases** — "All done!", "Job complete!", "Task finished!", "Work complete!"

### Changed

- **README.md** — simplified structure, removed verbose install commands, listed all features
- **CLAUDE.md** — added memory management rules, context economy guidelines, orchestration patterns
- **`/research`** — improved with structured output to `research/` directory
- **notification.py** — refactored, cleaner code structure
- **statusline.py** — minor improvements
- **elevenlabs_tts.py** — better error handling
- **docs/tooling.md** — updated tooling reference
- **.env.example** — updated variables documentation
- **.gitignore** — added new exclusions for backups and cache
- **.mcp.json.sample / .mcp.json.windows** — simplified MCP server configs
- **TTS cache** — regenerated audio files with improved quality

### Removed

- **`speckit.validate.md`** — replaced by `/validation` commands
- **`.claude/settings.json`** — moved to template (`settings.example.json`)
- **Verbose README sections** — installation commands, file structure, hooks reference, env variables table

## [0.1.0] - 2025-12-26

### Added

- **Security Guard** (`guard.py`) — blocks dangerous bash commands (`rm -rf /`, `.env` writes, privileged docker)
- **TTS Notifications** (`notification.py`) — voice alerts via ElevenLabs, OpenAI, or pyttsx3
- **Status Line** (`statusline.py`) — shows project, branch, model, context usage
- **MCP Servers** — context7, chrome-devtools, memory, sequential-thinking
- **Windows support** — `.mcp.json.windows`, cross-platform guard hook
- **Shell aliases** — `cc`, `ccr`, `ccd`, `tg`, `ta`
- **CLAUDE.md** — project instructions for Claude Code
