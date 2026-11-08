---
name: branches
description: Refresh this account's Branch Board with every open branch and worktree across your local repos, and name what needs you in a few lines. Use when the user types /branches or asks what branches, worktrees or PRs are open, what's unpushed, or what can be cleaned up.
argument-hint: "[optional repo or folder filter, e.g. 'Telatris']"
---

# /branches

Read-only. Never delete, push, commit or remove anything unless the user asks in this conversation.

Repos are found under `~/Dev-Projects`, three folders deep. Set `BRANCHES_ROOT` to use another folder. Folders named `Archive` are skipped.

## 1. Collect

Run the collector. It fetches each repo, reads worktrees and branches, and asks `gh` for PRs. Pass the filter if the user gave one.

```bash
python3 -I ~/.claude/skills/branches/collect.py "<filter>" --out "<scratchpad>/branch-board/data.json"
```

`<scratchpad>` is this session's scratchpad directory. Create `branch-board/` first. The script prints a summary for you to read. Don't paste it into chat. The board is the view.

## 2. Board page

Each account has its own board, titled "Branch Board". Find it by title. Never store or hard-code its link.

```bash
cp ~/.claude/skills/branches/board.html "<scratchpad>/branch-board/index.html"
```

1. List this account's artifacts with the Artifact tool: `action: "list"`, `scope: "mine"`, `limit: 200`. Take the most recent one titled exactly "Branch Board".
2. **Found:** read it with `action: "read"` and its `url`. Then read its data with the same call and `path: "data.json"`. A publish over an unread copy is refused. Then publish with `url` set to it, `file_path` set to `<scratchpad>/branch-board/index.html`, and `files` set to `{"data.json": "<scratchpad>/branch-board/data.json"}`.
3. **Not found:** publish without `url`, with the same `file_path` and `files`, plus `icon: "branch"` and `pin: true`. This is the account's first board.

## 3. Reply

At most three lines that name what needs the user, then the board link on its own line. Skip a line when nothing fits it.

- 🔴 Work that exists only on this Mac. Name the repo and branch.
- 🧹 Merged branches that can be removed. Say if any have uncommitted changes.
- 🟡 Root checkouts far behind origin.

## Cleanup, only when asked

Remove the worktree first, then the branch. Check a worktree's changes before removing it. Squash-merged branches need `git branch -D`.
