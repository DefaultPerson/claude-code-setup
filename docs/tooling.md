## 1) MCP Servers

**Context7 (docs):** Library documentation lookup. `resolve-library-id → get-library-docs` (version/topic). Pin freshness, quotes ≤25 words.
**Chrome DevTools MCP:** Browser automation, testing, performance analysis. Auto-selections of pages/frames. Consider quotas. Text/structure focus.

## 2) Tool Selection

| Task | Tool |
|------|------|
| Code search (exact) | Grep |
| Code search (broad) | Task agent (Explore) |
| Documentation | Context7 or WebSearch+WebFetch |
| Browser testing | Chrome DevTools MCP |
| Deep analysis | Native extended thinking (/ultrathink) |

## 3) Built-in Tools (preferred)

- **WebSearch** — web search with current data
- **WebFetch** — fetch and parse web pages
- **Extended thinking** — native in Opus 4.5/Sonnet 4 (no MCP needed)

## 4) Orchestration

**Coordination:** decomposition; dependencies: docs → implementation → tests; unified response.
**Resilience:** backoff, graceful degradation; alternative sources.

## 5) Web Search Tips

Queries by signatures/errors/versions (`Class.method E123 v3.3 site:docs.vendor.com`).
Priority: docs/RFC/release notes → issues/SO.
Conflicts: 5-min repro/test. Always source+date; quotes ≤25 words.

## 6) CLI Tools

`gh` (PR/review/releases), `git`, `uv` (Python), `pnpm` (Node.js)
