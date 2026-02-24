---
description: Publish repository to GitHub with full setup.
---

Interactive repo publication workflow. Uses `gh` CLI for everything.

## Algorithm

1. **Detect state**: `git remote -v` — check if `origin` points to GitHub.
   - **New repo** (no origin): full creation flow (steps 2-9).
   - **Existing repo** (origin exists): update flow — skip creation, go to step 3 to review/update description, topics, visibility, license, pages.
   - **No git repo**: `git init` first.

2. **Ask questions** (AskUserQuestion, single batch — new repos only):
   - **Owner**: personal account or organization? List available orgs with `gh api user/orgs --jq '.[].login'`.
   - **Visibility**: public or private?

3. **Ask questions** (both new and existing repos):
   - **License**: MIT (Recommended for public) / Apache-2.0 / GPL-3.0 / Keep current / None
   - **GitHub Pages**: Yes (MkDocs Material) / No / Keep current

4. **Auto-detect** (no user input needed):
   - **Repo name**: from current directory name
   - **Description**: generate concise 1-line summary from README.md or CLAUDE.md
   - **Topics**: detect from stack files:
     - `package.json` → nodejs, javascript/typescript
     - `pyproject.toml` / `requirements.txt` → python
     - `go.mod` → golang
     - `Cargo.toml` → rust
     - `Dockerfile` → docker
     - Also infer from README content (keywords, frameworks)
   - For existing repos: fetch current values with `gh repo view --json description,repositoryTopics` and show diff

5. **Create or update repo**:
   - New: `gh repo create <owner>/<name> --public|--private --description "<desc>" --source . --push`
   - Existing: `gh repo edit --description "<desc>"` (only if changed)

6. **Set topics**:
   ```bash
   gh repo edit --add-topic <tag1> --add-topic <tag2> ...
   ```

7. **License** (if selected/changed):
   - Fetch license text: `gh api licenses/<spdx-id> --jq .body > LICENSE`
   - Replace `[year]` and `[fullname]` placeholders
   - Commit and push

8. **GitHub Pages** (if selected/changed):
   - Create `mkdocs.yml` with Material theme, `docs/index.md` from README
   - Add GitHub Actions workflow `.github/workflows/docs.yml` for auto-deploy
   - Commit and push

9. **Polish** (automatic):
   - Check `.gitignore` exists — create basic one if missing
   - Suggest social preview image if repo is public
   - Suggest adding CI workflow if `.github/workflows/` is empty

10. **Output**:
    ```
    Repo: https://github.com/<owner>/<name>
    Visibility: public/private
    Topics: tag1, tag2, tag3
    License: MIT
    Pages: enabled at https://<owner>.github.io/<name>
    Changes: [list of what was created/updated]
    ```
