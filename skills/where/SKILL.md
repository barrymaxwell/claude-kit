---
name: where
description: Say where this session is working - repo, worktree, branch, sync state, uncommitted files, dev server, last commit and PR - as a short table. Use when the user types /where or asks which worktree, branch, folder or dev server this session is on.
---

# /where

Read-only. Run this from the session's working directory:

```bash
if ! top=$(git rev-parse --show-toplevel 2>/dev/null); then echo "not-git $PWD"; exit 0; fi
common=$(cd "$(git rev-parse --git-common-dir)" && pwd)
root=$(dirname "$common")
echo "repo $(basename "$root")"
echo "folder $top"
[ "$top" != "$root" ] && echo "worktree $(basename "$top")" || echo "worktree root"
echo "branch $(git branch --show-current || echo detached)"
up=$(git rev-parse --abbrev-ref '@{upstream}' 2>/dev/null) && echo "upstream $up $(git rev-list --left-right --count "$up"...HEAD)" || echo "upstream none"
echo "base $(git rev-list --left-right --count origin/HEAD...HEAD 2>/dev/null)"
echo "changes $(git status --porcelain | wc -l | tr -d ' ')"
echo "last $(git log -1 --format='%h|%s|%cr')"
gh pr view --json number,state,url --jq '"pr #\(.number) \(.state) \(.url)"' 2>/dev/null || echo "pr none"
# Dev server: what this folder's launch.json starts, then anything listening from this folder now.
for f in "$top/.claude/launch.json" "$root/.claude/launch.json"; do
  [ -f "$f" ] && { jq -r '.configurations[]? | "config \(.name)|\(.runtimeExecutable // "") \((.runtimeArgs // []) | join(" "))|\(.port // "")"' "$f" 2>/dev/null; break; }
done
for pid in $(lsof -nP -iTCP -sTCP:LISTEN -t 2>/dev/null | sort -u); do
  cwd=$(lsof -a -p "$pid" -d cwd -Fn 2>/dev/null | sed -n 's/^n//p')
  case "$cwd" in "$top"|"$top"/*) ;; *) continue ;; esac
  [ "$top" = "$root" ] && case "$cwd" in "$root"/.claude/worktrees/*) continue ;; esac
  port=$(lsof -nP -a -p "$pid" -iTCP -sTCP:LISTEN -Fn 2>/dev/null | sed -n 's/^n.*://p' | head -1)
  echo "running :$port $(ps -o command= -p "$pid" | cut -c1-60)"
done
```

Reply with a heading and a two-column table, with `~` for the home folder. Leave out a row that has nothing to say. Start each value with ✅ when it's fine and ⚠️ when it needs attention.

```
### <repo> · `<branch>`

| | |
|---|---|
| **Worktree** | <name>, or "root checkout" |
| **Folder** | `<path>` |
| **Sync** | ✅ up to date, or ⚠️ <N> ahead / <N> behind <upstream>, or ⚠️ not pushed yet. Add "· <N> behind main" if any. |
| **Changes** | ✅ clean, or ⚠️ <N> uncommitted files |
| **Dev server** | ✅ <config name> running on :<port>, matched by port, or "not running · <config name> on :<port>" from launch.json, or "none set up" |
| **Last commit** | `<hash>` <subject> · <when> |
| **PR** | [#<n>](<url>) <state> |
```

`upstream A B` means A behind and B ahead. `base A B` means A commits behind the default branch and B ahead of it. A `running` line is a server started from this folder. A `config` line is the dev server this folder's `.claude/launch.json` starts.

If the folder isn't a git repo, say so in one line with the path.
