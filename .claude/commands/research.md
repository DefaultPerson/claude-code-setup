---
description: Conduct competitor analysis or technical research with structured output to research/.
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
   - **Competitor Analysis**: "alternatives", "vs", "competitors", "pricing", "compare", product/company names, "аналоги", "конкуренты"
   - **Technical Research**: "API", "how to", "best practices", "parsing", "library", "framework", "implementation", "github", "как", "парсить", "получить данные", "готовые решения"
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

### Phase 1: Scope Clarification (if needed)

Only ask clarifying questions if topic is genuinely ambiguous. **Max 3 questions.**

Present questions one at a time with recommendation:

**Recommended:** Option X - {reasoning}

| Option | Description |
|--------|-------------|
| A | ... |
| B | ... |

Possible questions (only if truly unclear):
1. **Scope**: Which aspects are most important? (features, pricing, implementation, all)
2. **Depth**: Quick overview or deep dive?
3. **Targets**: Any specific products/libraries to include or exclude?

Skip clarification if topic is clear enough to proceed.

### Phase 2: Research Execution

**Core principle: Claude determines queries and depth dynamically based on topic.**

#### Research Approach

1. **Start with broad discovery**:
   - Generate search queries based on topic semantics
   - Use current context (no hardcoded years or templates)
   - Search for main topic, alternatives, comparisons, best practices

2. **Analyze and identify gaps**:
   - What information is missing?
   - What claims need verification?
   - What specific products/tools need deeper investigation?

3. **Targeted deep dives**:
   - Search for specific missing information
   - Use WebFetch for official documentation, pricing pages, feature lists
   - Use Context7 for library/framework documentation

4. **Iterate until coverage is sufficient**:
   - No artificial limits on number of searches
   - Stop when topic is well covered
   - Stop when new searches don't yield new information
   - Stop if user says "enough" or "хватит"

#### Tools

- **WebSearch**: Primary search tool for discovery
- **WebFetch**: Deep reading of specific pages (docs, pricing, features)
- **Context7**: Library/framework documentation lookup
- **GitHub Search**: Ready-made solutions, reference implementations, popular libraries

#### GitHub Search

For existing solutions use WebSearch with `site:github.com`:
- `{topic} stars:>100` — popular repos
- `{topic} awesome` — curated lists

Evaluate: stars, last commit, license. Extract: patterns, dependencies, project structure.

#### Atomic Writes

After each significant block of findings, write to the research document:
- Initial findings after broad discovery
- Updated findings after gap analysis
- Final findings after verification

### Phase 3: Synthesis & Documentation

Structure findings based on detected mode:

#### For Competitor Analysis

```markdown
## Executive Summary
{2-3 paragraphs: key findings, market landscape, recommendation}

## Market Overview
{Brief description of the market/category}

## Competitors

### {Competitor 1}
- **Overview**: {what it is, who it's for}
- **Key Features**: {bullet list}
- **Pricing**: {tiers, free tier, enterprise options}
- **Strengths**: {what they do well}
- **Weaknesses**: {gaps, issues, limitations}
- **User Sentiment**: {reviews summary if found}

### {Competitor 2}
...

## Feature Comparison

| Feature | {Comp 1} | {Comp 2} | {Comp 3} |
|---------|----------|----------|----------|
| ... | ... | ... | ... |

## Pricing Comparison

| Tier | {Comp 1} | {Comp 2} | {Comp 3} |
|------|----------|----------|----------|
| Free | ... | ... | ... |
| Pro | ... | ... | ... |

## Recommendations
- **Primary**: {what to choose and why}
- **Alternatives**: {when to consider others}
- **Open Questions**: {what needs further investigation}
```

#### For Technical Research

```markdown
## Executive Summary
{2-3 paragraphs: problem, solution approach, recommendation}

## Technology Overview
{What the technology/approach is about}

## Best Practices
- **{Practice 1}**: {description + rationale}
- **{Practice 2}**: {description + rationale}

## Implementation Patterns

### Pattern: {Name}
```{language}
{code example if applicable}
```
**When to use**: {context}
**Trade-offs**: {pros/cons}

## Alternatives Comparison

| Criterion | {Option 1} | {Option 2} | {Option 3} |
|-----------|------------|------------|------------|
| Performance | ... | ... | ... |
| Complexity | ... | ... | ... |
| Community | ... | ... | ... |

## Security Considerations
- {Security concern 1}
- {Security concern 2}

## Recommendations
- **Primary**: {recommended approach}
- **Alternatives**: {when to consider others}
- **Open Questions**: {what needs team decision}
```

### Phase 4: Finalize & Report

1. Update document status to "Final"
2. Compile **Sources** section with annotations:
   ```markdown
   ## Sources
   1. [{Title}]({URL}) - {brief annotation: why valuable}
   2. ...
   ```

3. Report to user:
   - Path to research document
   - Brief summary of key findings (3-5 bullet points)
   - Suggested next steps if applicable

## Rules

- **Absolute paths** only
- **Atomic writes** after each significant finding block
- **No hardcoded query templates** — generate dynamically
- **No artificial search limits** — research until topic is covered
- **Sources at end**, not inline
- Match **user's language** in output
- Single quotes escaping: `'I'\''m Groot'`

## Error Handling

- If no relevant results: note the gap, suggest query refinement
- If conflicting information: document both perspectives, recommend verification approach
- If search fails: retry once, then document limitation

## Examples

```
/research telegram aggregator alternatives
/research CoinGecko API alternatives
/research NATS vs Kafka for real-time events
/research telegram message parsing best practices
/research как получить данные с binance
/research python async web scraping
/research github telegram bot python
```
