#!/bin/bash
# SessionStart hook. Confirms the kit loaded, and offers to set up the kit
# in a project folder that has no CLAUDE.md yet.
KIT="$HOME/claude-kit"
input=$(cat)
cwd=$(printf '%s' "$input" | jq -r '.cwd // empty' 2>/dev/null)
[ -n "$cwd" ] || cwd="$PWD"

# Skills that come from the kit: links in ~/.claude/skills that point into it.
skills=""
for s in "$HOME/.claude/skills"/*; do
  [ -L "$s" ] || continue
  case "$(readlink "$s")" in "$KIT"/*) skills="$skills /$(basename "$s")" ;; esac
done
skills=$(echo $skills | sed 's/ /, /g')

rules="no"
[ "$(readlink "$HOME/.claude/CLAUDE.md")" = "$KIT/CLAUDE.md" ] && rules="yes"

if [ "$rules" = "yes" ]; then
  msg="claude-kit loaded: rules, plus ${skills:-no skills}"
else
  msg="claude-kit rules are NOT linked: ~/.claude/CLAUDE.md doesn't point to $KIT/CLAUDE.md"
fi

ctx="Start your first reply with this line, as is: \"$msg.\""

# Offer the kit only in a real project folder: a git repo, or anything under ~/Dev-Projects.
in_project=no
git -C "$cwd" rev-parse --show-toplevel >/dev/null 2>&1 && in_project=yes
case "$cwd" in "$HOME/Dev-Projects"/*) in_project=yes ;; esac
case "$cwd" in */.claude/worktrees/*) in_project=no ;; esac
root=$(git -C "$cwd" rev-parse --show-toplevel 2>/dev/null || echo "$cwd")
if [ "$in_project" = yes ] && [ ! -f "$root/CLAUDE.md" ]; then
  ctx="$ctx Then add one line: this folder has no CLAUDE.md yet, and ask if Barry wants to set up the kit. If he says yes, follow \"Set up the kit\" in the global CLAUDE.md."
fi

jq -n --arg msg "$msg" --arg ctx "$ctx" \
  '{systemMessage: $msg, hookSpecificOutput: {hookEventName: "SessionStart", additionalContext: $ctx}}'
