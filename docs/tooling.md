## 1) MCP: When and How

**Context7 (docs):** APIs/versions/patterns. `resolve-library-id → get-library-docs` (version/topic). Pin freshness, quotes ≤25 words.
**Sequential-Thinking (analysis):** multi-layer tasks/architecture/debug. Decomposition → hypotheses → facts → conclusions. Modes: `--think`(4K)/`--think-hard`(10K)/`--ultrathink`(32K). Log conclusions; combine with Context7.
**Chrome DevTools MCP:** Chrome DevTools API. Auto-selections of projects/frames, STDIO, consider quotas. Don't export assets — text/structure only.

## 2) Tool Selection and Policies

**Tools:** Search — Grep(exact)/Agent(broad); Understanding — Sequential(>0.7)/Read(simple); Docs — Context7; Tests — Chrome DevTools MCP.
**Delegation:** Score>0.6 → Task-tools (flags by scope); Wave>0.7 → Sequential for coordination.
**By default:** Docs — Context7 (current versions). Libraries — latest stable, pin version.

## 3) Commands/Flags

**Docs/research:** Context7 (`resolve → get-docs`, with topic/version).
**Analysis:** Sequential (`--think`/`--ultrathink`), hypotheses/conclusions.
**Tests:** Chrome DevTools MCP (critical paths,).

## 4) Orchestration

**Coordination:** decomposition; dependencies: Context7 → Chrome DevTools MCP; unified response/PR.
**Cache:** Context7(versions/patterns), Sequential(conclusions), Shared(links).
**Resilience:** backoff, circuit-breaker, graceful degradation; alternative: Context7.

## 5) Web Search as 10×

Queries by signatures/errors/versions (`Class.method E123 v3.3 site:docs.vendor.com`).
Priority: docs/RFC/release notes → issues/SO.
Dates: 12–18 month horizon; pin version and date.
Conflicts: 5-min repro/test. Always source+date; quotes ≤25 words; time-check.

## 6) Related Tools

`gh` (PR/review/releases);
