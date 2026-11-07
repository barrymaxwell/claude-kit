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
mkdir -p ~/.claude/skills && ln -sfn ~/claude-kit/skills/meeting ~/.claude/skills/meeting && ln -sfn ~/claude-kit/skills/recap ~/.claude/skills/recap && ln -sfn ~/claude-kit/skills/branches ~/.claude/skills/branches && ln -sfn ~/claude-kit/skills/where ~/.claude/skills/where
```

## Skills

- `skills/meeting/` is `/meeting`. After a client call, it files the transcript, writes the meeting note and updates the client's to-do, done and decisions files. Run `/meeting RealPlayer`, or `/meeting` from inside a client folder.
- `skills/branches/` is `/branches`. It lists open branches, worktrees and PRs across `~/Dev-Projects`, with status icons, and refreshes the pinned Branch Board page. Run `/branches Telatris` to filter.
- `skills/recap/` is `/recap`. At the end of a session, it lists what was done, plus the worktrees, servers and links.
- `skills/where/` is `/where`. It says which repo, worktree and branch the session is on, plus sync state, uncommitted files, the last commit and the PR.

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
