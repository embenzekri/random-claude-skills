# Refresh loop and pruning

Scar: marketintel's AGENTS.md grew to 26-34 KB against an 8 KB target after six cap raises
(`tools/backlog/contextFileCaps.mjs`: target 8192, a "freeze" cap of 25664, each raise justified
in a comment); its retrospective was 57% of every dispatch's mandatory reading until trimmed to
40 lines. A cap that can be raised is not a cap.

## Caps (design constants, not configurable per repo)

| File | Cap |
|---|---|
| root AGENTS.md | 8,192 bytes |
| CLAUDE.md | 5 lines, pointer only |
| each area AGENTS.md | 200 lines |
| injected retrospective / lessons file | 40 lines |
| docs/architecture/codebase-map.md | one row per area, no prose per row |

## Size check script

Save in the target repo as `scripts/check-context-caps.sh` (explicit, short, exits non-zero):

```sh
#!/bin/sh
# Fails if always-loaded context files exceed their caps.
ROOT="$(cd "$(dirname "$0")/.." && pwd)"
fail=0
b=$(wc -c < "$ROOT/AGENTS.md")
[ "$b" -le 8192 ] || { echo "FAIL root AGENTS.md $b bytes > 8192"; fail=1; }
l=$(wc -l < "$ROOT/CLAUDE.md"); [ "$l" -le 5 ] || { echo "FAIL CLAUDE.md $l lines > 5"; fail=1; }
find "$ROOT" -name AGENTS.md -not -path '*/node_modules/*' -not -path "$ROOT/AGENTS.md" |
while read -r f; do
  n=$(wc -l < "$f"); [ "$n" -le 200 ] || echo "FAIL $f $n lines > 200"
done | grep -q FAIL && { echo "area file over cap (re-run for names)"; fail=1; }
exit $fail
```

Owner command: `sh /ABS/REPO/scripts/check-context-caps.sh`. Wire it into CI and into the
integrator's pre-merge gates (a prose cap is ignored; marketintel's inline-fix rule only worked
once it became a gate).

## When to refresh

| Trigger | Action |
|---|---|
| Merged ticket changed an area's entry points, commands, contracts, invariants | update that area file in the same PR; integrator checks the diff includes it |
| New package/area, moved or deleted dir, new cross-area import | update area file, codebase-map.md, dependency-rules.md; re-run boundary gate |
| Any cap exceeded | prune (below); never raise |
| A premise in an area file proved false during a ticket | fix it now and mark the line `(corrected DATE)`; do not leave it for later |
| A line carries UNVERIFIED for over 30 days | verify it or delete it |
| Whole map older than about 90 days, or a big reorg | full SURVEY again, diff against current files |

Cheap refresh = REFRESH mode on touched areas only: one haiku sweep of that area (same brief as
the survey), sonnet edits the area file, lead checks the diff of "Invariants" and "Do not touch".

## Pruning rules (apply in this order)

1. Delete resolved gotchas (the code now prevents them or a test does).
2. Delete anything a command can print: file lists, dependency lists, symbol lists. Replace with
   the command (`ls`, the generated CODEMAP) rather than the output.
3. Replace multi-paragraph explanations with a one-line rule plus a link to `docs/`.
4. Move history ("we tried X in September, it failed because...") to
   `docs/architecture/archive/<area>-YYYY-MM.md`. Keep in the area file only the surviving
   rule and a link to the archive entry. The archive is read on demand, NEVER referenced as
   "read first" and never imported with `@` into an always-loaded file.
5. A rule that recurs becomes a gate (script, hook, lint rule, CI check); then delete the prose
   or reduce it to "enforced by <script>".
6. Still over the cap: the area is too big. Split the area (new area file) instead of compressing.

## Never

- Raise a cap, or add an "exception" list of oversized files.
- Paste incident narratives, commit hashes lists, retro text, or ticket numbers by the dozen into
  an always-loaded file.
- Hand-maintain facts a script can regenerate (symbol lists, route lists, dependency graphs).
