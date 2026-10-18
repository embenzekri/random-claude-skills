---
name: codebase-map
description: Map a big existing repository for agents, produce an impact map for a proposed change, and keep the map fresh. Use when the user says "map this codebase", "onboard agents to this repo", "codemap", "AGENTS.md", "impact map", "what does this change touch", "big repo", "refresh the map", or when team-lead's big-repo flow (flow B) reaches its MAP step. Fans out cheap read-only haiku sweeps per area, synthesises on sonnet, writes a root AGENTS.md (max 8 KB), one AGENTS.md per area (max 200 lines), docs/architecture/codebase-map.md and dependency-rules.md, lists affected areas, contracts, callers, covering tests and missing characterisation tests before any edit, enforces size caps with wc -c, and turns dependency rules into a CI gate.
---

# codebase-map: make a big repo legible to agents, and keep it that way

Called by `team-lead` flow B (feature in a big repo) and flow E (refactor). Delegation briefs and
report contracts are the `fanout` skill (`/Users/elmahdibenzekri/.claude/skills/fanout/SKILL.md`):
reuse its prompt contract and report contract, do not restate them here. Ticket shape:
`task-packet`. Closing proof: `verify-against-reality`.

Three modes. Pick one, say which in your first line.

| Mode | When | Output |
|---|---|---|
| SURVEY | repo has no map, or the map is older than the last big reshuffle | the files in section 2 |
| IMPACT | a task packet or change request exists and you must know what it touches | an impact map (section 3) |
| REFRESH | a merged ticket touched an area, or a size cap is exceeded | updated area file, caps green (section 4) |

Hard rules, each with its scar:
1. **Read-only.** Mapping edits no application code. Only the map files in the target repo and
   scratch files change (fleet-kit BOOTSTRAP-PROMPT phase 3).
2. **Never invent.** Every claim is verified or marked `UNVERIFIED:` and carries `path:line`.
   An agent writing context files confabulates confidently; the markers are how you find the spots
   before ten dispatches inherit them (BOOTSTRAP-PROMPT "what to check").
3. **Run the commands, do not assume them.** A `package.json` test script is not proof tests pass
   today. Record the exit state and date.
4. **Caps are gates, not hopes.** Root 8 KB, area 200 lines. marketintel's AGENTS.md reached
   26-34 KB against an 8 KB target after six cap raises, so each raise was just another gate edit.
5. **Boundaries are the expensive thing to get wrong.** One giant area called "backend" is wrong.
   Two agents able to edit the same files at once is what the `touches` field exists to prevent,
   and only works if areas are real. Put the area boundaries to the owner as the first question.
6. **History never goes into always-loaded files.** Archive it (section 4).

## 1. Choose a depth

Count first: `git -C /ABS/REPO ls-files | wc -l` and the top-level directory list.

| Size | Approach |
|---|---|
| under about 300 files, one language | skip the fan-out; one sonnet agent surveys; still write root + area files |
| 300 to 5,000 files | one haiku sweep per top-level area (or per package), one sonnet synthesis |
| more, or monorepo with 10+ packages | as above, plus a generated per-package CODEMAP (symbol/export list) from a script, regenerated in CI; code-explorer only for flows |

Optional: the official `code-modernization` plugin has analysis agents (legacy-analyst,
architecture-critic) that overlap this. It is NOT installed (manifest bug) so never depend on it;
if installed later it may replace the sweeps for legacy-heavy repos. Installed helpers:
`feature-dev:code-explorer` (trace one flow end to end), `feature-dev:code-architect`
(only after the impact map, for design).

## 2. SURVEY

Full playbook with the exact sweep brief: `references/survey-playbook.md`. Sequence:

1. **Partition** (you, or the planner): list top-level dirs, workspace manifests, CODEOWNERS,
   CI config. Draft candidate areas; ask the owner to confirm boundaries (rule 5).
2. **Sweep wave** (haiku, read-only, parallel, at most 4 concurrent, 10-15 tool calls each).
   One agent per area, grep-and-list facts only, no judgement: entry points, build/test/lint/
   typecheck commands, imports from and to other areas, data stores and migrations, external
   services and env var names (names only, never values), owners (CODEOWNERS or git shortlog),
   test locations. Bulk goes to a scratch file; report 15 lines per the fanout contract.
3. **Verify wave** (haiku or you): run each area's test/typecheck command once, record pass/fail
   and date. Anything not run is `UNVERIFIED`.
4. **Synthesis** (sonnet, reads only the scratch files): writes the outputs below from
   `templates/`. Cross-area dependency direction and "do not touch" calls are judgement; the
   top-tier model reviews those two sections (and the area boundaries) before they are committed.
5. **Gate** (section 4 size check, plus: every `UNVERIFIED` listed in the hand-back summary).

Outputs in the target repo (templates in this skill):

| File | Cap | Template |
|---|---|---|
| `AGENTS.md` (root) | 8,192 bytes | `templates/root-AGENTS.md` |
| `CLAUDE.md` | 5 lines: pointer to `AGENTS.md` (`@AGENTS.md`), nothing else | `templates/CLAUDE-pointer.md` |
| `<area>/AGENTS.md` per area | 200 lines | `templates/area-AGENTS.md` |
| `docs/architecture/codebase-map.md` | area table, one row per area, links not prose | `templates/codebase-map.md` |
| `docs/architecture/dependency-rules.md` | allowed directions, forbidden edges, shared contracts | `templates/dependency-rules.md` |

Root holds only what every dispatch needs: mission in 3 sentences, area table with links, rules
for every area, global commands, Definition of Done pointer. Everything per-area goes in the
area file. Agents read root plus ONLY their area file. If the repo already has an AGENTS.md,
read it and restructure into this split; never overwrite blind.

Commit the map files in one batch on a branch (explicit paths, no `git add -A`), PR it, and tell
the owner the three decisions you were least sure about.

## 3. IMPACT: what does this change touch

Input: a task packet (or the owner's description). Output: `impact-map.md` from
`templates/impact-map.md`, in the scratch dir or attached to the ticket. Read the area files
first; they are the index. If an area file is oversized (over its cap) or cites paths that do
not exist, the index is stale: fall back to `grep -rIl <symbol>` and `feature-dev:code-explorer`,
and record "map drift" (file, size, dead paths) as a REFRESH item in the impact file. Scar:
marketintel customer-price-check-app AGENTS.md was 45 KB vs the 8 KB cap and cited removed
`src/lib/collections/*`. Then:

1. **Entry points** the change alters: routes, handlers, jobs, CLI commands, UI entries.
2. **Affected areas** and what each owns; compare with the packet's `touches`. A mismatch means
   the packet's `touches` is wrong: fix the packet.
3. **Contracts** read or written: API schemas, DB tables/columns/views, events, env/config
   names, shared constants, feature flags. For each: owner area, consumers, and whether the
   change is compatible. Cross-area contract change = cross-area decision, the lead's.
4. **Callers and readers**: grep every symbol, table and config name being changed, including
   strings, SQL, templates and docs. Use `feature-dev:code-explorer` for flows grep cannot see
   (dynamic dispatch, DI, reflection, events). List unresolved dynamic usage as UNVERIFIED.
5. **Tests that cover it**: for each changed unit, the test file(s) and what they actually
   assert. A test that runs the code but asserts nothing about the behaviour does not count.
6. **Runtime signals**: logs, metrics, cron jobs, dashboards that would show breakage.
7. **Missing characterisation tests**: every affected behaviour with no meaningful test gets one
   row: what to pin, where, how to run. These are written BEFORE editing and must pass on
   unmodified main (`team-lead` flow B step 2; tester role, never the implementer).
8. **Smallest compatible change** note: the narrowest edit set and what must stay byte-identical.

Sweeps for steps 4 and 5 are haiku grep-and-list; steps 2, 3, 7 are sonnet; a change that crosses
a security, migration or money boundary gets a top-tier read of the finished map.

## 4. REFRESH

Details, triggers, prune rules and the check script: `references/refresh-and-pruning.md`.

Refresh when: a merged ticket touched an area's entry points, commands, contracts or invariants;
a boundary changed (new package, moved dir, new cross-area import); a cap is exceeded; a premise
in an area file was found false. The PR that changes a boundary updates the area file in the same
PR (flow B step 7). Otherwise run a REFRESH sweep for the touched areas only.

Size check (absolute paths, run from anywhere):

```
cd /ABS/REPO && wc -c AGENTS.md CLAUDE.md && find . -name AGENTS.md -not -path '*/node_modules/*' -exec wc -l {} +
```

Fail if root over 8,192 bytes or any area file over 200 lines. Fixing a failure = prune
(move history to `docs/architecture/archive/<area>-YYYY-MM.md`, delete resolved gotchas,
replace prose with a link). Never raise a cap; the cap is a design constant, and a repeat
lesson becomes a script or a gate, not a longer file.

## 5. Boundary check (rules become gates)

Optional but recommended once `dependency-rules.md` exists: encode it as a tool config so CI
fails on a forbidden import (TypeScript: dependency-cruiser; Python: import-linter; others and
the CI snippet: `references/boundary-gates.md`). Write the config from the rules file, run it
against current main first; existing violations go to an allowlist file with a ticket each, new
ones fail. Without the gate the rules file is prose and will drift.

## Hand-back (to team-lead or the owner)

At most 15 lines: VERDICT (mode, areas mapped), FILES (path + size), UNVERIFIED count with the
file listing them, the 3 least-sure decisions, caps status. Never paste file contents.

## Files in this skill

- `references/survey-playbook.md`: partition rules, haiku sweep brief, synthesis brief, verify wave.
- `references/refresh-and-pruning.md`: triggers, size-check script, prune rules, archive layout.
- `references/boundary-gates.md`: dependency-cruiser and import-linter recipes, CI step.
- `templates/`: CLAUDE-pointer.md, root-AGENTS.md, area-AGENTS.md, codebase-map.md, dependency-rules.md, impact-map.md.
