#!/usr/bin/env python3
"""Collect branch and worktree status for every git repo under a root folder.

Usage: collect.py [filter] [--root DIR] [--out FILE] [--no-fetch]
Prints a markdown summary for chat. With --out, also writes JSON for the board page.
Read-only: runs git fetch --prune and gh pr list, nothing else.
"""
import argparse, json, os, subprocess, sys
from datetime import datetime, timezone

ICON = {"current": "🟢", "merged": "🧹", "pr": "🔗", "pushed": "🟢", "changes": "🟡",
        "behind": "🟡", "local": "🔴", "empty": "⚪", "remote": "☁️"}


def run(args, cwd, timeout=30):
    try:
        r = subprocess.run(args, cwd=cwd, capture_output=True, text=True, timeout=timeout)
        return r.stdout.strip() if r.returncode == 0 else ""
    except Exception:
        return ""


def find_repos(root, depth=3):
    repos = []
    root = os.path.expanduser(root)
    for dirpath, dirnames, _ in os.walk(root):
        rel = os.path.relpath(dirpath, root)
        level = 0 if rel == "." else rel.count(os.sep) + 1
        if ".git" in dirnames and os.path.isdir(os.path.join(dirpath, ".git")):
            repos.append(dirpath)
            dirnames[:] = []
            continue
        dirnames[:] = [d for d in dirnames if not d.startswith(".") and d not in ("node_modules", "Archive")]
        if level >= depth:
            dirnames[:] = []
    return sorted(repos)


def default_branch(repo):
    ref = run(["git", "symbolic-ref", "--short", "refs/remotes/origin/HEAD"], repo)
    return ref or "origin/main"


def worktrees(repo):
    out = run(["git", "worktree", "list", "--porcelain"], repo)
    items, cur = [], {}
    for line in out.splitlines() + [""]:
        if not line:
            if cur:
                items.append(cur)
            cur = {}
        elif line.startswith("worktree "):
            cur["path"] = line[9:]
        elif line.startswith("branch "):
            cur["branch"] = line[7:].replace("refs/heads/", "", 1)
        elif line == "detached":
            cur["branch"] = None
    return items


def prs(repo):
    out = run(["gh", "pr", "list", "--state", "all", "--limit", "100",
               "--json", "number,headRefName,state,url,title,isDraft"], repo, timeout=20)
    try:
        data = json.loads(out) if out else []
    except json.JSONDecodeError:
        data = []
    by = {}
    for p in data:  # newest first; keep the first per branch
        by.setdefault(p["headRefName"], p)
    return by


def branch_info(repo, name, base, wt_path, pr_map, is_root):
    up = run(["git", "for-each-ref", "--format=%(upstream:short)|%(upstream:track)|%(committerdate:short)",
              f"refs/heads/{name}"], repo)
    upstream, track, date = (up.split("|") + ["", "", ""])[:3]
    counts = run(["git", "rev-list", "--left-right", "--count", f"{base}...{name}"], repo).split()
    behind, ahead = (int(counts[0]), int(counts[1])) if len(counts) == 2 else (0, 0)
    unpushed = 0
    if upstream and "[gone]" not in track:
        c = run(["git", "rev-list", "--count", f"{upstream}..{name}"], repo)
        unpushed = int(c) if c.isdigit() else 0
    changes = 0
    if wt_path:
        changes = len([l for l in run(["git", "status", "--porcelain"], wt_path).splitlines() if l])
    pr = pr_map.get(name)
    gone = "[gone]" in track
    base_name = base.split("/", 1)[-1]

    if name == base_name:
        if unpushed:
            status, note = "local", ""
        else:
            status = "behind" if behind else ("changes" if changes else "current")
            note = f"{behind} behind origin" if behind else ""
    elif pr and pr["state"] == "MERGED" or gone:
        status, note = "merged", "merged; safe to remove once changes are checked" if changes else "merged; safe to remove"
    elif not upstream and ahead == 0 and changes == 0:
        status, note = "empty", "no commits yet"
    elif not upstream or unpushed:
        status, note = "local", "only on this Mac"
    elif pr and pr["state"] == "OPEN":
        status, note = "pr", ("draft PR" if pr.get("isDraft") else "PR open")
    elif changes:
        status, note = "changes", ""
    else:
        status, note = "pushed", "pushed, no PR"

    return {
        "branch": name, "worktree": None if is_root else (os.path.basename(wt_path) if wt_path else None),
        "is_root": is_root, "status": status, "note": note, "ahead": ahead, "behind": behind,
        "changes": changes, "unpushed": unpushed, "pushed": bool(upstream) and not gone,
        "date": date, "pr": {k: pr[k] for k in ("number", "state", "url", "title")} if pr else None,
    }


def remote_rows(repo, base, pr_map, local, days=14):
    """Branches on GitHub with recent commits that have no local branch, e.g. a teammate's or a cloud session's."""
    cutoff = datetime.now(timezone.utc).timestamp() - days * 86400
    base_name = base.split("/", 1)[-1]
    out = run(["git", "for-each-ref", "--sort=-committerdate",
               "--format=%(refname:short)|%(committerdate:unix)|%(committerdate:short)|%(authorname)",
               "refs/remotes/origin"], repo)
    rows = []
    for line in out.splitlines():
        ref, ts, date, author = (line.split("|") + ["", "", "", ""])[:4]
        name = ref.split("/", 1)[-1] if "/" in ref else ""
        if not name or name in ("HEAD", base_name) or name in local or name.startswith("dependabot/"):
            continue
        if not ts.isdigit() or int(ts) < cutoff:
            continue
        counts = run(["git", "rev-list", "--left-right", "--count", f"{base}...{ref}"], repo).split()
        behind, ahead = (int(counts[0]), int(counts[1])) if len(counts) == 2 else (0, 0)
        pr = pr_map.get(name)
        rows.append({
            "branch": name, "worktree": None, "is_root": False, "status": "remote",
            "note": f"on GitHub only, last commit by {author}", "author": author,
            "ahead": ahead, "behind": behind, "changes": 0, "unpushed": 0, "pushed": True,
            "date": date, "pr": {k: pr[k] for k in ("number", "state", "url", "title")} if pr else None,
        })
    return rows


def collect(repo, fetch):
    if fetch:
        run(["git", "fetch", "-q", "--prune", "origin"], repo, timeout=40)
    base = default_branch(repo)
    pr_map = prs(repo)
    wts = worktrees(repo)
    seen, rows = set(), []
    for i, w in enumerate(wts):
        b = w.get("branch")
        if not b:
            continue
        seen.add(b)
        rows.append(branch_info(repo, b, base, w["path"], pr_map, i == 0))
    for b in run(["git", "for-each-ref", "--format=%(refname:short)", "refs/heads"], repo).splitlines():
        if b not in seen:
            rows.append(branch_info(repo, b, base, None, pr_map, False))
    rows += remote_rows(repo, base, pr_map, {r["branch"] for r in rows})
    remote = run(["git", "remote", "get-url", "origin"], repo)
    attention = any(r["status"] not in ("current", "pushed") for r in rows)
    return {"name": os.path.basename(repo), "group": os.path.basename(os.path.dirname(repo)),
            "path": repo, "remote": remote, "base": base, "rows": rows, "attention": attention}


def markdown(repos):
    lines = []
    quiet = [r["name"] for r in repos if not r["attention"]]
    for r in repos:
        if not r["attention"]:
            continue
        lines.append(f"**{r['name']}**")
        lines.append("| | Branch | Worktree | State |")
        lines.append("|---|---|---|---|")
        for x in r["rows"]:
            bits = [x["note"]] if x["note"] else []
            if x["changes"]:
                bits.append(f"{x['changes']} uncommitted")
            if x["unpushed"]:
                bits.append(f"{x['unpushed']} unpushed")
            if x["pr"] and x["pr"]["state"] == "OPEN":
                bits.append(f"[#{x['pr']['number']}]({x['pr']['url']})")
            wt = "root" if x["is_root"] else (x["worktree"] or ("GitHub" if x["status"] == "remote" else "none"))
            lines.append(f"| {ICON[x['status']]} | `{x['branch']}` | {wt} | {', '.join(bits) or 'clean'} |")
        lines.append("")
    if quiet:
        lines.append("🟢 Clean: " + ", ".join(quiet))
    return "\n".join(lines) if lines else "🟢 Everything is clean."


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("filter", nargs="?", default="")
    ap.add_argument("--root", default="~/Dev-Projects")
    ap.add_argument("--out")
    ap.add_argument("--no-fetch", action="store_true")
    a = ap.parse_args()
    paths = [p for p in find_repos(a.root) if a.filter.lower() in p.lower()]
    repos = [collect(p, not a.no_fetch) for p in paths]
    print(markdown(repos))
    if a.out:
        data = {"generated": datetime.now(timezone.utc).isoformat(timespec="seconds"),
                "root": a.root, "filter": a.filter, "repos": repos}
        with open(os.path.expanduser(a.out), "w") as f:
            json.dump(data, f, indent=1)


if __name__ == "__main__":
    main()
