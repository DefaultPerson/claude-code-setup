---
description: Push current branch and create a pull request.
---

## Git Rules

- Trunk-based development with rebase (linear history)
- PR title = Conventional Commit format, ≤72 chars
- PR description: what / why / how to test / risks
- PR base always `main`, merge strategy: **Rebase and merge**
- `--force-with-lease` only on personal feature branches after rebase
- Use `gh` for all GitHub operations
- Large PRs (>400 LOC) — consider splitting

## Algorithm

1. **Guard**: `git status` — ensure working tree is clean (everything committed).
   - **If on `main`**: stop — "You're on main. No PR needed. Push directly with `git push` or create a feature branch first." **STOP.**
   - **If on feature branch**: continue.
2. **Sync**: `git fetch origin` → `git rebase origin/main` → `git push -u origin HEAD --force-with-lease`.
3. **PR**:
   - Check if PR exists: `gh pr view --json number` — if exists, just push updates.
   - Create: `gh pr create --base main --head <current-branch>`.
   - Title: Conventional Commit format.
   - Body: what / why / how to test / risks.
4. **Checks**: `gh pr checks --watch` — if failing, diagnose and fix, re-push.
5. **Review**: Review using repo's PR template/checklist if present.
6. **Merge**: All checks green → ask user (AskUserQuestion): "Merge and delete branch?"
   - **Yes**: `gh pr merge --rebase` → `git switch main && git pull origin main` → `git branch -D <branch> && git push origin --delete <branch>`.
   - **No**: output PR link and stop.
7. **Output**: PR link, check statuses, summary of what was done.

Act immediately — no confirmation needed (except merge step).
