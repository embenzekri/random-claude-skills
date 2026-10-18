# Re-run and mutation recipes

## Re-running acceptance
- Run each Verify command from the packet verbatim, from `/ABS/WT`, after `git -C /ABS/WT status --porcelain`
  is clean. Capture the printed value (with its unit), compare to the packet's expected value, then to
  the VERIFY LOG line. Three-way: packet expected / log claim / your result.
- Run the known-bad control too (a route that must 404, a grep that must be 0). A check without a
  failing control is not evidence (`verify-against-reality` proof 1).
- Count with `grep -o ... | wc -l`, not `grep -c`.
- Typecheck/build in every touched package, last: `cd /ABS/PKG && npx tsc --noEmit`.
- Dependencies missing in the worktree is an environment problem, not a defect: install per the repo's
  documented command, say so in `reruns`.
- Exit 0 is not a pass: read the artefact. A test run that collected 0 tests is red.

## Mutation check
Goal: prove the added tests detect the change, and that detection is the PR's, not pre-existing.

1. Identify the risky line(s) from the diff: the filter, comparison, default, guard, SQL clause.
2. **Against main** (the PR #127 trap):
   `git -C /ABS/REPO worktree add --detach /ABS/SCRATCH/mut-main origin/main`
   Copy only the ticket's new/changed test files in. New-behaviour tests must fail here. If they pass
   on main, they add no detection for this change: finding `major`.
3. **Against the branch**: `git -C /ABS/REPO worktree add --detach /ABS/SCRATCH/mut-branch <head_sha>`.
   Mutate the **production file** (delete the filter, flip `>` to `>=`, revert the default). Run the
   suite. Must go red; record the failing line count (`2 failed / 90`). Restore, confirm green.
4. Never mutate fixtures or fakes (TASK-159: 7/7 green under both mutations because the double had
   drifted from the real mapper). A test that never imports the module under test cannot guard it;
   a test matching source text is not a test of the code (TASK-150).
5. Fixtures from a captured real payload? Check provenance (TASK-151: hand-written v1 shape, live v2).
6. Delete the scratch worktrees afterwards. Do not leave branches behind.

## Cannot mutate
Config-only, docs-only, or pure SQL changes: say `mutation: not applicable (<why>)` and replace with
the equivalent: execute the SQL against the database and show rows; compare config values against the
running system. Do not leave the field blank.

## Pitfalls
- Hidden/background browser tabs are throttled; pass explicit tab ids; synthesized events prove nothing
  about real gestures (see `verify-against-reality/references/tool-lies.md`).
- Timing/flaky tests: run the failing test 3 times before calling it a finding; record the rate.
- A branch behind main can make reruns differ from CI: rebase in the scratch copy, not the ticket worktree.
