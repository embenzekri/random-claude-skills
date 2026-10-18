---
name: review-lane
description: Independent, read-only review of one ticket's branch or diff before merge, ending in a JSON verdict (merge-ready, merge-with-follow-up, blocked) and a short human summary. Use when the user or team-lead says "review this ticket", "review the branch", "is it ready to merge", "review lane", "independent review", "merge-ready?", or after an implementer reports done. Re-runs the acceptance commands and a mutation check itself, cross-references past defects, delegates lenses to pr-review-toolkit and claude-security, and never merges.
---

# review-lane: independent review before merge

You are the reviewer: a fresh context that never saw the implementation, read-only on the
code, with one output, a verdict file. Sources: wallapopo `tech-lead.md` (review role),
`FLEET_ORCHESTRATOR.md` (review node, verdict contract, auto-merge policy), marketintel
`RETROSPECTIVE.md`. Role and routing context: `team-lead` section 7 and its `references/routing.md`.

## Hard rules

1. **Never the author's session.** If you wrote or edited this branch, stop and hand back to
   the lead. Self-approval is the failure this lane exists to prevent.
2. **Read-only.** No edits, commits, pushes or merges in the ticket worktree. The verdict (plus any feedback file the lead explicitly asks for) is the only file you write. Scratch work
   (mutation runs, repros) happens in throwaway worktrees (step 5). The only file you write
   is the verdict, plus scratch under the scratchpad.
3. **You never merge.** The integrator merges; you return a verdict.
4. **Do not trust the author.** Their note, summary and VERIFY LOG are claims to re-check.
5. **FIND is separate from VERIFY.** A finding is `confirmed: true` only if you reproduced
   it (command + observed output). Otherwise `confirmed: false`, and it cannot block.
6. **Absolute paths in every command**, in the verdict too.
7. **Live checks use the ticket's named read-only query tool, never a frozen rollback DB**
   (wallapopo: a review agent queried the wrong DB and called correct work fabricated).

## Inputs (ask the lead for any that is missing, do not guess)

- `/ABS/WT` ticket worktree or branch, and the base (normally `origin/main`).
- The task packet (`task-packet` skill): `touches`, `risk`, `complexity`, Acceptance,
  Verify commands, Contracts touched.
- The implementer's note, changelog fragment and VERIFY LOG (paths: `/ABS/WT/.agent-team/ticket.json` -> `dod`).
- Your model: **sonnet** by default; **top tier** if the diff touches infra, SQL/migrations,
  auth/secrets/input handling or contracts (`team-lead` routing). If you were started on a
  lower tier than that requires, say so first line of the summary and ask for re-dispatch.

## Steps

### 1. Load and freeze the diff
```
git -C /ABS/REPO fetch origin
git -C /ABS/WT diff --name-status origin/main...HEAD > /ABS/SCRATCH/files.txt
git -C /ABS/WT diff --no-renames origin/main...HEAD > /ABS/SCRATCH/diff.patch
git -C /ABS/WT log --oneline origin/main..HEAD
```
Rename detection off (a clean merge once deleted a P0 ticket via rename detection). A clean
`git status` is not an empty branch: judge by `origin/main..HEAD`. If HEAD is not a
descendant of current `origin/main`, note "needs rebase" (not a defect). Grep changed files for
conflict markers (`<<<<<<<`).

### 2. Scope check
Every changed path must match the ticket's `touches` / Write set. Findings for: files outside
`touches`, drive-by reformatting or renames, unrequested lockfile changes, committed
`.agent-team/`, edits to a contract not listed under "Contracts touched" (that alone is
`blocked`: contract changes belong to the lead). Also check `touches` for undeclared real edits.

### 3. Re-run acceptance; treat the VERIFY LOG as claims
List the `VERIFIED:` lines. **Re-execute every Acceptance item and Verify command yourself**
in `/ABS/WT`, and record command + observed value in `reruns`. A log line you did not re-run
stays a claim. Log vs your run mismatch is a confirmed finding, at least `major`. Apply the
`verify-against-reality` proofs (known-bad control, units, SQL actually executed, typecheck
last). Missing log, `FAILED:` lines, or an UNVERIFIED line hiding a check that could have run:
finding. Genuine UNVERIFIED items go to `follow_ups` with who must verify.

### 4. Merged is not running
State what must ship before this does anything (image, migration, deploy, flag). A before/after
claim measuring un-deployed behaviour is a finding. Not a block by itself; the deploy step must be filed.

### 5. Mutation re-run on the risky line
Pick the line whose removal must break an acceptance item. Use throwaway worktrees:
```
git -C /ABS/REPO worktree add --detach /ABS/SCRATCH/mut-main origin/main
git -C /ABS/REPO worktree add --detach /ABS/SCRATCH/mut-branch <branch-head-sha>
```
(a) On `mut-main`, copy in only the ticket's test files: tests for the new behaviour must go
red on main. (b) On `mut-branch`, delete or flip the risky line in the **production file**
(never the fixture or a fake): the suite must go red. Green means decorative coverage:
confirmed `major`. A fresh worktree has no `node_modules`: symlink it from the main checkout
(`ln -s /ABS/REPO/node_modules /ABS/SCRATCH/mut-branch/node_modules`) or reuse it. Never mutate
inside the author's worktree; if truly impossible, back up + restore + prove
`git -C /ABS/WT status --porcelain` is empty and record it in the verdict. Characterisation
tickets (feature already shipped, tests pass on main by design): skip (a); the production-line
mutation in (b) is the proof. Prove the mutation applied (`git diff --stat`). macOS has no
`timeout`. Clean up with `git -C /ABS/REPO worktree remove --force <path>`.
Recipes and traps: `references/mutation-and-rerun.md`.

### 6. Cross-reference past defects
Grep the retrospective (`.backlog/RETROSPECTIVE.md` or the repo's equivalent), the test
registry / rejected-approaches log, and history (`git -C /ABS/WT log --oneline -S'<symbol>' origin/main -- <path>`)
for every changed function, constant and query. A defect with a recurring shape: grep the
other copies in the repo. Third occurrence of a shape is `major` at least. See `references/past-defects.md`.

### 7. Pick lenses by diff content, run them in parallel (cap about 4)
Delegate, do not re-implement. Lenses return **unverified candidates** only. Prompts and
checklists: `references/lenses.md`.

| Diff contains | Lens |
|---|---|
| anything (baseline) | `pr-review-toolkit:code-reviewer`, or `/code-review` (plugin `code-review`) |
| try/catch, fallbacks, defaults, swallowed errors | `pr-review-toolkit:silent-failure-hunter` |
| tests added or changed | `pr-review-toolkit:pr-test-analyzer` |
| new types, interfaces, schemas, enums | `pr-review-toolkit:type-design-analyzer` |
| comments or docs changed (non-trivial) | `pr-review-toolkit:comment-analyzer` |
| auth, input parsing, secrets, exposed surface | `claude-security:claude-security` skill (`claude-security:scan` for a wider sweep) |
| SQL, migrations, infra, IaC, contracts | you run on the top tier and use the checklist in `references/lenses.md` |

### 8. VERIFY every candidate, then grade
For each lens candidate and each suspicion, attempt a repro: failing test, command with output,
query result, or exact `file:line` with trace. Reproduced: `confirmed: true`. Plausible but not
reproduced: keep as `confirmed: false`, severity capped at `minor`, listed in `follow_ups`, never
a block. Drop what you disproved. For every `blocker`, say whether you established the right
fix or only found the bug (marketintel TASK-157). Scale and mapping: `references/severity-and-verdict.md`.

### 9. Write the verdict
Fill `templates/verdict.json`; save to `/ABS/WT/.agent-team/review/<ticket>.verdict.json` (or the
path the lead names; create the folder). Print a human summary (max 15 lines): verdict, blocking
findings with `file:line`, reruns that disagreed with the log, what you did NOT verify, model
used, who acts next. The last line of your reply is one JSON line
`{"verdict":"merge-ready|merge-with-follow-up|blocked","summary":"..."}`. Unparseable means a human looks.

## Merge rules (you inform, the integrator applies)

- **Auto-merge candidate** only if verdict is `merge-ready` AND the diff (checked from the diff,
  not the ticket's claim) touches no infra, SQL/migrations, auth/secrets or contracts AND the
  integrator's gates pass on the rebased branch. The lead's own policy (FLEET_ORCHESTRATOR) overrides this flag. Default off; set `auto_merge_eligible` false in doubt.
- Everything else goes to the integrator and the owner: `merge-with-follow-up`, `blocked`, any
  restricted domain, an unparseable verdict, any unconfirmed major finding.
- Reviewer never merges, edits or self-approves. Unparseable counts as blocked for policy.

## Inline-fix rule

Scar: marketintel closed 42 tickets and filed 26 new ones in one day because every nit became a
ticket. Trivial findings (typo, missing assertion line, stale comment, unused import, under about
10 lines, no design choice) carry `"fix": "inline"` and go back to the same ticket's implementer
on the same branch. Only `complexity: complex` findings (needs a decision, spans modules,
touches a contract, or a second agent already failed) become `"fix": "new-ticket"`, filed by the
lead in one batch (one commit, one push). Reviewers do not file tickets.

## Files

- `references/lenses.md`: lens routing, agent names, prompt stubs, SQL/infra checklist.
- `references/severity-and-verdict.md`: severity scale, JSON schema, verdict mapping.
- `references/mutation-and-rerun.md`: re-run and mutation recipes, pitfalls.
- `references/past-defects.md`: cross-reference recipe and recurring defect shapes.
- `templates/verdict.json`: fill-in verdict. `templates/review-brief.md`: brief the lead pastes when dispatching you.
