#!/usr/bin/env bash
#
# install-opencode.sh — one-shot installer for OpenCode + Fireworks + GLM-5.1.
#
# Idempotent. Safe to re-run. Works from `curl | bash` (remote raw fetch) or
# from a local clone (`bash scripts/install-opencode.sh`).
#
# Prereqs: curl, bash, python3. No jq.
#
set -euo pipefail

# --- config --------------------------------------------------------------------

REPO="DefaultPerson/agent-setup"
REF="${AGENT_SETUP_REF:-feat/opencode-support}"   # flip to master after merge
RAW="https://raw.githubusercontent.com/${REPO}/${REF}"

CFG_DIR="${XDG_CONFIG_HOME:-$HOME/.config}/opencode"
CMD_DIR="$CFG_DIR/commands"

COMMANDS=(commit prime push-and-pr publish release research ultrathink)

# --- ui helpers ----------------------------------------------------------------

if [[ -t 1 ]]; then
  C_OK=$'\033[32m'; C_WARN=$'\033[33m'; C_ERR=$'\033[31m'; C_DIM=$'\033[2m'; C_R=$'\033[0m'
else
  C_OK=''; C_WARN=''; C_ERR=''; C_DIM=''; C_R=''
fi
ok()   { printf '%s✓%s %s\n' "$C_OK"   "$C_R" "$*"; }
info() { printf '%s·%s %s\n' "$C_DIM"  "$C_R" "$*"; }
warn() { printf '%s!%s %s\n' "$C_WARN" "$C_R" "$*" >&2; }
die()  { printf '%s✗%s %s\n' "$C_ERR"  "$C_R" "$*" >&2; exit 1; }

# --- prereq checks -------------------------------------------------------------

for bin in curl bash python3; do
  command -v "$bin" >/dev/null 2>&1 || die "missing prerequisite: $bin"
done

# --- shell rc detection --------------------------------------------------------

SHELL_RC=""
case "${SHELL:-}" in
  *zsh*)  SHELL_RC="$HOME/.zshrc"  ;;
  *bash*) SHELL_RC="$HOME/.bashrc" ;;
  *)      [[ -f "$HOME/.zshrc" ]] && SHELL_RC="$HOME/.zshrc"
          [[ -z "$SHELL_RC" && -f "$HOME/.bashrc" ]] && SHELL_RC="$HOME/.bashrc" ;;
esac
[[ -n "$SHELL_RC" ]] || warn "could not detect shell rc file; env vars won't persist"

# Append KEY=VAL export to SHELL_RC if not already present.
rc_export() {
  local key="$1" val="$2"
  [[ -n "$SHELL_RC" ]] || return 0
  touch "$SHELL_RC"
  if ! grep -q "^export[[:space:]]\+${key}=" "$SHELL_RC"; then
    printf '\nexport %s=%q\n' "$key" "$val" >> "$SHELL_RC"
    info "appended export $key to $SHELL_RC"
  fi
}

# Append PATH segment to SHELL_RC if not already present.
rc_path_prepend() {
  local segment="$1"
  [[ -n "$SHELL_RC" ]] || return 0
  touch "$SHELL_RC"
  if ! grep -Fq "$segment" "$SHELL_RC"; then
    printf '\nexport PATH="%s:$PATH"\n' "$segment" >> "$SHELL_RC"
    info "added $segment to PATH in $SHELL_RC"
  fi
}

# --- 1. install opencode CLI ---------------------------------------------------

if command -v opencode >/dev/null 2>&1; then
  ok "opencode already installed ($(opencode --version 2>/dev/null || echo unknown))"
else
  info "installing opencode CLI via opencode.ai/install"
  curl -fsSL https://opencode.ai/install | bash || die "opencode install failed"
  # opencode.ai/install puts the binary under ~/.opencode/bin
  export PATH="$HOME/.opencode/bin:$PATH"
  rc_path_prepend "$HOME/.opencode/bin"
  command -v opencode >/dev/null 2>&1 || die "opencode still not on PATH after install"
  ok "opencode installed"
fi

# --- 2. create config dirs -----------------------------------------------------

mkdir -p "$CMD_DIR"
ok "config dir ready: $CFG_DIR"

# --- 3. fetch or copy template files -------------------------------------------

# Detect whether we're running from a local checkout by walking up from BASH_SOURCE.
# If found, copy locally; else fetch from RAW.
LOCAL_REPO=""
if [[ -n "${BASH_SOURCE[0]:-}" && -f "${BASH_SOURCE[0]}" ]]; then
  candidate="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
  if [[ -f "$candidate/.opencode/opencode.json" ]]; then
    LOCAL_REPO="$candidate"
  fi
fi

fetch_to() {
  # fetch_to <remote-path> <local-dest>
  local src="$1" dst="$2"
  if [[ -n "$LOCAL_REPO" && -f "$LOCAL_REPO/$src" ]]; then
    cp "$LOCAL_REPO/$src" "$dst"
  else
    curl -fsSL "$RAW/$src" -o "$dst" || die "failed to fetch $src"
  fi
}

info "source: ${LOCAL_REPO:-$RAW}"

fetch_to ".opencode/opencode.json" "$CFG_DIR/opencode.json"
fetch_to "AGENTS.md"                "$CFG_DIR/AGENTS.md"
for cmd in "${COMMANDS[@]}"; do
  fetch_to ".claude/commands/${cmd}.md" "$CMD_DIR/${cmd}.md"
done
ok "template files installed (config + AGENTS.md + ${#COMMANDS[@]} commands)"

# --- 4. prompt for Fireworks API key -------------------------------------------

if [[ -z "${FIREWORKS_API_KEY:-}" ]]; then
  # If already in rc file, source it.
  if [[ -n "$SHELL_RC" ]] && grep -q '^export[[:space:]]\+FIREWORKS_API_KEY=' "$SHELL_RC" 2>/dev/null; then
    # shellcheck disable=SC1090
    FIREWORKS_API_KEY="$(grep '^export[[:space:]]\+FIREWORKS_API_KEY=' "$SHELL_RC" | tail -1 | sed -E 's/^export[[:space:]]+FIREWORKS_API_KEY=//; s/^"//; s/"$//; s/^'\''//; s/'\''$//')"
    export FIREWORKS_API_KEY
    info "FIREWORKS_API_KEY loaded from $SHELL_RC"
  fi
fi

if [[ -z "${FIREWORKS_API_KEY:-}" ]]; then
  printf '\nGet a Fireworks API key at: https://fireworks.ai/account/api-keys\n'
  # /dev/tty so `curl | bash` pipelines can still prompt interactively.
  if [[ -r /dev/tty ]]; then
    printf 'Enter your FIREWORKS_API_KEY (hidden): '
    IFS= read -rs FIREWORKS_API_KEY < /dev/tty
    printf '\n'
  else
    die "no tty available for key prompt; set FIREWORKS_API_KEY in the environment and re-run"
  fi
  [[ -n "$FIREWORKS_API_KEY" ]] || die "empty FIREWORKS_API_KEY"
  export FIREWORKS_API_KEY
  rc_export FIREWORKS_API_KEY "$FIREWORKS_API_KEY"
fi

# --- 5. resolve GLM-5.1 slug from live catalog ---------------------------------

info "resolving GLM-5.1 slug from Fireworks catalog"
SLUG="$(
  curl -fsS https://api.fireworks.ai/inference/v1/models \
    -H "Authorization: Bearer $FIREWORKS_API_KEY" \
  | python3 -c '
import json, sys
data = json.load(sys.stdin).get("data", [])
# Prefer a 5.1-specific slug, fall back to any glm-5*
ids = [m["id"] for m in data if "id" in m]
glm5 = [i for i in ids if "glm-5" in i.lower()]
prio = sorted(glm5, key=lambda i: (
    0 if "5p1" in i or "5-1" in i or "5.1" in i else
    1 if "5p0" in i or "5-0" in i else
    2,
    i,
))
print(prio[0] if prio else "")
' || true
)"
[[ -n "$SLUG" ]] || die "no GLM-5 model visible to this API key (check Fireworks dashboard/tier)"
ok "resolved model: $SLUG"

# --- 6. rewrite placeholder in config ------------------------------------------

# Use python to avoid sed escape gotchas with /'s in the slug.
python3 - "$CFG_DIR/opencode.json" "$SLUG" <<'PY'
import sys, pathlib
p = pathlib.Path(sys.argv[1])
slug = sys.argv[2]
p.write_text(p.read_text().replace("{{GLM_MODEL_ID}}", slug))
PY

# Validate the resulting config.
python3 -m json.tool "$CFG_DIR/opencode.json" >/dev/null \
  || die "rewritten $CFG_DIR/opencode.json is not valid JSON"
if grep -q '{{GLM_MODEL_ID}}' "$CFG_DIR/opencode.json"; then
  die "placeholder not fully replaced in $CFG_DIR/opencode.json"
fi
ok "config rewritten with live slug"

# --- 7. smoke test chat-completions --------------------------------------------

info "smoke-testing Fireworks chat completions"
SMOKE_PAYLOAD="$(python3 -c '
import json, sys
print(json.dumps({
    "model": sys.argv[1],
    "max_tokens": 8,
    "messages": [{"role": "user", "content": "ping"}],
}))
' "$SLUG")"

SMOKE_BODY="$(
  curl -fsS https://api.fireworks.ai/inference/v1/chat/completions \
    -H "Authorization: Bearer $FIREWORKS_API_KEY" \
    -H "Content-Type: application/json" \
    -d "$SMOKE_PAYLOAD" \
  || die "Fireworks chat/completions returned non-2xx"
)"

SMOKE_TEXT="$(printf '%s' "$SMOKE_BODY" | python3 -c '
import json, sys
try:
    d = json.load(sys.stdin)
    print((d.get("choices") or [{}])[0].get("message", {}).get("content", "") or "")
except Exception as e:
    print("")
')"
[[ -n "$SMOKE_TEXT" ]] || die "smoke test returned empty content; response: $SMOKE_BODY"
ok "smoke test passed ($(printf '%s' "$SMOKE_TEXT" | head -c 40))"

# --- done ----------------------------------------------------------------------

printf '\n%s✓ OpenCode setup complete.%s\n' "$C_OK" "$C_R"
printf '%s  Config:   %s%s\n' "$C_DIM" "$CFG_DIR/opencode.json"  "$C_R"
printf '%s  Commands: %s (%d files)%s\n' "$C_DIM" "$CMD_DIR" "${#COMMANDS[@]}" "$C_R"
printf '%s  Model:    %s%s\n' "$C_DIM" "$SLUG" "$C_R"
printf '\nNext:\n'
if [[ -n "$SHELL_RC" ]]; then
  printf '  source %s   # if FIREWORKS_API_KEY was freshly added\n' "$SHELL_RC"
fi
printf '  opencode\n\n'
