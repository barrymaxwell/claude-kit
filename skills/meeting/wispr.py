#!/usr/bin/env python3
"""Find and export Wispr Flow meetings for the /meeting skill.

  wispr.py list [--date YYYY-MM-DD] [--limit N]
  wispr.py export <meeting id> <client folder> --title "Short title" [--speakers "..."] [--force]

`list` prints meetings in Pacific time, newest first.
`export` writes Transcripts/<title> <YYYY-MM-DD HH:MM>(GMT-7:00).txt, the Zoom
naming pattern. It refuses if a file in Transcripts/ already names the same
Wispr meeting, and prints that file's path instead.
"""

import argparse
import json
import pathlib
import sqlite3
import sys
from datetime import datetime
from zoneinfo import ZoneInfo

BASE = pathlib.Path.home() / "Library/Application Support/Wispr Flow"
DB = BASE / "flow.sqlite"
PACIFIC = ZoneInfo("America/Los_Angeles")


def connect():
    # Read-only, so a running Wispr Flow is never disturbed.
    return sqlite3.connect(f"file:{DB}?mode=ro", uri=True)


def local_start(created_at):
    # createdAt is UTC, e.g. "2026-10-15 18:31:39.071 +00:00".
    utc = datetime.strptime(created_at[:19], "%Y-%m-%d %H:%M:%S").replace(tzinfo=ZoneInfo("UTC"))
    return utc.astimezone(PACIFIC)


def gmt_label(dt):
    # Zoom writes "(GMT-7:00)" in summer and "(GMT-8:00)" in winter.
    minutes = int(dt.utcoffset().total_seconds() // 60)
    sign = "-" if minutes < 0 else "+"
    h, m = divmod(abs(minutes), 60)
    return f"(GMT{sign}{h}:{m:02d})"


def speaker_names(speaker_map_json):
    """Map speaker id to a name. Unassigned ids are missing from the result."""
    if not speaker_map_json:
        return {}
    m = json.loads(speaker_map_json)
    people = m.get("people") or {}
    names = {}
    for sid, a in (m.get("assignments") or {}).items():
        a = a or {}
        pid = a.get("user") or a.get("consensus")
        person = people.get(pid) if pid else None
        if person and person.get("name"):
            names[int(sid)] = person["name"]
    return names


def cmd_list(args):
    rows = connect().execute(
        "SELECT id, title, createdAt, recordedMs, speakerMap FROM Meetings "
        "WHERE isDeleted=0 ORDER BY createdAt DESC LIMIT ?",
        (args.limit if not args.date else 200,),
    ).fetchall()
    for mid, title, created, recorded_ms, smap in rows:
        start = local_start(created)
        if args.date and start.strftime("%Y-%m-%d") != args.date:
            continue
        minutes = round((recorded_ms or 0) / 60000)
        named = ", ".join(sorted(set(speaker_names(smap).values()))) or "none"
        ready = "refined" if (BASE / "meetings" / mid / "refined.ndjson").exists() else "no refined.ndjson yet"
        print(f"{mid}  {start:%Y-%m-%d %H:%M} {gmt_label(start)}  {minutes} min  {title}")
        print(f"    named: {named} · {ready}")


def cmd_export(args):
    row = connect().execute(
        "SELECT title, createdAt, speakerMap FROM Meetings WHERE id=?", (args.id,)
    ).fetchone()
    if not row:
        sys.exit(f"No Wispr meeting with id {args.id}")
    _, created, smap = row

    transcripts = pathlib.Path(args.client) / "Transcripts"
    transcripts.mkdir(exist_ok=True)
    marker = f"Wispr Flow meeting {args.id}"
    for f in transcripts.glob("*.txt"):
        with open(f, encoding="utf-8", errors="ignore") as fh:
            if marker in fh.readline() and not args.force:
                print(f"exists: {f}")
                return

    src = BASE / "meetings" / args.id / "refined.ndjson"
    if not src.exists():
        sys.exit(f"{src} is missing. Wispr may still be refining the transcript.")

    names = speaker_names(smap)
    start = local_start(created)
    out = transcripts / f"{args.title} {start:%Y-%m-%d %H:%M}{gmt_label(start)}.txt"

    if args.speakers:
        speakers = args.speakers
    else:
        first = sorted({n.split()[0] for n in names.values()})
        speakers = f"Wispr named {' and '.join(first) or 'nobody'}. Other speakers are unassigned."

    lines = [f"Source: Wispr Flow meeting {args.id}, refined.ndjson.", speakers, ""]
    with open(src, encoding="utf-8") as fh:
        for raw in fh:
            if not raw.strip():
                continue
            d = json.loads(raw)
            sid = (d.get("speaker") or {}).get("id")
            who = names.get(sid, f"spk{sid}" if sid is not None else "?")
            lines.append(f"[{d.get('timestamp', '')}] {who}: {d.get('text', '').strip()}")
    out.write_text("\n".join(lines) + "\n", encoding="utf-8")
    print(f"wrote: {out}")


def main():
    p = argparse.ArgumentParser()
    sub = p.add_subparsers(dest="cmd", required=True)
    pl = sub.add_parser("list")
    pl.add_argument("--date", help="Pacific date, YYYY-MM-DD")
    pl.add_argument("--limit", type=int, default=10)
    pe = sub.add_parser("export")
    pe.add_argument("id")
    pe.add_argument("client", help="Client folder, e.g. .../Clients/RealPlayer")
    pe.add_argument("--title", required=True, help="Short call title for the file name")
    pe.add_argument("--speakers", help="Second header line: who Wispr named, and your guesses")
    pe.add_argument("--force", action="store_true", help="Write even if this meeting was exported")
    args = p.parse_args()
    {"list": cmd_list, "export": cmd_export}[args.cmd](args)


if __name__ == "__main__":
    main()
