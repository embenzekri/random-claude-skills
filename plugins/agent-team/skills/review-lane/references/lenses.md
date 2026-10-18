# Lenses: what to delegate, how to brief, how to treat the output

Names confirmed installed (18 Oct 2026) under `/Users/elmahdibenzekri/.claude/plugins/cache/claude-plugins-official/`:
- `pr-review-toolkit` agents: `code-reviewer`, `silent-failure-hunter`, `pr-test-analyzer`,
  `type-design-analyzer`, `comment-analyzer`, `code-simplifier`; command `review-pr`.
  Spawn as `pr-review-toolkit:<agent>` via the `Agent` tool.
- `code-review` plugin: command `/code-review`.
- `claude-security`: skill `claude-security:claude-security`; skill `claude-security:scan`
  (the `claude-security:claude-security` AGENT only runs as a session's main agent, never dispatch it as a subagent).
- `superpowers` 7.0.0: skills `requesting-code-review`, `receiving-code-review`.
  `requesting-code-review` is the author-side companion (how the implementer asks); `receiving-code-review`
  is how the implementer processes your verdict (verify before applying, no blind agreement). Point to them in the
  handoff; do not run them yourself.

## Brief for every lens agent

```
Review ONLY this diff: /ABS/SCRATCH/diff.patch (repo checkout: /ABS/WT, read-only).
Ticket intent: <goal + acceptance, 3 lines>. Focus: <lens focus>.
Return candidates as: file:line | claim | how to reproduce. No praise, no style nits, no fixes applied.
Max 15 lines. Do not edit files.
```
Run in parallel (cap about 4). Lens agents default to `All tools`: say "do not edit" in the brief
and check `git -C /ABS/WT status --porcelain` is empty afterwards (a dirty tree means a lens wrote; discard and note it).

## Routing by diff content

| Signal in diff | Lens | Focus line for the brief |
|---|---|---|
| any code | `pr-review-toolkit:code-reviewer` | bugs, logic errors, project-guideline violations (it reads CLAUDE.md) |
| `catch`, `except`, `.catch(`, `?? default`, `|| fallback`, `|| true`, retries, `2>/dev/null` | `silent-failure-hunter` | errors swallowed, fallbacks hiding failure, exit-0-after-failure |
| files under tests/, `*.test.*`, `*_spec*` | `pr-test-analyzer` | does each new test fail without the change; behaviour not implementation; gaps |
| new `type`/`interface`/`class`/enum/schema/zod | `type-design-analyzer` | invariants, illegal states representable, a derived value stored twice |
| comment/docstring/README edits | `comment-analyzer` | comments that lie about the code |
| login, tokens, permissions, parsing user input, SQL built from strings, shell exec, file paths, CORS, secrets, env | `claude-security:claude-security` skill on the changed paths; top-tier reviewer | injection, authz gaps, secret exposure |
| `.sql`, migrations, views, grants, Terraform/Dockerfile/workflow/IaC, API schemas, shared constants | top-tier reviewer yourself + checklist below | see below |
| big diff, nothing special | `/code-review` as a second opinion | correctness |

`code-simplifier` is not a review lens (it edits). Skip it.

## SQL / migration / infra checklist (top tier)

1. Execute every changed statement against the real database, read-only or in a rolled-back
   transaction. Never trust a green suite: UNION ALL + ORDER BY shipped 3 times under green tests.
2. Order: expand, backfill, switch, contract. A destructive step (drop, delete, truncate,
   cascade, force push, prod deploy) needs the owner's explicit yes: finding `blocker` if absent.
3. After DDL/view/function change re-check grants the consumer needs (`has_table_privilege(...)`);
   a cascade drop once revoked grants.
4. Migration must land before the image that needs it (enrichment down 1h otherwise).
5. Idempotent and re-runnable; no data loss on retry; rollback step exists and was stated.
6. Infra: no prod secrets in the worktree, no deploy outside CI/the release role, resources named in `touches`.
7. Contracts: every derived value has one owner (colorway list lived in 4 places and 400'd every order). A
   contract change not in the packet is `blocked`.
8. Compiled-in defaults are configuration: pinned explicitly?
9. Duplicate source of truth: two label/value maps or constants that must agree (grep both; assert one derives from the other or a test compares them).

## Treat output as unverified

Lens output reproduces rarely as stated. Typical false positives: flags behaviour that is
intentional per the packet's non-goals, cites a line the diff did not change, "missing
test" for something covered elsewhere. Step 8 of SKILL.md decides each one. Record which lens
produced a confirmed finding in `source` so the lens set can be tuned over time.
