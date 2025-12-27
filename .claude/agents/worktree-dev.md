# Worktree Development Agent

Isolated development agent that works in a separate git worktree.

## Input

Expects structured input:
```
branch: <branch-name>
port: <port-number> (optional, default: 3001)
task: <task-description>
base: <base-branch> (optional, default: main)
```

## Workflow

### 1. Setup Worktree

```bash
# Get project name from current directory
PROJECT_NAME=$(basename $(git rev-parse --show-toplevel))
WORKTREE_PATH="../${PROJECT_NAME}-${branch}"

# Create worktree with new branch
git worktree add -b ${branch} ${WORKTREE_PATH} ${base}
```

### 2. Execute Task

Work in the worktree directory using absolute paths:
- Read/edit files in `${WORKTREE_PATH}/`
- Run commands with `cd ${WORKTREE_PATH} && <command>`
- Install dependencies if needed

### 3. Run Application (if port specified)

```bash
cd ${WORKTREE_PATH} && npm run dev -- --port ${port}
# or
cd ${WORKTREE_PATH} && python -m uvicorn main:app --port ${port}
```

### 4. Return Result

Report back to orchestrator:
- Worktree path created
- Branch name
- Changes made (files modified)
- Server URL if running
- Any errors encountered

## Example Invocations

```
# Simple task
branch: feature-auth
task: Add login endpoint to API

# With port for testing
branch: experiment-v1
port: 3001
task: Refactor auth module using JWT

# Multiple parallel (called by orchestrator)
branch: variant-a
port: 3001
task: Implement caching with Redis

branch: variant-b
port: 3002
task: Implement caching with Memcached
```

## Cleanup

Agent does NOT cleanup worktree. Orchestrator or user should run:
```bash
git worktree remove ${WORKTREE_PATH}
```

## Constraints

- Always use absolute paths for worktree operations
- Never modify files in the main worktree
- Commit changes before reporting completion
- Use port range 3001-3010 for dev servers
