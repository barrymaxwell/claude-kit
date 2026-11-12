---
name: close
description: Close out the current Claude Code session. Checks this session and the sessions it started for uncommitted, unpushed or unmerged work, then removes their worktrees and branches if nothing is left, and stops their dev servers. Use when Barry types /close or asks to clean up, close branches or worktrees, or check whether anything still needs committing.
---

# /close

Ends a session's git footprint. Touch only the worktrees and branches this session and its linked sessions used.

## 1. Find what this session used

- Load the session tools with ToolSearch (`select:mcp__ccd_session_mgmt__list_sessions,mcp__ccd_session_mgmt__get_session`).
- Call `get_session("self")`, and `list_sessions` with `{"linked": true}`. Collect each session's worktree path and branch.
- Run `git fetch -q origin`, then `git worktree list` from the repo root.
- A worktree or branch that no session names belongs to someone else. Leave it.

## 2. Check for unsaved work

For each worktree and branch:

- `git -C <worktree> status --short`: uncommitted files.
- `git log --oneline origin/main..<branch>`: commits not on main.
- `git branch -r --contains <branch>`: where it was pushed.

Also check the main checkout with `git status -sb`, and `~/claude-kit` if this session edited it.

## 3. Decide

- **Anything unsaved:** stop. List each item in one line, with its worktree and branch. Ask whether to commit, push or drop it. Remove nothing.
- **All clean and merged:** remove without asking.
  - If this session is inside a worktree it is removing, leave it first with ExitWorktree.
  - `git worktree remove <path>`. Never pass `--force`.
  - `git branch -d <branch>`. Never `-D`.
  - `git push origin --delete <branch>` only if the remote branch exists and `origin/main` contains it.
  - `git worktree prune`.
- Stop the dev servers these sessions used, even if something is unsaved. See step 4.
- Leave sessions open.

## 4. Stop dev servers

- Call `mcp__Claude_Browser__preview_list`. Stop each server it shows with `preview_stop`.
- Take the ports linked sessions used from their transcripts. Run `list_events` for each one.
- Run `lsof -nP -iTCP -sTCP:LISTEN` to find each port's process. Run `lsof -a -p <pid> -d cwd` to find its folder.
- Stop a process with `kill <pid>` when its folder is a worktree being removed, or when one of these sessions started it. Never `kill -9`.
- Leave a server whose folder belongs to another open session, even on a port this session used. Name it in the reply.
- Run `lsof` again to confirm each port is free.

## 5. Reply

Three lines at most:

```
Nothing to commit. Removed <n> worktrees and <n> branches: <names>.
Stopped <launch name> on <port>.
```

If something blocked removal, say what and where. If a branch was already gone, say so.
