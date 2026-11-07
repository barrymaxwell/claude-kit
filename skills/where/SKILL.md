---
name: where
description: Say where this session is working - repo, worktree, branch, sync state, uncommitted files, last commit and PR - in a few lines. Use when Barry types /where or asks which worktree, branch or folder this session is on.
---

# /where

Read-only. Run this from the session's working directory:

```bash
if ! top=$(git rev-parse --show-toplevel 2>/dev/null); then echo "not-git $PWD"; exit 0; fi
common=$(cd "$(git rev-parse --git-common-dir)" && pwd)
echo "repo $(basename "$(dirname "$common")")"
echo "folder $top"
[ "$(git rev-parse --absolute-git-dir)" != "$common" ] && echo "worktree $(basename "$top")" || echo "worktree root"
echo "branch $(git branch --show-current || echo detached)"
up=$(git rev-parse --abbrev-ref '@{upstream}' 2>/dev/null) && echo "upstream $up $(git rev-list --left-right --count "$up"...HEAD)" || echo "upstream none"
echo "base $(git rev-list --left-right --count origin/HEAD...HEAD 2>/dev/null)"
echo "changes $(git status --porcelain | wc -l | tr -d ' ')"
echo "last $(git log -1 --format='%h %s (%cr)')"
gh pr view --json number,state,url --jq '"pr #\(.number) \(.state) \(.url)"' 2>/dev/null || echo "pr none"
```

Reply in this shape, with `~` for the home folder. Leave out a line that has nothing to say.

```
**<repo>** · `<branch>`
Worktree: <name>, or "root checkout"
Folder: <path>
Sync: <ahead/behind its upstream, or "not pushed yet">. <N> behind main, if any.
Changes: <N> uncommitted files, or "clean"
Last commit: <hash> <subject> (<when>)
PR: #<n> <state> <link>
```

`upstream A B` means A behind and B ahead. `base A B` means A commits behind the default branch and B ahead of it.

If the folder isn't a git repo, say so in one line with the path.
