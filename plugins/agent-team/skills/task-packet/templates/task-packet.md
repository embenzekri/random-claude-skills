---
id: T-000
title: Short imperative phrase
model: sonnet            # exact: haiku | sonnet | opus (top tier). Never inherit a default.
complexity: standard     # trivial | standard | complex
touches: [src/area/**]   # paths/globs, tables, env vars, infra resources this ticket writes
blocked_by: []           # ticket ids that must be done first
risk: low                # low | medium | high (high = migration, auth, prod data, spend)
---

## Goal
One observable outcome, one sentence.

## Non-goals
- What must not change. Budgets and safety limits (max turns, $ ceiling, no prod secrets).

## Premise check
Verified <date/time>, by <who>. Each fact has a pointer or real output.
- <fact> (path/file.ts:123 | `command` -> output)

## Read set
- /abs/or/repo-relative/paths the agent may read (plus root AGENTS.md and ONE area file)

## Write set
- Exactly the paths the agent may write. Everything else is read-only.

## Contracts touched
- <contract file / shape / constant> : read-only | changes (changes go to the lead, not here)

## Acceptance
1. <number or exit status, machine-verifiable: "p95 <= 200 ms over 50 runs", "0 rows from <query>">

## Verify commands
```
cd /ABS/WORKTREE && <exact command>      # expected: <exact expected output or exit code>
```

## Rollout / rollback
- Takes effect when: <merge | deploy of X | migration Y>. Rollback: <exact revert step>.

## Deliverable + report contract
- Marker: /ABS/WORKTREE/.agent-team/ticket.json (do not edit).
- Note: <dod.note path>. Verify log: <dod.verify_log path> with lines `VERIFIED: <check> <measured value>`
  and no line starting `FAILED:`. Changelog fragment: <path or none>.
- Report (max 15 lines): files changed, each acceptance item with its measured number, anything
  you could not verify. Never paste file contents. Do not report success you did not measure.
