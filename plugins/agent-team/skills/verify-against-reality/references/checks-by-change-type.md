# Checks by change type

For each type: what to run, what number to name first, and the known-bad control. Combine types
(a feature usually touches several). Commands for the owner use absolute paths, e.g.
`cd /abs/path && npm test`.

## UI / web page
- Build with zero errors and the expected page count (a page missing from the count did not build).
- Content check on built output: unique string present, removed string gone *everywhere it could recur*
  (`grep -rl "old" dist/` - shared copy/i18n keys reach many pages), added string count via
  `grep -o | wc -l`. Control: absent string -> 0.
- Every asset reference resolves to a file (loop over hrefs/srcs, `[ -f ]`).
- Measure, do not eyeball: viewport share %, pixel coordinates, at mobile (375) and desktop widths;
  RTL page tested itself. Front the tab; check console for errors. Control: a deliberately wrong
  threshold must flag.
- Real gestures for interaction; never dispatched events.

## API / endpoint / external integration
- Fixture is a captured real payload (store it in the repo). Control: mutate the parsing line, test
  must fail.
- Call the live endpoint; check the body field you depend on, not just the status. Control: bad
  input/route must produce the error you expect.
- Units and shape of every field you read (v1 vs v2 style traps).

## SQL / migration
- Execute every statement against the real database (read-only or rolled back); eyeball actual rows.
  Control: a deliberately broken variant errors as predicted.
- Row counts before/after, the unit named (rows vs entities).
- Migration applied in the *target* environment: query the migrations table / `\d` the object.
- ACLs re-checked after change: `has_table_privilege('role','schema.obj','SELECT')`.
- State what changes in prod and what depends on this object (views, jobs).

## Background job / scheduler / worker
- Run it once for real (or a dry-run against live data) and read the output rows/logs.
- Check the *effect* (rows written, correct count, correct status), not that the process exited 0.
- Compiled-in defaults reviewed as config; each env/input pinned explicitly.
- Retry semantics: `maxRetries: 1` can mean two executions/rows; count with that in mind.
- Idempotence: second run produces no duplicates.

## Config / secret
- Read the value back from the running system (env of the deployed revision), not from the file you edited.
- Never print secret values in the log; log name + length/hash/presence. Control: a deliberately
  missing key must produce the expected failure.
- Which environments get it (prod vs preview)? Verified in each.

## Deploy / release
- Deployed revision/digest == merged commit (e.g. the project's verify-deploy tool:
  `cd /Volumes/MyData/ProjectsPro/ai-business/wallapopo-main && node tools/deploy/verify-deploy.mjs <filter>`
  after `git fetch origin main`; `unknown` means the image records no commit - report as UNVERIFIED,
  never guess).
- Live content check with known-bad control; allow for lag on first response, redeploy and recheck.
- Preconditions of chained steps checked; previous step's exit AND output sanity (non-empty).
- Rollback path named.

## Data pipeline / generated assets
- Source and output counts reconciled with units (input rows -> output rows, with the explained drop).
- Spot-check N real rows end to end; compare against an independent source for magnitude.
- Both copies of duplicated artefacts byte-identical (`cmp`); index/registry updated, not only the artefact.
- Freshness: timestamps of the newest row are today's, not cached.
- Re-run is idempotent; failure mid-run leaves no empty/partial output that a later step would ship.

## Docs / non-code
- Every command and path in the doc was executed or exists (`ls`); absolute paths for owner commands.
- Claims with numbers carry a source and date; stale figures flagged.
