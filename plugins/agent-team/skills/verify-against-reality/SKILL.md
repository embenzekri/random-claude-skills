---
name: verify-against-reality
description: The pre-close proof every agent runs before saying "done". Use when asked to verify, "is it done", "prove it works", "before closing", "check it's live", "did the deploy work", or to meet the "definition of done"; also before any success claim, commit, PR or ticket close. Supersedes and extends superpowers:verification-before-completion with owner-specific rules - known-bad controls, mutation checks, units, live read-back, merged-is-not-running, and the VERIFY LOG.
---

# Verify against reality

**This skill supersedes and extends `superpowers:verification-before-completion`.** That skill
says "run a command, read the output before you claim". This one adds what that one lacks, each
rule paid for by a real incident in the owner's projects (xmarlin, wallapopo/dispatch,
marketintel): a **known-bad control** for every check, a **mutation check**, **units**, a **read-back
of the live end state**, **merged is not running**, and a **verify log** that a Stop hook can gate on.
If both skills are loaded, follow this one.

## Rule zero: these are not evidence

Each of these has been reported as proof and was wrong:

- exit code 0 (an ingestor reported `success` on every run while writing to the wrong database;
  a scale test "passed" three times on one page because `--max-pages` defaulted to 1)
- a green suite (tests passed on a file that did not compile; 90/90 green with a WHERE clause deleted)
- a success toast, a "200 OK" (Cloudflare Pages returns 200 + index.html for a page never built)
- another agent's summary ("2 failures each" came from mutating the test double, not production)
- "looks fine" (a page was cleared as fine while the garment showed at 46% on mobile; the lead made this mistake too)

Evidence is **a command you ran after your final edit, plus the value it printed, compared with
a number you named in advance.** Name the expected value *before* you run the check.

## The seven proofs

Run every proof that applies to your change. `references/checks-by-change-type.md` says which.

### 1. Content check with a KNOWN-BAD CONTROL
Check the thing itself (the title, the row, the byte count, the string), not its status code. Then
run the **same check against something that must fail** and confirm it fails. A check that cannot
fail proves nothing.
- Deploy: fetch the page, match a string unique to it; the control is a route that does not
  exist and must *not* match. (Pages 404-as-200, xmarlin.)
- Count: `grep -o 'X' f | wc -l`, not `grep -c` (counts lines, not matches; a minified build read "2"
  when the truth was 633). Control: grep a string you know is absent, expect 0.
- Removal: `grep -rl "deleted string" dist/` must be empty *and* the same grep on the previous build
  must hit (otherwise the grep is the broken part).

### 2. Mutation check on the risky line
Break or revert the line you changed (delete the filter, flip the comparison, `git stash` the fix).
The suite **must go red**. Paste the failing output. Restore, confirm green again. If it stays
green, your coverage is decorative: write the assertion, do not report done.
- Mutate the **production file**, never the fixture or a fake (TASK-159: 7/7 green under both
  mutations; the "failures" were in a fake that had drifted from the real mapper).
- Re-run the mutation on `main` first: a failure that was already there is not coverage you added.
- A test that never imports the module under test cannot guard it. A test that matches source
  text is not a test of the code (TASK-150).
- Build fixtures from a **captured real payload**, never from memory or docs (TASK-151: v1 shape
  hand-written, v2 shape live, 20 production rows falsified).

### 3. Units and magnitude of every number
Write the unit next to every number you quote: calls, ads, rows, euros, bytes, px, %, ms are
not interchangeable. Sanity-check the order of magnitude against something independent (a
total, a prior run, a row count). If you count a proxy, say what it over/under-counts. Read the
cost column before claiming money was saved ("€0 saved, paid for and thrown away" - the model
was free; a stated benefit was off by ~90x). A measured number beats an impression, always.

### 4. Read back the live end state
The code is not the system. Query the database, call the live API, read the real log line, open
the real page. Reading code and concluding "it should work" is not verification.
- Run your function over a real sample of live values, not examples you chose; eyeball the rows.
- Assert the *effect* (the row exists with the right value), not the text of the call.
- A synthesized event proves nothing about a browser behaviour (`dispatchEvent("dragstart")`
  fires regardless of `draggable`): use a real gesture, with the tab **fronted**.
- Put at least one piece of real output (query result, API response, log line) in your note.

### 5. Merged is not running
Five tickets (TASK-136/148/175/172/177) merged correct code that did nothing because the Cloud
Run job still ran an older image. Ask of every change: "what must ship before this does anything?"
- Deployed revision / image digest / commit label **equals** the commit you merged (main HEAD for
  those paths). Read it from the running system, not from your deploy command's output.
- **Compiled-in defaults are configuration.** A job with no env/JSON input runs its constants as
  production config (image 0.4.2's defaults governed an enricher for weeks). Pin them explicitly.
- If you cannot deploy, say so in plain words: "this has no effect in production until X is
  redeployed", file the deploy ticket, and give a falsifiable prediction (which number moves, and
  what it means if it does not). That goes in the log as `UNVERIFIED`.
- Chained steps: never deploy after a failed upstream step (a failed export left `_site` empty and
  `wrangler deploy` shipped an empty Studio).

### 6. Execute every SQL statement you wrote; check prod and ACLs
Nothing else catches a query that was never run: the same illegal `ORDER BY` after `UNION ALL`
shipped three times (TASK-136, 150, 157) with a green suite, and would have failed every daily run.
Run each statement against the real database (read-only or in a rolled-back transaction). After
any DDL/view/function change, re-check privileges the consumer needs (`has_table_privilege(...)`)
and state exactly what changes in production when this lands.

### 7. Type-check / build as the LAST step
Run the package's `tsc --noEmit` (or build) in **every package you touched, after your final edit.**
A run that predates a file you later added is not green; the claim is about the code you ship
(archive §13). Also: no stray lockfile changes, no conflict markers (`grep -rn '<<<<<<<'`),
everything committed. Then re-run the full test command once more if anything changed.

## Tools lie: pre-flight before trusting a measurement
Short form (full list with scars in `references/tool-lies.md`): hidden/background tabs are
throttled (IntersectionObserver never fires, screenshots stale); shared browser tabs get hijacked
by other sessions (pass an explicit tab id); `getBoundingClientRect` ignores `clip-path` and
`overflow`; `offsetWidth` is empty on bare SVG; a DOM scan cannot see `::before` backgrounds;
`grep -c` counts lines; Pages returns 200 for missing routes; unknown framework props are dropped
silently; "exit 0" after a failed upstream step. When a measurement contradicts what you see,
suspect the tool first.

## The VERIFY LOG (contract)

Write one line per check to the file named in `.agent-team/ticket.json` -> `dod.verify_log`.
Create the parent folder if needed; append, never overwrite. Exactly these shapes, each line
starting at column 0:

```
VERIFIED: <claim> — <evidence: command + observed value> — control: <known-bad result>
FAILED: <claim> — <evidence>
UNVERIFIED: <claim> — <why it could not be checked>
```

- `VERIFIED:` needs all three parts. The evidence is the command you ran *and the value it
  printed*, with units. The control is what the known-bad variant did (or the mutation turned red).
  No control available? Say `control: none possible (<why>)` - and prefer `UNVERIFIED`.
- `FAILED:` means a check ran and the claim is false. **Do not close.** Fix, re-run, and append
  a new `VERIFIED:` line. Then delete or rewrite the stale `FAILED:` line (the gate refuses any
  `FAILED:` line, so the log must reflect the final state, not the history).
- `UNVERIFIED:` does not block the gate, but you must repeat every one in your final report
  to the owner, with what would verify it and who must do it. It is never a place to hide a
  skipped check you could have run.
- One claim per line. No line = not verified. A summary sentence is not a log line.

Example:

```
VERIFIED: ads page /ads/v3zip is built — curl -s localhost:8790/ads/v3zip | grep -o '<title>[^<]*' -> "<title>V3 Zip Bronze" — control: /ads/does-not-exist -> no match (0)
VERIFIED: slug appears once in list export — grep -o 'v3zip-bronze' _site/data/tests/ads.json | wc -l -> 1 (count of matches, not lines) — control: grep -o 'zzz-absent' ... | wc -l -> 0
VERIFIED: expiry filter is covered — deleted `and sr.source = 'wallapop'` in pgDealRepository.ts; npm test -> 2 failed / 90 — control: restored line, 90/90 pass
VERIFIED: watchlist SQL runs — node q.mjs 'select ...' -> 214 rows, priority populated — control: same query with `order by prio` -> error 42703
VERIFIED: typecheck clean after last edit — cd /abs/pkg && npx tsc --noEmit -> exit 0, 0 errors, run after final commit — control: none possible (tsc has no negative); mutation above shows suite reacts
UNVERIFIED: enricher change is live — needs image rebuild; deploy ticket DISP-412 filed, prediction: enriched_rows/day rises from ~300 to >900 — not deployable from this worktree
```

### Ticket sessions vs everything else
If `.agent-team/ticket.json` exists at the worktree root, you are in a ticket session. Its shape is
`{"id","role","worktree","dod":{"note","verify_log","changelog"},"waived":null}`. A Stop hook
will refuse to end your turn until every non-null `dod` path exists and is non-empty, and the
verify_log has at least one line starting `VERIFIED:` and **no** line starting `FAILED:`. A
non-empty `waived` reason disables the gate; never set it yourself - only the owner/lead does.
Outside ticket sessions this skill still applies in full; the log is simply not enforced. Write it
anyway for any non-trivial change.

## Order of work before saying done
1. Re-read the acceptance criteria line by line; list which proof covers each one.
2. Name expected values. 3. Run proofs 1-6 with controls. 4. Edit as needed, then proof 7 last.
5. Write the log, the note, the changelog. Commit before you answer.
6. Report: what is verified (with the log path), what is `UNVERIFIED` and why, in that order. An honest
   partial (move to review, not done) beats an inflated close.

Rationalisations to refuse: "the suite is green so the mutation check is redundant"; "it merged so it
is live"; "the other agent already checked"; "the screenshot looks right"; "I will typecheck at the
start since I only changed docs after".
