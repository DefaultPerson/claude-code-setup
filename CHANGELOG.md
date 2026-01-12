# Changelog

All notable changes to this project will be documented in this file.

## [Unreleased]

### Changed

- **CLAUDE.md** — added rule to prevent Co-Authored-By in commits

## [0.4.0] - 2025-12-30

### Added

- **HTML Session Viewer** — `pre_compact.py` now generates standalone HTML with markdown rendering, syntax highlighting, and copy buttons per message
- **Theme Toggle** — session viewer supports dark/light theme switching with localStorage persistence (dark default)
- **Notification Stacking Prevention** — desktop notifications replace each other instead of accumulating:
  - Linux: `x-canonical-private-synchronous` and `x-dunst-stack-tag` hints
  - macOS: `terminal-notifier` with `-group` (if installed)
  - Windows: Toast `Tag` and `Group` properties
- **LSP Plugins Section** — README now documents TypeScript, Python (Pyright), Go (gopls) plugins

### Changed

- **CLAUDE.md** — optimized from 128 to 61 lines, merged `dev_guidelines` and `cursor_prefs`, removed redundant sections
- **README.md** — streamlined features list, updated Pre-Compact Hook description
- **.mcp.json.windows** — fixed context7 config to use `env` instead of `--api-key` arg
- **.claude/settings.local.json.windows** — added missing PreCompact and statusLine hooks
- **.env.example** — added `DESKTOP_NOTIFICATIONS` variable

### Removed

- **Persistent Memory** — removed `.claude/memory.md` and related CLAUDE.md section
- **Agents** — removed `sandbox.md` and `worktree-dev.md` (use built-in Task tool instead)
- **`/load-context`** — removed slash command

### Fixed

- **.claude/settings.example.json** — typo `youre` → `your`
- **pre_compact.py** — user messages rendered character-by-character when `content` was string instead of array

## [0.3.0] - 2025-12-29

### Added

- **Desktop Notifications** — cross-platform native notifications (Linux `notify-send`, macOS `osascript`, Windows PowerShell Toast)
- **`DESKTOP_NOTIFICATIONS`** — env variable to enable/disable (default: true)
- **`DEBUG_STATUSLINE`** — env variable to dump statusline input to `/tmp/claude-statusline-debug.json`
- **`tg2`** — tmux alias for 2 horizontal panes (side-by-side)
- **`tg3`** — tmux alias for 3 panes

### Changed

- **statusline.py** — context display changed from `~X%` to `X%+` format
- **notification.py** — integrated desktop notifications with TTS
- **Agents** — added required `description` field to frontmatter (sandbox, worktree-dev)
- **README.md** — updated tmux aliases section with tg2/tg3

### Removed

- **`/load-context`** — removed slash command (use memory.md directly)

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
