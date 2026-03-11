---
description: Sort and reorganize a plan file by headers.
---

$ARGUMENTS

Arguments: <file path>

## Algorithm

1. **Validate**: Check file exists. If no argument — ask for path (AskUserQuestion).

2. **Backup**: `cp <file> <file>.bak`

3. **Parse & Sort**:
   - Identify headers (`#`, `##`, `###`) and their content blocks (bullets, lists, paragraphs, nested items).
   - Preserve frontmatter (YAML between `---`) at the top.
   - Sort top-level sections alphabetically by header text.
   - Sort sub-items within each section alphabetically.
   - Keep nested content (indented bullets) attached to their parent.
   - Preserve blank lines between sections.
   - **Preserve every original line exactly as-is** — no rewording, no reformatting.

4. **Write sorted version** to original path.

5. **Verify** (automated):
   - Write a temporary verification script (`/tmp/verify-sort.py` or similar).
   - The script reads `<file>.bak` (original) and `<file>` (sorted).
   - Extracts all non-empty, non-whitespace-only lines from both.
   - Sorts both lists and compares — every original line must appear in sorted output and vice versa.
   - Reports: total lines, matched lines, missing/extra lines if any.
   - Run the script, show output.
   - Delete the script after verification.
   - If mismatch — report which lines are missing/added, restore from backup, abort.

6. **Rewrite version**: Create `<file>.rewritten.<ext>`:
   - Take the sorted plan as base.
   - Rewrite for clarity: fix grammar, unify style, remove duplicates, add section summaries where helpful.
   - Keep all original items (no deletions).

7. **Output**: Report paths of all 3 files (backup, sorted, rewritten) and line counts.

Act immediately — no confirmation needed.
