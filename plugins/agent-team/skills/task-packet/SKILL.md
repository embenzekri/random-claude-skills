---
name: task-packet
description: Write an agent-ready ticket (task packet) before any code is written, and set up the ticket marker when dispatching an implementer into a worktree. Use when the user says "write a ticket", "task packet", "split this into tasks", "dispatch an implementer", "brief an agent", "make this agent-ready", or when team-lead needs tickets. Produces frontmatter (id, title, model, complexity, touches, blocked_by, risk) plus Goal, Non-goals, Premise check, Read set, Write set, Contracts touched, numeric Acceptance, exact Verify commands, Rollout/rollback and a report contract, in 300-700 tokens.
---

# task-packet: one ticket, one agent, no questions needed

A ticket is read by a fresh agent that has read the root `AGENTS.md` and one area file and
nothing else. Put only what is specific to this task in it. Stable rules (testing conventions,
git workflow, Definition of Done) live in AGENTS.md, not in tickets. Delegation brief shape and
report contracts: the `fanout` skill. The lead's flow: the `team-lead` skill.

Template (copy it): `templates/task-packet.md`, relative to this skill's directory (the plugin copy is canonical; a copied skill dir carries its own `templates/`).

## Step 0: already done or superseded? (before anything else)

Before reading code or writing a packet, search history for the ticket and its key snippet:
`git -C /ABS/REPO log --all --oneline --grep=<ID>` and `git -C /ABS/REPO log --all -S'<key snippet>' --oneline`.
Also check the ticket is not already on main. If it shipped, the verdict is
`obsolete: done in <sha>`: write NO packet (optionally a re-scoped residual packet for what is
genuinely left) and hand back to the lead. Scar: TASK-3016 pilot, 18 Oct 2026 - a ticket in
`todo/` had shipped a month earlier (542009111); one `git log -S` found it.

## Size

Target 300-700 tokens; a genuinely complex ticket up to about 1,500. More than that means the
missing context belongs in a linked doc: write "Read `docs/x.md` section 3", do not restate it
(marketintel `.backlog/README.md`). Prose "why" only when it changes what to implement. Use a
table only when it compresses.

## Frontmatter

| Field | Rule |
|---|---|
| `id` | Allocated by a tool under a lock, never by hand. Two sessions picking the same id twice in one day made a duplicate that broke every backlog tool and turned all PRs red (marketintel). No tool yet: `T-` plus the max id on all branches and worktrees plus 1, checked just before writing |
| `title` | Imperative, short |
| `model` | Exact model. By cost of being wrong (`team-lead/references/routing.md`): top tier for architecture, contracts, migrations, auth/security, infra/SQL review, integration; sonnet for bounded implementation and tests; haiku for mechanical sweeps only |
| `complexity` | `trivial` (one file, one obvious change, verified by one command) / `standard` / `complex` (prod data, schema, spend, cross-area, or a prior agent failed). `complex` needs a top-tier pre-read of the premise before dispatch |
| `touches` | Everything this ticket WRITES or locks. Backlog tickets often use area notation (`area:name`); translate it to concrete paths/globs. Paths and globs, DB tables, env vars, infra resources (`infra:cloud-scheduler`), contracts. Honest and wide. Two tickets sharing a touch never run at the same time |
| `blocked_by` | Tickets that must be done first (order, not simultaneity). Doing them out of order causes an outage, not a conflict |
| `risk` | `high` for migration, auth, prod data, spend, public surface. High risk gets a top-tier reviewer |

## Sections

1. **Goal.** One observable outcome. "Page X returns the price in EUR" not "improve prices".
2. **Non-goals.** What must not change, plus budgets: max turns, a dollar or call ceiling for
   anything that spends money, "no prod secrets". An agent without a non-goal list widens scope.
3. **Premise check.** Facts the ticket depends on, each verified NOW with a pointer
   (`src/a.ts:88`) or real output (the command and its result). Premises go stale in hours:
   marketintel TASK-362/142/157 were false by pickup time, and TASK-151 parsed a Knative v1 shape
   from a v2 endpoint and wrote falsified status into 20 live rows. Re-run the checks at dispatch;
   if one flipped, fix the ticket, do not dispatch. Never write "I believe" or a remembered number.
4. **Read set.** Paths to read. Prefer "Read `T-102` conclusions" to copying them.
5. **Write set.** Exact paths the agent may write. "One file, one owner": name what it must NOT
   touch if a concurrent ticket is near (xmarlin brief template: Own / Do not touch).
6. **Contracts touched.** Each shared shape (API, schema, view, event, constant, env name) as
   `read-only` or `changes`. A ticket that needs a contract change is not ready: the lead
   fixes the contract first and re-issues the ticket. Cross-area contracts are never a worker's call.
7. **Acceptance.** Numbers and exit codes only, each checkable by a command. See the ban list below.
7a. **Toolchain bootstrap.** Install command (e.g. `npm ci`), runtime version, and whether
   dependencies already exist in the fresh worktree (usually no `node_modules`). Never make the
   agent discover these.
7b. **Live-data claims.** Every claim about prod/live data is marked UNVERIFIED, with how
   Acceptance avoids needing prod access (fixtures, read-only query the lead runs).
8. **Verify commands.** Exact, copy-pasteable, absolute paths, with the expected output. Include
   one known-bad control where it matters (a request that must fail, a fixture that must go red)
   and the mutation step: remove the change, the new test must fail. "Tests added" acceptance
   may be "test count rises by >= N" with the baseline count command. Assert rendered text
   exactly as the DOM shows it (`Marketplace:` with the colon), not the label constant. Give the
   restore command for the mutation (`git checkout -- <file>`).
9. **Rollout / rollback.** When it takes effect (merge, deploy of X, migration Y first) and the
   exact revert. "Merged is not running": if a deploy is needed, say "no effect in prod until X
   redeployed" and name the deploy ticket with a falsifiable prediction (5 marketintel tickets
   were inert).
10. **Deliverable + report contract.** Files the agent leaves behind (implementation note, verify
    log, changelog fragment) and a short report: measured numbers, not assertions; failures
    stated plainly with the miss size; no file contents pasted.

## Acceptance rules

- Each item is a number, a count, an exit status, or an exact string comparison, produced by a
  command in Verify commands.
- Forbidden words as the criterion: convert, feel, robust, clean, improve, better, intuitive,
  fast, polished, works, handles, properly, reasonable, user-friendly. "Make it convert" produced
  fabricated social proof and an invented delivery promise in xmarlin because those do convert.
  "Hero >= 26% of first screen on mobile, measured" cannot be satisfied that way.
- Say the unit. marketintel reported 261 "ads" that was a call count; the real number was about 3.
- Test the thing that ships: re-run type-check and tests as the LAST step after the final edit.
- Tests must fail without the change. A fake that returns what the author typed proves nothing:
  429 characterisation tests were green while 4 operator pages returned 500.
- SQL tickets: execute every statement; name the DB identity; query the live row count.

Examples:

| Bad | Good |
|---|---|
| Make search faster | `curl -w '%{time_total}' <url>` p95 <= 0.2 s over 50 runs, command in Verify |
| Handle empty input robustly | `parse('')` returns `[]` and `parse(null)` throws `TypeError`; both asserted in `/ABS/WT/tests/parse.test.ts` |
| Migrate the table | `select count(*) from t where new_col is null` returns 0 after backfill |

## Dispatching the ticket (the lead does this, in order)

1. Run the Premise check commands again. Any change: edit the ticket first.
2. Check `touches` against every active ticket and `blocked_by` against done. Overlap: wait.
3. Create the worktree: `git -C /ABS/REPO worktree add /ABS/WT/T-123 -b agent/T-123 origin/main`
4. Exclude the marker directory from git, once per repo (the file is shared by all worktrees):
   `echo ".agent-team/" >> "$(git -C /ABS/REPO rev-parse --git-common-dir)/info/exclude"`
   Check it first so you do not duplicate the line: `grep -qx '.agent-team/' <that file>`.
5. Write the marker, `/ABS/WT/T-123/.agent-team/ticket.json` (create the directory):

```json
{
  "id": "T-123",
  "role": "implementer",
  "worktree": "/ABS/WT/T-123",
  "dod": {
    "note": ".agent-team/T-123.note.md",
    "verify_log": ".agent-team/T-123.verify.log",
    "changelog": "changelog.d/T-123.md"
  },
  "waived": null
}
```

   - `role`: one of `implementer`, `tester`, `reviewer`, `integrator`, `release`.
   - `worktree`: absolute path of the worktree root. Hooks block Edit/Write outside it.
   - `dod` paths are relative to the worktree and must be copied from `ticket.json` into the packet's Deliverable section, never invented (a packet saying `docs/notes/X.md` while the hook required `.agent-team/X.note.md` cost the TASK-3016 tester a conflict). Use `null` for `changelog` if the repo has no
     fragments. The Stop hook refuses to end the turn until every non-null path exists and is
     non-empty, `verify_log` has at least one line starting `VERIFIED:`, and none starting `FAILED:`.
   - Reviewers and testers still get a marker: point `note` at their report file.
   - `"waived": "<reason>"` (non-empty string) disables the Stop gate. Only the lead sets it,
     and records the reason in the retro line. Never waive to get past a failing verify log.
6. Dispatch with the `Agent` tool: explicit `model` from the ticket, cwd = the worktree, body =
   the ticket text plus "read the ticket, do only it, stop and report blocked if a premise is
   false". The note and verify log are where the agent writes `VERIFIED: <check> <value>` lines
   from real command output.
7. When the agent returns: read the verify log first, re-run Verify commands yourself (or hand to
   `verify-against-reality`), then send to a fresh reviewer. Do not accept the summary as proof.
8. After merge, remove the worktree only once its branch files equal what landed on main
   (`git -C /ABS/REPO worktree remove /ABS/WT/T-123`), and delete the marker with it.

Staging reminder to put in every implementer brief: `git add <explicit paths>`, never `-A`,
`.`, `--all`, or `commit -a`; never `gh pr merge`; never `git push --force` (use
`--force-with-lease` only if the lead asked). Hooks block these, but say it anyway.
