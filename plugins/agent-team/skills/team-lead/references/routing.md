# Routing, budgets, concurrency

## Model by cost of being wrong

| Work | Model | Why / scar |
|---|---|---|
| Architecture, ADRs, module boundaries | top tier | Wrong design is paid for in every later ticket |
| Shared contracts (API, schema, constants, env) | top tier, by the lead | xmarlin colorway list in 4 places drifted, every order 400'd |
| Migrations: plan, diff review, rollout | top tier | marketintel: 3 Postgres-fatal statements under green suites; image shipped before migration, enrichment down 1h |
| Auth, secrets, input handling, security review | top tier + `claude-security` | Blast radius is the whole product |
| Infra and SQL review | top tier | codex agent deployed a prod job unsandboxed; cascade drop revoked grants |
| Final integration, conflict resolution on API/migration/auth | top tier | Conflicts here are design decisions |
| Root cause of a bug that already beat one agent | top tier | Spend on analysis, not typing |
| Bounded implementation from a ticket | sonnet | Cheapest tier that can finish; escalate on evidence |
| Tests against a fixed API, characterisation tests | sonnet | Needs the expected behaviour stated in the ticket |
| Integration chores: rebase, CI fixes, changelog assembly | sonnet | Mechanical but must read output |
| Ordinary code review | sonnet | Top tier if the diff touches the rows above |
| Mapper synthesis, ticket drafts from a digest | sonnet | |
| grep-and-list, counts, format/lint sweeps, renames, filling a section from a digest | haiku | Mechanical only. Haiku judgement "comes back confident and wrong" (xmarlin) |

Dividing line: **can the agent verify its own output here, or does it need knowledge it cannot
check?** Verifiable here goes down a tier; needing unverifiable knowledge goes up.

Rules:
- Every ticket names an exact model. Never inherit the CLI default (marketintel TASK-005).
- Judge the tier, not the vendor: weaker models passed the gate and shipped unrunnable code.
- Escalate on evidence (a wrong result, a failed gate, two failures), never on feeling.
- When two options differ in cost and quality, tell the owner both and say which is which.
- Say in your final report which model did which job.

## Per-role defaults

planner-architect top; mapper haiku sweeps + sonnet synthesis; implementer sonnet (top for
migration/contract/auth tickets); tester sonnet; reviewer sonnet (top for infra/sql/auth/
contracts); integrator sonnet (top when resolving semantic conflicts); release sonnet.

## Concurrency and budgets

- Cap about 4 concurrent claude processes. Reserve the slot atomically (PID slot lock);
  check-then-spawn ran 5 against a cap of 4.
- WIP: keep few. marketintel ran WIP 20 with a production sub-limit of 6; as a solo owner
  start at 2-3 tickets in flight.
- Do not dispatch a ticket whose `touches` overlaps an active one, nor whose `blocked_by` is open.
  Ignore merged `agent/*` branches when scanning active claims (202 remote refs vs 17 real).
- Allocate ticket ids with a tool under a lock, never by hand (two sessions allocated the same
  id twice in one day; a duplicate id made every backlog tool throw and every PR red).
- Check provider quota before dispatch. Keep a ledger line per dispatch.
- A dispatch that spends money carries a ceiling in the ticket (dollars or max calls), and a
  preflight price check where the provider offers one.
- Dispatch priority: customer-visible product before margin before machinery. A machinery
  ticket must name the throughput it unblocks (18 of ~90 todo tickets were fleet tooling).

## Triage order when a run fails

1. Infra: network (ENOTFOUND), auth, quota/rate limit, disk. 15 of 19 runs died on ENOTFOUND.
2. Harness: did the process exit before the agent finished, did the hook block it.
3. Premise: is the ticket's claim still true.
4. Only then: agent quality, and then escalate model for analysis.

## Context-size caps

Root AGENTS.md at most 8 KB. Area AGENTS.md at most 200 lines. Injected retrospective at most 40
lines. Raising a cap needs a written justification; re-derive caps from main at merge time,
never copy forward.
