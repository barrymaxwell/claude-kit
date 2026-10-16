---
name: meeting
description: Run Barry's after-call routine for a client folder in his Obsidian vault. Finds the call transcript (Zoom, or exported from Wispr Flow), writes the meeting note, and merges To-Do.md, Done.md and Decisions.md. Use when Barry types /meeting or asks to process, file or write up today's call.
argument-hint: "[client] [extra hints, e.g. 'the 9:00 call']"
---

# /meeting

Barry's routine after a client call. It turns one transcript into a meeting note and updates the client's live lists, without creating duplicates.

## 0. Set up

**Client folder.** Clients live in `~/Library/Mobile Documents/iCloud~md~obsidian/Documents/Work/Clients/`.

- If `$ARGUMENTS` names a client, use that folder. Match case-insensitively. A full path works too.
- If not, and the working directory is inside a client folder, use that one.
- If not, use the client whose `To-Do.md` changed most recently. Name it in the reply.

**The client's `README.md` is the routine.** Read it first, along with `To-Do.md`, `Decisions.md`, `Done.md`, `Brief.md` and the two newest notes in `Meetings/`. If the README disagrees with this skill, follow the README.

**Today** is the Pacific date: `TZ=America/Los_Angeles date +%F`.

**Prototype repo.** Use the repo the README or Brief names. If none, try `~/Dev-Projects/<client name in lowercase>`. If there is no repo, skip the shipped check and say so.

**Re-runs are normal.** Before writing anything, check whether this call has already been processed: a note in `Meetings/` that links the transcript, or a `Decisions.md` section for that note. If so, update those files in place. Check the note against the transcript and add what it missed. Leave lines that are right as they are. Never add a second note, section, transcript or list item for the same call.

## 1. Find the transcript

1. **`Transcripts/` first.** Zoom files are named `<Call title> YYYY-MM-DD HH:MM(GMT-7:00).txt` in Pacific time. Take the newest file dated today. If Barry named a different call in the arguments, use that one.
2. **Then Wispr Flow**, if `Transcripts/` has nothing from today. List today's meetings:

   ```bash
   python3 ~/.claude/skills/meeting/wispr.py list --date YYYY-MM-DD
   ```

   Times are already Pacific. Pick the one for this client. Check the title, the named speakers and the first 40 lines of `meetings/<id>/refined.ndjson` against the Brief and recent notes. Other clients' calls show up here too. If two meetings could be this client's, ask Barry which.

3. **Export it.** Read the transcript first so you can guess the unnamed speakers. Wispr often names only Barry and one other person. The rest are `spk1`, `spk3` and so on. Use names said in the call and the attendees in recent notes. Two things to watch for:

   - One `spkN` can hold two people. Say so in the header line and say who leads which topics.
   - Wispr and Zoom mishear names. Check odd names against earlier transcripts and notes. On RealPlayer, Ariel often comes out as "Andrew" or "Rio".

   Then:

   ```bash
   python3 ~/.claude/skills/meeting/wispr.py export <id> "<client folder>" \
     --title "<Short call title>" \
     --speakers "Wispr named only Dana and Barry. From context: spk1 is Lee Park. spk3 is Sam."
   ```

   The title is short and lowercase after the first word, like `RP26 design review`. The script names the file in the Zoom pattern. Its first line names the Wispr meeting id, and it refuses to export the same meeting twice. If it prints `exists:`, use that file.

   If `refined.ndjson` is missing, Wispr is still refining. Say so and stop.

`../RealNetworks/Meeting-Transcripts.md` documents the Wispr layout if anything here breaks. Use it for the layout only. Its `Open-Questions.md` step belongs to the old folder structure.

## 2. Write the meeting note

`Meetings/YYYY-MM-DD Short title.md`. Short title is two or three words, like `Design review`. Match the existing notes exactly:

```markdown
# 22 Oct 2026 · Design review

Dana, Lee, Sam, Barry. 9:00, 38 minutes.
Transcript: `Transcripts/RP26 design review 2026-10-22 09:00(GMT-7:00).txt`

Next: Friday at 9:00, same group.

---

## Decided

- **Lead in bold.** One or two plain sentences. Reasoning goes here, not in Decisions.md.

## Shown

- Who showed what.

## Raised

- Name: the point, when who said it matters.

## Owed

| Who | What |
| --- | --- |
| Barry | ... |
```

- Attendees are first names, Barry last. Start time from the file name. Length from the last timestamp, rounded to the minute.
- `Next:` only when the call set one. Leave it out otherwise.
- `Shown` only when someone demoed something. Leave it out otherwise.
- Decided means settled in the call. A maybe or a lean goes in Raised.
- No checkboxes in the note. Owed is a table.

## 3. Merge into `To-Do.md`

Sections, from the README: **Priority list**, **Prototype**, **My calls**, **Waiting on**, **Parked**.

Each open item is one line:

```markdown
- [ ] **Key words** in bold, then the task. · [[2026-10-22 Design review|22 Oct]]
```

Work through every row of Owed and every open question from the call:

- **New:** add it to the right section, linked to this meeting. Barry's work due at the next call goes in Priority list, most urgent first, even when it was also handed to him as a call. Other design work goes in Prototype, in priority order. Calls they handed Barry go in My calls. What others owe Barry goes in Waiting on. Parked items have no checkbox or link.
- **Changed:** if an item already covers it, reword that item in place. Keep its original link. Don't add a second copy. Check for near-duplicates by meaning, not wording.
- **Moved:** an item can move between sections. Move it. Don't copy it.
- **Settled:** if the call answered a My calls item or decided a question, the item drops off To-Do. Its decision goes to Decisions.md.
- **Delivered:** a Waiting on item delivered in the call goes to Done under today, with no version.
- **Not Barry's and not owed to Barry:** a row like "Dana: recap to the group" stays in the note's Owed table only.

**Move finished items to `Done.md`.** Check what shipped:

```bash
git -C <prototype repo> log --since="<YYYY-MM-DD of the newest Done.md section> 00:00" --date=short --format="%ad %h %s"
```

Read `src/data/changes.ts` too. Each entry's `version` names the prototype version it shipped in. Write `v3-multi-select` as `Prototype v3`.

Count work committed after the call ended. Done is the state now. Ignore uncommitted work.

Keep the `00:00`. Without a time, git counts from the current time of day and misses that day's commits.

- An item is done when a commit or a `changes.ts` entry covers it. Partly done stays open, reworded to what's left. Drop wording that what shipped now contradicts.
- In `Done.md`, add `## D Mon YYYY` for the commit date, newest first. Reuse the heading if it exists. Lines are `- [x] Text. Prototype v3. · [[link]]`, keeping the item's original link.
- A commit with a `changes.ts` entry and no to-do still gets a line in Done. Link it to the meeting that raised it, if one did. Skip commits with neither a to-do nor a `changes.ts` entry. Those are fixes and housekeeping.
- Add lines under today's heading only. Older Done sections are history. Leave them as they are, even where they name things since renamed.
- When shipped work settles a My calls item, Barry made the call. Add it to `Decisions.md` too, in the section of the meeting the item links to. End the line with `Barry's call, prototype v3.`
- Remove the item from To-Do.md. It must never be open in both files.

**Rewrite the top of `To-Do.md`:**

- The reminder line: `> **Tomorrow, 9:00.** Show ...`. When and what the next call is, then what to show first. One or two sentences.
- `Updated D Mon YYYY.` with today's date.

## 4. Append to `Decisions.md`

Add a section for this call at the top, under the intro, newest first:

```markdown
## 22 Oct 2026 · [[2026-10-22 Design review|Design review]]

- One settled call per line. No reasoning.
```

Only what the call settled, plus Barry's calls from step 3. If the section exists, merge into it.

## Writing

Barry's voice rules from `~/.claude/CLAUDE.md` apply to every file: short common words, one idea per sentence, no semicolons or dashes joining clauses, none of the banned words. Write dates as `22 Oct 2026`. Match the wording style of the lines already in each file. Use the client's own names for things.

## 5. Reply

One to three lines. What was written, and what needs Barry's eye: speaker guesses, a meeting picked from two, an item you weren't sure was done. Example:

> Filed 22 Oct Design review from Wispr. To-Do has 6 new items and 2 reworded. 3 moved to Done. spk3 is a guess between Lee and Sam.
