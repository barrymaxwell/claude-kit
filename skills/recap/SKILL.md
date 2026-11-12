---
name: recap
description: Summarize all work from the current Claude Code session in a few lines, including sessions it started, the worktrees and branches used, and the dev servers that ran. Use when Barry types /recap or asks to summarize the session, wrap up, or list what was done.
argument-hint: "[optional focus, e.g. 'onboarding only']"
---

# /recap

A short end-of-session summary. Barry reads it in seconds.

## 1. Gather

Collect facts first. Write nothing until every check has run.

- **This session.** Read the conversation itself. Note what changed, what shipped and what is still open.
- **Sessions it started.** Load the session tools with ToolSearch (`select:mcp__ccd_session_mgmt__list_sessions,mcp__ccd_session_mgmt__list_events,mcp__ccd_session_mgmt__get_session`). Call `list_sessions` with `{"linked": true}`. For each one, read `list_events` with a high limit. Its compaction summary, if any, holds most of the facts.
- **Worktrees.** Call `get_session("self")` and `get_session` for each linked session to get the worktree name and branch. Then, from the repo:
  - `git worktree list`
  - Run `git fetch -q origin` once.
  - For each branch, run `git status --short` in its worktree. Run `git log --oneline origin/main..<branch>` for unmerged commits. Run `git branch -r --contains <branch>` to see where it was pushed. A branch that `origin/main` contains is merged and pushed.
- **Servers.**
  - Call `mcp__Claude_Browser__preview_list` for servers this session started.
  - Read `.claude/launch.json` for names and ports.
  - Run `lsof -nP -iTCP -sTCP:LISTEN | grep -E 'node|vite|python|ruby'` for what is still listening.
  - Take ports that linked sessions used from their transcripts.
  - List the servers these sessions used. Add one line for other dev servers still listening, so Barry can stop them.
- **Links.** Collect PRs, artifacts, deploy URLs and docs that were created or updated. Copy URLs exactly as the transcripts give them.

If a check fails or can't run, say so in **Open**. Don't guess.

## 2. Write

Match `/where` and `/close`: a heading, then short tables. Use `~` for the home folder. Start each state with ✅ when it's done or fine and ⚠️ when it needs Barry. Leave out any section with nothing in it.

```
### <repo> · Recap

| Done | |
|---|---|
| **<session title, linked>** | <change, under 10 words> |
| | <change> |

| Worktree | Branch | State |
|---|---|---|
| **<worktree name>** | `<branch>` | ✅ merged and pushed, or ⚠️ 3 commits not pushed, or ⚠️ 2 uncommitted files |

| Server | Port | State |
|---|---|---|
| **<launch name>** | :<port> | ✅ running, or ✅ stopped |

| Links | |
|---|---|
| **<name>** | <url> |

**Open**
- ⚠️ <anything pending, unverified or broken>
```

Rules:

- 15 rows at most across the tables. Merge or drop rows to fit.
- One fact per row. No intro line and no closing line.
- List outcomes, not steps. Write "Added the RealPlayer screen", not "Read the notes, then added…".
- Link each linked session once, in the Done table: [title](#local_<id>). Use "This session" for work done here.
- Other dev servers still listening get one row: **Also running** · :5181, :5182 · ✅ left alone.
- Follow Barry's writing rules in `~/.claude/CLAUDE.md`, and the project's GLOSSARY.md if it has one.
- With an argument, cover only that focus. Still list every worktree and server.
