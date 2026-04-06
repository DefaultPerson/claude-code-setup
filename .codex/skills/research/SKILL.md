---
name: research
description: >
  Conduct competitor analysis or technical research with structured output to research/.
  Triggers: "research", "/research", "исследуй", "ресерч"
allowed-tools: [Bash, Read, Glob, Grep, Edit, Write]
---

## User Input

```text
$ARGUMENTS
```

You **MUST** consider the user input before proceeding.

## Outline

### Phase 0: Setup

1. **Parse topic** from `$ARGUMENTS`
   - If empty, ask user what to research

2. **Auto-detect research mode** based on topic keywords:
   - **Competitor Analysis**: "alternatives", "vs", "competitors", "pricing", "compare", product/company names
   - **Technical Research**: "API", "how to", "best practices", "parsing", "library", "framework", "implementation", "github"
   - If unclear, proceed with general research approach

3. **Generate output path**:
   - Slugify topic: lowercase, replace spaces with `-`, remove special chars
   - Path: `{REPO_ROOT}/research/{topic-slug}.md`
   - Create directory if not exists: `mkdir -p research`

4. **Initialize research document** with metadata (atomic write):
   ```markdown
   # Research: {Topic}

   **Date**: {YYYY-MM-DD}
   **Mode**: {Detected Mode}
   **Status**: In Progress
   ```

5. **Generate subtopics** (query decomposition):
   - Decompose main topic into 3-5 focused subtopics
   - Adapt subtopics based on detected mode:

   **For Competitor Analysis**:
   - What is {topic}? (market category, core value prop)
   - Who are the main players? (direct competitors)
   - How do they compare? (features, pricing, positioning)
   - What are the problems? (complaints, limitations)
   - What do users recommend? (community preferences)

   **For Technical Research**:
   - What is {topic}? (definition, core concepts)
   - How does it work? (mechanics, implementation)
   - What are the alternatives? (other approaches)
   - What are the problems? (limitations, gotchas)
   - What are best practices? (recommendations, patterns)

   Show the research plan to user before starting deep research.

### Phase 1: Scope Clarification (if needed)

Only ask clarifying questions if topic is genuinely ambiguous. **Max 3 questions.**

Skip clarification if topic is clear enough to proceed.

### Phase 2: Deep Research Execution

**Core principle: Multi-pass search with parallel exploration and source triangulation.**

#### Step 1: Parallel Research (MANDATORY for complex topics)

Launch 2-3 parallel agents, each handling one focused subtopic.
Use whatever multi-agent mechanism is available (Agent tool, spawn_agent, etc.).

**Rules for parallel research**:
- Each agent gets ONE focused subtopic
- Agents should use web search and web fetch tools
- Wait for all agents to complete before moving to Step 2
- For simple topics: skip parallel agents, do sequential search

#### Step 2: Multi-Pass Search Strategy

After parallel research, fill gaps with targeted passes:

**Pass 1 — Broad Discovery** (if not done by agents):
- General queries about the topic
- Overview articles, official docs

**Pass 2 — Expert Sources**:
- `site:news.ycombinator.com {topic}` — developer opinions, real experiences
- `site:reddit.com {topic}` — community insights, discussions
- `site:github.com {topic} stars:>100` — proven solutions, popular repos

**Pass 3 — Gap Analysis & Targeted Search**:
After each pass, evaluate internally:
- What's confirmed? What's still missing?
- What claims need verification from another source?

**Pass 4 — Counter-Arguments** (ALWAYS do this):
- `{topic} problems`, `{topic} criticism`, `why not use {topic}`

**Pass 5 — Source Triangulation**:
For key facts: verify from 2-3 independent sources.

#### Atomic Writes

After each significant block of findings, write to the research document.

#### Stopping Criteria

- All subtopics from Phase 0 covered
- Key claims verified from multiple sources
- Counter-arguments documented
- New searches don't yield new information
- User says "enough"

### Phase 3: Synthesis & Documentation

#### Confidence Ratings

- 🟢 **High**: 3+ sources, official docs, recent data
- 🟡 **Medium**: 1-2 sources, reasonably recent
- 🔴 **Low/Unverified**: Single source, outdated, or conflicting info

Structure findings based on detected mode (competitor analysis or technical research).

### Phase 4: Finalize & Report

1. Update document status to "Final"
2. Add **Disputed/Unverified Claims** section (if any)
3. Add **Research Metadata** (sources consulted, passes, depth)
4. Compile **Sources** section with annotations
5. Report to user: path, summary, disputed claims, next steps

## Rules

- **Absolute paths** only
- **Atomic writes** after each significant finding block
- **No artificial search limits** — research until topic is covered
- **Sources at end**, not inline
- Match **user's language** in output
