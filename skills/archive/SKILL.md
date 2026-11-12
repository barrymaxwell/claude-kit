---
name: archive
description: Archive this Claude Code session and the sessions it started, after checking that none of them has uncommitted or unpushed work. If something is unsaved, shows it and asks whether to commit. Use when Barry types /archive or asks to archive this session and its sub-sessions.
---

# /archive

Archives this session and its sub-sessions, but only when nothing would be lost. Archiving stops a session and removes its worktree, so uncommitted files there are gone.

## 1. Find the sessions

- Load the tools with ToolSearch (`select:mcp__ccd_session_mgmt__get_session,mcp__ccd_session_mgmt__list_sessions,mcp__ccd_session_mgmt__archive_session`).
- Call `get_session("self")`, and `list_sessions` with `{"linked": true}`. Keep the sessions this one started, and the ones they started. Leave out the session that started this one.
- For each, note its title, id, worktree folder (`cwd`), branch and whether it is running.

## 2. Check for unsaved work

Run `git fetch -q origin` once. Then, for each session's folder and branch:

- `git -C <folder> status --short`: uncommitted files.
- `git log --oneline origin/<branch>..<branch>`: commits not pushed. If there is no `origin/<branch>`, use `git branch -r --contains <branch>`. A branch that `origin/main` contains is pushed.

Also check `~/claude-kit` if a session edited it. Skip a folder that no longer exists.

Several sessions can share one folder. Check each folder once.

## 3. If something is unsaved

Archive nothing. Show what you found, then ask one question: commit it?

```
### <repo> · Not archived

| Session | Worktree | Unsaved |
|---|---|---|
| **<title, linked>** | `<worktree>` · `<branch>` | ⚠️ 2 uncommitted files: `src/a.tsx`, `src/b.css` |
| **<title, linked>** | `<worktree>` · `<branch>` | ⚠️ 1 commit not pushed |
| **<title, linked>** | `<worktree>` · `<branch>` | ✅ clean |
```

- List up to 5 file names per row, then "and 3 more".
- Offer three answers: commit and push, then archive. Leave it. Show the diff.
- On "commit": write the commit message from the diff, following Barry's writing rules. Commit in that worktree, push, and run step 2 again. Archive only when it comes back clean.
- Never discard or stash changes to make a session clean.

## 4. If everything is clean

Archive without asking again. Typing /archive is the approval.

1. Reply first, because archiving this session ends the conversation:

   ```
   ### <repo> · Archiving

   | Session | Worktree | State |
   |---|---|---|
   | **<title>** | `<worktree>` · `<branch>` | ✅ clean, pushed |
   ```

2. Archive each sub-session with `archive_session`, deepest first. Pass a reason like "Clean, all work pushed."
3. If one is still working, pinned or open on screen, the app refuses it. Note it, and don't archive this session. Say which session is left and why, then stop.
4. Archive this session last with `archive_session("self")`.

Leave dev servers, branches and other sessions alone. `/close` handles those.
