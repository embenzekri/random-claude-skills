# Flows per job type

External names verified on disk 2026-10-18 under
`/Users/elmahdibenzekri/.claude/plugins/cache/claude-plugins-official/`:
superpowers 7.0.0 skills: brainstorming, writing-plans, executing-plans, subagent-driven-development,
test-driven-development, using-git-worktrees, verification-before-completion, systematic-debugging,
dispatching-parallel-agents, requesting-code-review, receiving-code-review, finishing-a-development-branch.
feature-dev: command `feature-dev:feature-dev`; agents code-explorer, code-architect, code-reviewer.
pr-review-toolkit: command `pr-review-toolkit:review-pr`; agents code-reviewer, silent-failure-hunter,
code-simplifier, comment-analyzer, pr-test-analyzer, type-design-analyzer.
code-review: command `code-review:code-review` (PR review). claude-security: skill
`claude-security:claude-security`, command `claude-security:scan`.
`code-modernization` is NOT installed (manifest bug): optional, only for big legacy repos, install later.

All flows share the loop: ticket -> premise check -> worktree + marker -> implementer ->
verify -> independent review -> integrator merges one -> integration gates on main -> release
-> record one retro line.

## A. Greenfield app

1. Clarify outcome with the owner, one question at a time: `superpowers:brainstorming`.
2. You (top tier) write: spec, 3-7 ADRs (one line each: date, decision, data, what it rules out),
   and the contract files (API schema, DB schema, event shapes, env/config names, shared
   constants). One owner per derived value.
3. Architecture default: modular monolith, one module per business capability, public
   interface per module, contract-first boundaries. Split into services only for a measured
   scaling or security reason. New component = new package, not growth of an existing one,
   to keep agent context small (marketintel AGENTS.md "build new components independent").
4. Plan: `superpowers:writing-plans`, then split into tickets with `task-packet`.
5. Vertical slice first (one thin path through every layer, deployed and verified live) before
   breadth. xmarlin's first hosted use found 6 defects offline tests never saw.
6. Execute: `superpowers:subagent-driven-development`, constrained by this plugin: one
   implementer, worktree per writer, ticket marker, `superpowers:test-driven-development`
   inside each ticket.
7. UI work: design package first (`design-inspiration` then `design-concepting`), then code.
8. Stack skills as needed (Cloudflare: `workers-best-practices`, `wrangler`, `cloudflare`).
9. Seed the repo: root AGENTS.md (at most 8 KB), area AGENTS.md as areas appear, a 40-line
   retrospective, decision log, `.agent-team/` in local excludes.

## B. Feature in a big existing repo

1. MAP (read-only, no edits): mapper subagent(s). Haiku for "which files mention X"
   sweeps; sonnet to synthesise. Use `feature-dev:code-explorer` for tracing a flow.
   Output: a CODEMAP of the touched area, entry points, dependency direction, test coverage
   of the area, and an IMPACT MAP for this change (what reads/writes the things you will change).
2. Characterisation tests: tester pins current behaviour of everything in the impact map that
   lacks tests. Must pass on unmodified main first.
3. Design: `feature-dev:feature-dev` (uses code-architect) or `superpowers:brainstorming`;
   choose the SMALLEST compatible change. Cross-area change = cross-area decision, yours.
4. Contracts that cross areas are fixed by you before tickets exist.
5. Tickets via `task-packet`, one per area, `touches` honest, serialise overlaps.
6. Implement with TDD, review with `pr-review-toolkit:review-pr`, merge, verify live.
7. Update the area AGENTS.md/CODEMAP in the same PR if you changed a boundary.

## C. Bugfix

1. Reproduce before thinking: `superpowers:systematic-debugging`. Query reality (live data,
   real logs), not the code. A reviewer that "found" a bug against the wrong database called
   correct work fabricated (marketintel tech-lead.md).
2. Write the failing test or the failing live query. No repro = no fix.
3. Complex bug (prod data, schema, spend, or one agent already failed): top-tier investigation
   first, output is a root cause with file:line, then a sonnet implementer.
4. Fix, then DELETE the fix and confirm the test goes red, restore, confirm green.
5. Fix bugs found nearby inline when small; only a `complex` finding earns a new ticket
   (marketintel inline-fix rule, enforced as a gate, not prose).
6. Prod incident: restore first, improve later, tell the owner at once.

## D. Migration (schema, data, framework)

1. Top tier writes the plan and reviews the diff. Nothing here goes to haiku.
2. Expand -> backfill -> switch -> contract. Each phase its own ticket and its own deploy.
   Additive and idempotent SQL, dated files, never edited after landing.
3. Execute EVERY SQL statement against a real engine (CI service container or pglite):
   3 Postgres-fatal statements shipped under green suites in marketintel.
4. Migration lands BEFORE the image that needs it. Recheck grants after: `drop ... cascade`
   silently revoked reader grants and blanked dashboards; a non-owner GRANT returns success and
   grants nothing. Check owner with `pg_class.relowner`, ACL with `has_table_privilege`.
5. Backfills: check triggers first (an `updated_at` trigger surprised 3 backfills).
6. Destructive step (drop, delete, truncate, contract phase): owner says yes in chat, in that
   session. Rollback written in the ticket before the phase runs.
7. Framework migrations: codemod/mechanical steps in small tickets; optionally
   `code-modernization` on a big legacy repo once it installs.

## E. Refactor (behaviour must not change)

1. Characterisation tests first (flow B step 2), green on unmodified main.
2. Mechanical steps in small tickets, each independently revertible. Sonnet implements,
   haiku only for pure renames/format with a verify command that proves no behaviour change.
3. Same tests green after, plus the mutation check. Public contract diff must be empty
   unless a ticket says otherwise.
4. Never mix refactor with feature in one PR.

## Closing every flow

- `superpowers:verification-before-completion` and `verify-against-reality` before anyone says done.
- `superpowers:finishing-a-development-branch` is NOT used for merging here: the integrator owns it.
- One retro line appended (what bit us, what gate now exists). Repeat lesson -> make it a gate.
