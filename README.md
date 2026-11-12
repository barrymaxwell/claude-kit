# claude-kit

The context files Claude reads on every machine and every new project.

- `CLAUDE.md` applies to every project. It covers response style, pushback and base voice.
- `project/` is copied into each new project: brief, glossary and decisions log.

## New machine

```bash
git clone https://github.com/barrymaxwell/claude-kit.git ~/claude-kit
```

```bash
ln -sf ~/claude-kit/CLAUDE.md ~/.claude/CLAUDE.md
```

```bash
mkdir -p ~/.claude/skills && ln -sfn ~/claude-kit/skills/meeting ~/.claude/skills/meeting && ln -sfn ~/claude-kit/skills/recap ~/.claude/skills/recap && ln -sfn ~/claude-kit/skills/close ~/.claude/skills/close && ln -sfn ~/claude-kit/skills/branches ~/.claude/skills/branches && ln -sfn ~/claude-kit/skills/where ~/.claude/skills/where && ln -sfn ~/claude-kit/skills/no-ai-slop ~/.claude/skills/no-ai-slop && ln -sfn ~/claude-kit/skills/archive ~/.claude/skills/archive
```

## Skills

The [Slash Commands page](https://claude.ai/artifact/MwUdunrUjNK3WnAZ6ii2zf) lists them all. Its source is `skills.html`. When a skill changes, update the page and republish it to that URL.

- `skills/meeting/` is `/meeting`. After a client call, it files the transcript, writes the meeting note and updates the client's to-do, done and decisions files. Run `/meeting RealPlayer`, or `/meeting` from inside a client folder.
- `skills/branches/` is `/branches`. It refreshes this account's pinned Branch Board with every open branch, worktree and PR under `~/Dev-Projects`. The first run in an account creates and pins the board. Set `BRANCHES_ROOT` to scan another folder.
- `skills/recap/` is `/recap`. At the end of a session, it lists what was done, plus the worktrees, servers and links.
- `skills/close/` is `/close`. It checks for unsaved work, then removes the session's worktrees and branches and stops its dev servers.
- `skills/archive/` is `/archive`. If no session has unsaved work, it archives this session and its sub-sessions. If one does, it asks whether to commit.
- `skills/where/` is `/where`. It says which repo, worktree and branch the session is on, plus sync state, uncommitted files, the last commit and the PR.
- `skills/no-ai-slop/` edits drafts to sound less like AI. By Peter Yang, MIT license.

## New project

From the project folder:

```bash
cp -n ~/claude-kit/project/* .
```

Then ask Claude to fill in the brief.

## Updating

Edit `~/claude-kit/CLAUDE.md` directly. It's the same file as the global one.
Commit and push. On other machines, `git pull`.

Every few weeks, ask Claude in each active project: "Prune the context
files. Archive what's stale, merge duplicates, keep them short."

## Session start

`hooks/session-start.sh` runs when a session starts. It's wired in through `~/.claude/settings.json`. Each new session opens with "claude-kit loaded" and the kit's skills. In a project folder with no CLAUDE.md, Claude offers to set up the kit.
