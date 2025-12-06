---
description: Universal validation of LLM-generated code against specification, quality standards, and project constitution.
handoffs:
  - label: Fix Issues
    agent: speckit.implement
    prompt: Fix validation failures in the implementation
  - label: Update Spec
    agent: speckit.clarify
    prompt: Clarify spec issues found during validation
  - label: Create PR
    agent: push-and-pr
    prompt: Create pull request for validated changes
---

## User Input

```text
$ARGUMENTS
```

You **MUST** consider the user input before proceeding (if not empty).

## Goal

Perform comprehensive validation of LLM-generated code before PR creation. Validate code against:
1. Feature specification (spec.md, plan.md)
2. Linting, formatting, and type checking tools
3. Test suite execution
4. Project quality standards
5. Constitution alignment (GATE checklist for Bot/Service/Tracker)

## Operating Constraints

**STRICTLY READ-ONLY for artifact files**: Do **not** modify spec.md, plan.md, tasks.md. Code fixes require explicit user approval.

**Constitution Authority**: The project constitution (`.specify/memory/constitution.md`) is **non-negotiable**. Constitution conflicts are automatically CRITICAL.

## Execution Steps

### Phase 0: Setup & Stack Detection

1. **Initialize Context**:
   Run `.specify/scripts/bash/check-prerequisites.sh --json --require-tasks --include-tasks` from repo root.
   Parse JSON for FEATURE_DIR and AVAILABLE_DOCS. All paths must be absolute.

   For single quotes in args like "I'm Groot", use escape syntax: e.g 'I'\''m Groot' (or double-quote if possible: "I'm Groot").

2. **Abort Conditions**:
   - If FEATURE_DIR not found → ERROR: "Run /speckit.specify first"
   - If plan.md not found → ERROR: "Run /speckit.plan first"
   - If tasks.md not found → ERROR: "Run /speckit.tasks first"
   - If no code changes detected → WARN: "No implementation found. Run /speckit.implement first?"

3. **Detect Project Type**:
   Scan spec.md and plan.md for keywords to determine validation profile:

   | Type | Detection Keywords |
   |------|-------------------|
   | Bot | telegram, discord, slack, bot, бот |
   | Service/API | api, service, endpoint, микросервис, сервис |
   | Tracker | monitor, track, aggregate, трекер, агрегатор |
   | Library | library, package, sdk, модуль |
   | CLI | cli, command, terminal, консоль |

4. **Auto-detect Tech Stack**:
   Scan project files to determine stack and tools:

   | Stack | Detection Files | Format | Lint | Type Check | Test |
   |-------|----------------|--------|------|------------|------|
   | Python | pyproject.toml, *.py | ruff format | ruff check | mypy | pytest |
   | TypeScript | tsconfig.json, *.ts | prettier | eslint | tsc | vitest/jest |
   | JavaScript | package.json, *.js | prettier | eslint | - | vitest/jest |
   | Go | go.mod, *.go | gofmt | golangci-lint | (built-in) | go test |
   | Rust | Cargo.toml, *.rs | cargo fmt | cargo clippy | (built-in) | cargo test |

   Store detected stack as TECH_STACK variable.

5. **Build File Inventory**:
   - Extract all file paths from tasks.md (implementation targets)
   - Find changed files: `git diff --name-only $(git merge-base HEAD main)..HEAD`
   - Filter to feature scope from plan.md

### Phase A: Spec Compliance

6. **Load Specification Context**:
   - Read spec.md: Extract functional requirements, user stories, acceptance criteria
   - Read plan.md: Extract architecture, data model, file structure, tech stack
   - Read tasks.md: Extract completed tasks [X] with file paths
   - Read data-model.md (if exists): Entity definitions
   - Read contracts/ (if exists): API specifications

7. **Build Requirement Traceability Matrix**:
   For each functional requirement in spec.md:

   | Req ID | Requirement Summary | Expected Files | Implemented In | Status |
   |--------|---------------------|----------------|----------------|--------|
   | FR-001 | User can login | auth.py | auth.py:L45-89 | FULL |
   | FR-002 | Password validation | validators.py | validators.py:L12-34 | PARTIAL |
   | FR-003 | Session management | session.py | NOT FOUND | MISSING |

8. **Code-to-Spec Analysis**:
   For each implemented file:
   - Map functions/classes to requirements they fulfill
   - Identify orphan code (no requirement mapping)
   - Flag requirement drift (implementation differs from spec)
   - Check acceptance criteria alignment

9. **Data Model Compliance** (if data-model.md exists):
   - Verify all entities from data-model.md are implemented
   - Check field types match specification
   - Validate relationships are correctly modeled

10. **Contract Compliance** (if contracts/ exists):
    - Verify all API endpoints from contracts are implemented
    - Check request/response schemas match contracts

**Output**: Spec Compliance Report with coverage percentage and gap list.

### Phase B: Tool Execution

11. **Pre-execution Checks**:
    - Verify tool availability based on TECH_STACK
    - Read project config (pyproject.toml, package.json, go.mod, Cargo.toml)
    - Identify package manager (uv, pnpm, npm, go, cargo)

12. **Execute Stack-Specific Tools**:

**If TECH_STACK = Python:**
```bash
# Formatting check
uv run ruff format --check --diff .

# Linting
uv run ruff check --output-format=json .

# Type checking
uv run mypy --strict . 2>&1 | head -200

# Tests with coverage
uv run pytest -v --tb=short --maxfail=10 --cov=. --cov-report=term-missing
```

**If TECH_STACK = TypeScript:**
```bash
# Formatting check
pnpm exec prettier --check .

# Linting
pnpm exec eslint . --format json

# Type checking
pnpm exec tsc --noEmit

# Tests
pnpm test -- --reporter=verbose
```

**If TECH_STACK = JavaScript:**
```bash
# Formatting check
pnpm exec prettier --check .

# Linting
pnpm exec eslint . --format json

# Tests
pnpm test -- --reporter=verbose
```

**If TECH_STACK = Go:**
```bash
# Formatting check
gofmt -l .

# Linting
golangci-lint run --out-format json

# Tests with coverage
go test ./... -race -coverprofile=coverage.out -v
```

**If TECH_STACK = Rust:**
```bash
# Formatting check
cargo fmt --check

# Linting
cargo clippy -- -D warnings

# Tests
cargo test -- --nocapture
```

13. **Aggregate Tool Results**:
    Create unified tool results summary:

    | Tool | Status | Issues | Critical | High | Medium | Low |
    |------|--------|--------|----------|------|--------|-----|
    | Format | FAIL/PASS | N files | 0 | 0 | N | 0 |
    | Lint | WARN/PASS | N issues | C | H | M | L |
    | Types | FAIL/PASS | N errors | C | H | M | L |
    | Tests | FAIL/PASS | N failures | C | H | 0 | 0 |
    | Coverage | WARN/PASS | X% | 0 | if <70% | 0 | 0 |

14. **Severity Mapping**:

    | Category | CRITICAL | HIGH | MEDIUM | LOW |
    |----------|----------|------|--------|-----|
    | Security | S* rules, secrets | - | - | - |
    | Types | Incompatible types | Missing annotations | Any usage | - |
    | Lint | Undefined vars | Unused imports | Complexity | Style |
    | Tests | Failed critical | Failed other | Flaky | Skipped |
    | Coverage | <50% | <70% | <80% | <90% |

### Phase C: Quality Analysis

15. **Universal Quality Checks**:

**SOLID Principles**:
For each major class/module, evaluate:
- **SRP**: Does class have one reason to change?
- **OCP**: Open for extension, closed for modification?
- **LSP**: Can derived classes substitute base?
- **ISP**: Are interfaces minimal and focused?
- **DIP**: High-level modules depend on abstractions?

Output: SOLID Compliance Score (0-100) per module.

**Error Handling**:
- Exceptions are specific (not bare `except:`)
- Error context is preserved
- User-facing errors are clear
- No silent failures

**Security**:
- No secrets in code (API_KEY=, password=, token=)
- Input validation at boundaries
- Parameterized queries only
- No eval/exec on user input

**Observability**:
- Structured logging (JSON preferred)
- No PII/secrets in logs
- trace_id propagation (if applicable)
- Health check endpoint (for services)

16. **Stack-Specific Quality Checks**:

**Python:**
- All I/O operations are async
- No blocking calls in async context
- Timeouts on external calls
- Exponential backoff for retries
- Connection pool configured

**TypeScript:**
- Strict null checks enabled
- Minimal `any` usage
- Proper async/await patterns
- Type guards where needed

**Go:**
- Errors wrapped with context
- No goroutine leaks
- Context propagation
- Defer for cleanup

**Rust:**
- Minimal unsafe blocks
- Result/Option handling (no unwrap in production)
- Proper error types

### Phase D: Constitution Alignment

17. **Load Constitution**:
    Read `.specify/memory/constitution.md` and extract GATE checklist.

18. **Apply Type-Specific Checklist**:

**For All (always apply):**
- [ ] Environment config from file (not hardcoded)
- [ ] Separate dev/prod configurations
- [ ] Docker/docker-compose setup (if applicable)
- [ ] Error handling for connection failures
- [ ] Health check implementation (for services)

**Telegram Bots (additional):**
- [ ] i18n support structure (if multi-language)
- [ ] Throttling middleware
- [ ] Feature-based handler organization

**Services/API (additional):**
- [ ] REST API structure
- [ ] Historical data storage (if applicable)
- [ ] Rate limiting

**Trackers (additional):**
- [ ] Auto-delete for old data
- [ ] Configurable footer/watermark

19. **Quality Gates Check**:

    | Gate | Required | Actual | Status |
    |------|----------|--------|--------|
    | Linting | 0 errors | N | PASS/FAIL |
    | Type checking | 0 errors | N | PASS/FAIL |
    | Unit coverage | >= 70% | X% | PASS/FAIL |
    | Critical issues | 0 | N | PASS/FAIL |
    | Security | 0 high/critical | N | PASS/FAIL |

### Phase E: Report Generation

20. **Generate Validation Report**:

```markdown
# Validation Report: [FEATURE_NAME]

**Generated**: [TIMESTAMP]
**Branch**: [BRANCH_NAME]
**Stack**: [TECH_STACK]
**Project Type**: [Bot/Service/Tracker/Library/CLI]
**Overall Status**: PASS | WARN | FAIL

## Executive Summary

[1-3 sentence summary of validation outcome]

## Validation Coverage Matrix

| Phase | Component | Status | Score/Issues | Blocking |
|-------|-----------|--------|--------------|----------|
| A | Spec Compliance | ... | X% coverage | No/Yes |
| B | Format | ... | N files | No |
| B | Lint | ... | N issues | Yes if CRITICAL |
| B | Types | ... | N errors | Yes if CRITICAL |
| B | Tests | ... | N failures | Yes if any |
| B | Coverage | ... | X% | Yes if <70% |
| C | SOLID | ... | X/100 | No |
| C | Security | ... | N issues | Yes if any |
| D | Constitution | ... | N/M passed | Yes if MUST failed |

## Phase A: Spec Compliance

### Requirement Coverage: X% (N/M)

[Traceability matrix]

### Missing Implementations
- [List requirements with zero code coverage]

## Phase B: Tool Results

[Tool execution summary table]

### Critical Issues (Must Fix)
[Numbered list with file:line and description]

### High Issues (Should Fix)
[...]

## Phase C: Quality Findings

### SOLID Compliance: X/100

| Module | SRP | OCP | LSP | ISP | DIP | Score |
|--------|-----|-----|-----|-----|-----|-------|

### Pattern Violations
[List of anti-patterns found]

## Phase D: Constitution Alignment

[GATE checklist with pass/fail status]

## Quality Gate Summary

| Gate | Required | Actual | Status | Blocker? |
|------|----------|--------|--------|----------|

## Actionable Recommendations

### Critical (Block PR)
[Numbered list of must-fix items]

### High (Fix Before Merge)
[...]

### Medium (Track for Later)
[...]

## Next Actions

Based on validation results:
- If CRITICAL issues: Run `/speckit.implement` to fix
- If only WARN: Proceed with PR, document known issues
- If PASS: Run `/push-and-pr` to create pull request
```

21. **Interactive Remediation Offer**:
    Ask user:
    > "Validation found [N] issues. Would you like me to:
    > A) Auto-fix formatting issues
    > B) Suggest code fixes for critical issues
    > C) Proceed to PR creation anyway (with warnings)
    > D) Re-run validation after manual fixes"

## Operating Principles

### Error Handling

| Scenario | Action |
|----------|--------|
| spec.md missing | ABORT with "Run /speckit.specify first" |
| plan.md missing | ABORT with "Run /speckit.plan first" |
| tasks.md missing | ABORT with "Run /speckit.tasks first" |
| Stack not detected | WARN, ask user to specify |
| Tool not installed | SKIP tool, WARN in report |
| Tool crashes | Capture stderr, continue |
| Timeout (>5min) | Kill, report partial |
| Tests failing | Capture details, categorize |

### Severity Levels

- **CRITICAL**: Security issues, type errors causing crashes, missing core requirements, constitution MUST violations
- **HIGH**: Missing types, low coverage, SOLID major violations, constitution SHOULD violations
- **MEDIUM**: Complexity warnings, style issues, edge case gaps
- **LOW**: Naming conventions, whitespace, minor redundancy

### Context Efficiency

- **Minimal tokens**: Focus on actionable findings
- **Progressive disclosure**: Load artifacts incrementally
- **Limit output**: Max 50 findings in table; summarize overflow
- **Deterministic**: Rerunning should produce consistent results

### Analysis Guidelines

- **NEVER modify files** without explicit approval
- **NEVER hallucinate** missing sections
- **Prioritize constitution violations** (always CRITICAL)
- **Use examples** over exhaustive rules
- **Report zero issues gracefully** with success message

## Context

$ARGUMENTS
