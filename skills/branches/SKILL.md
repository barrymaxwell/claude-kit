---
name: branches
description: Refresh the Branch Board with every open branch and worktree across Barry's repos, and name what needs him in a few lines. Use when Barry types /branches or asks what branches, worktrees or PRs are open, what's unpushed, or what can be cleaned up.
argument-hint: "[optional repo or folder filter, e.g. 'Telatris']"
---

# /branches

Read-only. Never delete, push, commit or remove anything unless Barry asks in this conversation.

## 1. Collect

Run the collector. It fetches each repo, reads worktrees and branches, and asks `gh` for PRs. Pass the filter if Barry gave one.

```bash
python3 -I ~/claude-kit/skills/branches/collect.py "<filter>" --out "<scratchpad>/branch-board/data.json"
```

`<scratchpad>` is this session's scratchpad directory. Create `branch-board/` first. The script prints a summary for you to read. Don't paste it into chat. The board is the view.

## 2. Board page

Copy the page next to the data, then republish the pinned artifact.

```bash
cp ~/claude-kit/skills/branches/board.html "<scratchpad>/branch-board/index.html"
```

1. Read the artifact first with the Artifact tool: `action: "read"`, `url: https://claude.ai/artifact/7vfFLMqxqXwPaW5gRtDPxA`. Then read its data too: the same call with `path: "data.json"`. The scheduled refresh replaces it, and a publish over an unread copy is refused.
2. Publish with `url` set to that link, `file_path` set to `<scratchpad>/branch-board/index.html`, and `files` set to `{"data.json": "<scratchpad>/branch-board/data.json"}`.

## 3. Reply

At most three lines that name what needs Barry, then the board link on its own line. Skip a line when nothing fits it.

- 🔴 Work that exists only on this Mac. Name the repo and branch.
- 🧹 Merged branches that can be removed. Say if any have uncommitted changes.
- 🟡 Root checkouts far behind origin.

## Cleanup, only when asked

Remove the worktree first, then the branch. Check a worktree's changes before removing it. Squash-merged branches need `git branch -D`.
