---
description: Sort and reorganize a plan file by headers.
---

$ARGUMENTS

Arguments: <file path>

## Algorithm

1. **Validate**: Check file exists. If no argument — ask for path (AskUserQuestion).

2. **Backup**: `cp <file> <file>.bak`

3. **Sort** (semantic, not mechanical):
   a. Parse file into sections (## headers). If orphan lines exist above the first header — create a header for them.
   b. **Semantic audit**: Go through EVERY non-empty line in EVERY section. For each line, check: does this line's topic match its current section header? If not — move it to the correct section. Common misplacements: tasks dumped under a catch-all section, items that match another section's topic by keyword, repo/docs cleanup mixed with infra tasks.
   c. Sort sections alphabetically by header.
   d. Insert moved lines before the first ### subsection in the target (not at the very end). Respect code block boundaries (``` ... ```) when detecting subsections.
   e. Collapse consecutive blank lines (max 1).
   f. Preserve every original line exactly as-is — no rewording, no reformatting. Keep frontmatter at the top.

4. **Write sorted version** to original path.

5. **Verify**: Write a temp script that compares `<file>.bak` and `<file>` — extract non-empty lines from both, sort, diff. Every line must be present. Run, show result, delete script. If mismatch — restore from backup, abort.

6. **Rewrite version**: Create `<file>.rewritten.<ext>` — rewrite the sorted plan for clarity (grammar, style, duplicates, section summaries). Keep all original items.

7. **Output**: Report paths of all 3 files and line counts.

Act immediately — no confirmation needed.
