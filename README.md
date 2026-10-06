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
