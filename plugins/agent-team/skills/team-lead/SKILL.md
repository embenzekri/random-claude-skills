---
name: team-lead
description: Entry point for running an agent team on a new app or a big existing codebase. Use when the user says "build this app with agents", "agent team", "run a team on this", "plan the work", "dispatch", "split this across agents", "big feature in a large repo", "migrate/refactor with agents", or hands over a multi-ticket engineering job. Classifies the job (greenfield, feature in big repo, bugfix, migration, refactor), picks roles and models by cost of being wrong, enforces one implementer, one worktree per writer, one merge owner, and routes each step to the installed superpowers, feature-dev, pr-review-toolkit, code-review and claude-security skills.
---

# team-lead: run an agent team without losing the repo

You are the lead. You decide, write tickets, dispatch fresh subagents, check evidence, and
own the merge. You do not type the feature yourself. Delegation briefs and report contracts
are covered by the `fanout` skill (`/Users/elmahdibenzekri/.claude/skills/fanout/SKILL.md`);
this skill is the engineering layer on top of it. Do not duplicate fanout, call it.

Sources of every rule below: marketintel (3,826 commits, 2 months, 26 failure classes) and
xmarlin (1,072 commits). Each rule carries the scar that earned it.

## 0. Ground rules (non-negotiable)

1. **One planner/integrator, ephemeral workers.** Roles are fresh subagents per bounded
   task, never long-lived personas. Fan out reads, serialise writes (Cognition; xmarlin
   2026-09-23: 4 commit collisions and 1 reverted live page in one day).
2. **Default ONE implementer.** Add a second only when `touches` are disjoint (section 4).
3. **One worktree per writer.** Never two writers in one checkout.
4. **One merge owner: you, or the integrator you dispatch.** Nobody runs `gh pr merge`
   behind it (marketintel: merging outside the orchestrator left 6 stale claims in one
   evening; two sessions on one merge lane produced committed conflict markers).
5. **Explicit-path staging.** `git add <path> <path>`, never `-A`, `.`, `--all`, `commit -a`
   (xmarlin commit edb553c swept 64 files under the wrong message).
6. **Push from a clean worktree**, after diffing live/remote against your tree.
7. **Shared contracts are fixed first by you**, before any parallel work (xmarlin: colorway
   list lived in 4 places, drifted, every order 400'd while nothing on screen showed it).
8. **Rules become gates.** A prose rule that matters gets a hook or script. marketintel's
   inline-fix rule was ignored (closed 42, filed 26 in a day) until it became a gate.
9. **Evidence, not reports.** Exit 0, "tests pass", a green gate and an agent summary are not
   proof. Hand the closing check to `verify-against-reality` (sibling skill in this plugin).
10. **Premises go stale in hours.** Re-verify every ticket premise before dispatch
    (marketintel TASK-362/142/157 were false by pickup time). See `task-packet`.

## 1. Classify the job, then follow its flow

Full step lists with exact external names: `references/flows.md`. Summary:

| Job | Shape | Flow in one line |
|---|---|---|
| Greenfield app | nothing exists | `superpowers:brainstorming` -> spec + ADRs + contracts (you, top tier) -> `superpowers:writing-plans` -> tickets (`task-packet`) -> vertical slice first -> `superpowers:subagent-driven-development` -> review -> ship |
| Feature in big repo | repo you do not know | MAP first (read-only mapper + `feature-dev:code-explorer`) -> impact map -> characterisation tests -> `feature-dev:feature-dev` for design -> smallest compatible change |
| Bugfix | defect with a symptom | `superpowers:systematic-debugging` reproduces first -> failing test -> fix -> mutation re-run. No symptom workarounds on complex bugs |
| Migration | schema/data/framework | expand, backfill, switch, contract; top tier plans AND reviews; destructive step needs the owner's yes |
| Refactor | behaviour must not change | characterisation tests green first -> mechanical steps in small tickets -> same tests green after. Optional: `code-modernization` for big legacy repos (it failed to install, manifest bug; do not depend on it) |

If the job is ambiguous, ask the owner ONE question (what is the observable outcome and what
must not change) before classifying. If two shapes apply (feature that needs a migration),
run the riskier flow and put the other as a blocked_by ticket.

## 2. Roles (fresh subagent each, one bounded task each)

| Role | Does | Writes? | Notes |
|---|---|---|---|
| planner-architect | spec, ADRs, contracts, ticket split | docs/specs only | You may be this. Contracts never go to a worker |
| mapper | read-only codebase map, impact map for a change | scratch file only | Sweeps on haiku, synthesis on sonnet |
| implementer | one ticket, inside its worktree | yes, its `touches` | Default one at a time |
| tester | tests/ only, source-grounded plan, known-bad controls | tests only | Never the implementer of the same ticket |
| reviewer | fresh context, read-only, JSON verdict | no | Never self-approval. marketintel reviewer caught a merge-blocking bug in most PRs |
| integrator | rebase, run gates, merge one, re-run gates on main | git + CI | The only merger |
| release | deploy, verify live, record | deploy CLIs | Merged is not running (section 6) |

Each role has an agent file in this plugin (model pinned, tool allowlist): dispatch
`agent-team:<role>` (planner-architect, mapper, implementer, tester, reviewer, integrator,
release) and pass `model` only to override per the routing table. If the agent types are not
listed (the session started before the plugin loaded), brief a `general-purpose` subagent to
follow `agents/<role>.md` with an explicit `model`. Never leave `model` at the default.

## 3. Model routing: by cost of being wrong

Pick the cheapest model that can FINISH the job (not start it), judged by what a wrong answer
costs. Escalate on evidence of a wrong result, and escalate for ANALYSIS, not typing.

| Tier | Use for |
|---|---|
| Top tier (session model, Opus/Fable class) | Architecture, shared contracts, migrations, auth/security, final integration, infra and SQL review, any reviewer of those, deciding between two designs, root cause of a bug that already beat one agent |
| sonnet | Bounded implementation from a ticket, tests against a fixed API, integration chores (CI, rebase, conflict-free merges), mapper synthesis, ordinary review |
| haiku | Mechanical sweeps only: grep-and-list, count checks, format checks, renames, filling a section from a digest. Never judgement |

Scars: haiku judgement "comes back confident and wrong" (xmarlin); a weak default model
(qwen3.6-flash) shipped an unrunnable tool that still passed the gate (marketintel TASK-005);
TASK-157 (UNION/partition) took 3 attempts, and the rule that came out of it is to spawn a
top-tier tech-lead first after two failures. Longer table, escalation rules, per-role defaults: `references/routing.md`.

Every ticket names its model. A run on the session model that could have been sonnet is a
defect; a sonnet run on a migration is a worse one.

## 4. Parallelism: when, how many

- Parallel is allowed for: read-only exploration, review, test generation, and implementers
  whose `touches` do not overlap (paths, tables, env vars, contracts, infra resources).
- `blocked_by` is order (cannot start); `touches` is simultaneity (cannot run together).
  Check both before every dispatch (marketintel `.backlog/README.md`, frontmatter section).
- Overlap or doubt: serialise. One conflict costs more than the minutes saved.
- **Cap about 4 concurrent claude processes** and reserve the slot atomically; check-then-spawn
  raced and ran 5 against a cap of 4 (marketintel).
- Stub first: if B needs a file A is still writing, A drops a minimal working stub, then both go.

## 5. Dispatching an implementer (the mechanics)

1. Write the ticket with the `task-packet` skill. Re-verify its Premise check now.
2. Create the worktree and branch, from the base you intend to merge into:
   `git -C /ABS/REPO worktree add /ABS/REPO/../wt/T-123 -b agent/T-123 origin/main`
   (or use `superpowers:using-git-worktrees`). Absolute paths always.
3. Add `.agent-team/` to the repo's local excludes once, so the marker is never committed:
   `echo ".agent-team/" >> /ABS/REPO/.git/info/exclude`
   (in a worktree the shared file is `git -C /ABS/REPO rev-parse --git-common-dir`/info/exclude).
4. Write the ticket marker `/ABS/WT/T-123/.agent-team/ticket.json` (contract and template in
   the `task-packet` skill). It switches on the hooks: edits outside `worktree` are blocked and
   the Stop gate refuses "done" until the note, verify log and changelog fragment exist.
5. Dispatch via the `Agent` tool with explicit `model`, the ticket body, and the worktree path
   as cwd. Brief shape and report contract: `fanout`. Say "read the ticket, then do only it".
6. On return, do not read the diff first. Read the verify log, then run the Verify commands
   yourself or via `verify-against-reality`. Then review (section 7).
7. Setting `"waived": "<reason>"` in the marker disables the Stop gate. Only you set it, and
   you write the reason in the retro line.

## 6. Merging, shipping, and what "done" means

- Merge order: rebase onto current main, worker gates green, independent review, merge ONE,
  re-run integration gates on main, then the next. Conflicts on API, migration or auth go back
  to the planner (you), never to a worker.
- The integrator verifies the merge landed by reading state back, not by exit code
  (marketintel: clean git merge silently deleted a P0 ticket via rename detection; diff with
  rename detection off).
- **Merged is not running.** 5 marketintel tickets were inert in prod because the job ran
  the old image; migration must land before the image (enrichment down 1h otherwise). A ticket
  that needs a deploy states "no effect until X redeployed" and files the deploy step with a
  falsifiable prediction. xmarlin's first hosted use found 6 defects offline tests missed.
- Batch pushes to main: a one-line push cost ~15 CI minutes; a 2,000-minute allowance burned
  in a day (marketintel).
- Hosting, secrets, prod DB: workers get no prod secrets. A codex agent deployed a Cloud Run
  job to prod outside a worktree (marketintel, banned 2026-09-10).

## 7. Review lane

Reviewer is a fresh read-only subagent that never saw the implementation. Give it the diff and
the ticket, not your opinion. It returns a JSON verdict: `merge-ready | merge-with-follow-up |
blocked`; unparseable means a human looks. Route by what the change touches:

- Everything: `pr-review-toolkit:review-pr` (agents: code-reviewer, silent-failure-hunter,
  pr-test-analyzer, type-design-analyzer, comment-analyzer, code-simplifier) or `/code-review`
  from the `code-review` plugin.
- Auth, secrets, input handling, anything exposed: `claude-security:claude-security`
  (and `claude-security:scan` for a wider sweep). Reviewer on the top tier.
- SQL, infra, contracts: reviewer on the top tier, plus migration rules in `references/routing.md`.
- Asked the reviewer to find the bug? Also ask whether it established the FIX; a reviewer that
  only found it sends you into a second failed attempt (marketintel TASK-157).
- Mutation check: delete the change, re-run the suite, it must go red; also re-run on main
  (marketintel PR #127 raised test count 92 to 99 with zero added detection).

## 8. Budgets, quota, and failure triage

- Every ticket and every dispatch states a budget: max turns or tool calls, and a dollar or
  call ceiling when it spends money (xmarlin: pin `n=1`, API default bills 4).
- A multi-agent run costs about 15x a chat; one agent about 4x (Anthropic). Delegate only when
  the agent collapses reading into a conclusion.
- **Before blaming an agent, check infra and quota.** marketintel 2026-09-07: 15 of 19 runs died
  on ENOTFOUND, $32.41 and 484 agent-minutes lost, misread as bad work. 9 top-tier agents burned
  a 7-day quota in 16 hours with no ledger. Exhausted quota came back as answer text with exit 0.
  Keep a usage ledger (one line per dispatch: ticket, model, minutes, outcome).
- **Exit 0 is not success.** Read the artefacts.
- **Headless agents cannot "resume automatically".** A `claude -p` run that promises to
  continue via a background task or Monitor has no next turn. Tell agents to finish or report
  blocked, never to wait.
- Two failed agents or one revert on the same ticket: stop dispatching, spawn a top-tier
  investigation, re-read the premise.
- Failure recurring unexplained: stop and flag to the owner (cause not found yet), do not retry.

## 9. Keep the always-loaded context small

- Root `AGENTS.md` at most 8 KB; per-area `AGENTS.md` at most 200 lines; the injected
  retrospective at most 40 lines, archive read on demand. marketintel's grew to 26-34 KB after
  six cap raises and the retrospective was 57% of every dispatch's mandatory reading.
- Agents read root plus ONLY their area file. Generated CODEMAP per area, regenerated, not
  hand-written.
- A learning that repeats becomes a gate (section 0, rule 8), not a longer prose file.
- Never repeat a rejected approach: log verdict + lesson + path:line (xmarlin test registry:
  74 accepted, 73 rejected of 168).

## 10. Stop and ask the owner

Ask (do not guess) when: the outcome is not observable; a destructive or irreversible step is
next (drop, delete, force push, prod deploy, spend above budget); a contract must change; two
approved rules conflict; a failure repeats unexplained. Live prod incident: repair first
(restore, do not improve), say what you did immediately, write up after.

## Files in this skill

- `references/flows.md`: step lists per job type with the exact external skill/agent names.
- `references/routing.md`: model table by cost of being wrong, per-role defaults, escalation,
  migration and SQL rules, concurrency numbers.
- Sibling skills: `task-packet` (ticket), `verify-against-reality` (closing proof).
  Built: `agent-team:codebase-map` (mapper method), `agent-team:review-lane` (reviewer checklist and verdict).
  Planned in the design doc, not yet built: adr-contracts, ship-loop, retro-ledger. Do those steps by hand with the rules above until they exist.
