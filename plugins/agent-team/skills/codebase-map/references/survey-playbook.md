# Survey playbook

Follows the fleet-kit BOOTSTRAP-PROMPT phases (read, survey with evidence, write, stop and show a
summary) at `/Volumes/MyData/ProjectsPro/ai-business/agentic-fleet-kit/BOOTSTRAP-PROMPT.md`.
Prompt contract and report contract come from `fanout`; paste its contract with the cap below.

## Partition rules

An area is an independently ownable unit of work: one directory tree (package, service, app,
migrations folder) that a single agent can change without editing another area's files.
- Start from workspace manifests (package.json workspaces, pnpm-workspace.yaml, go.work,
  Cargo workspace, pyproject, Gradle settings), top-level dirs, CODEOWNERS, CI job names.
- A directory of shared contracts (SQL migrations, API schemas, shared types) is its own area,
  flagged SHARED: two agents must never edit it at once. marketintel's `sql/` has no single
  owner and every package depends on it.
- Split an area that is too big for one 200-line file (rule of thumb: over about 40 source dirs
  or two unrelated test commands). Merge areas that always change together.
- Generated, vendored and build-output dirs are listed under "do not touch", not mapped.

## Haiku sweep brief (one per area, read-only)

Context: absolute repo path, the one area directory, the areas it must not read (others'
agents cover them; it may grep for imports of its own area's names across the repo).
Budget: 15 tool calls, `Explore` or `general-purpose` with `model: haiku`. Report cap: 15 lines
(locate/triage tier). Bulk output to `<scratch>/sweep-<area>.md`.

Ask for these facts, each as `path:line — fact`, and nothing interpretive:
1. Entry points: main files, route registrations, job/cron definitions, CLI commands, exports.
2. Commands: build, test, lint, typecheck, run. Source = manifest/Makefile/CI file and line.
   Do NOT run anything in this wave.
3. Imports out: other areas this area imports from (grep import paths), with one example each.
4. Imports in: other areas importing this area's public names (grep, count per area).
5. Data stores: tables/collections/buckets read or written, migration dirs, ORMs.
6. External services: HTTP clients, SDKs, queues, env var NAMES (never values; never print .env).
7. Tests: test dirs, framework, rough count of test files, any skipped/disabled markers.
8. Owners: CODEOWNERS lines, else top 3 authors by `git shortlog -sn -- <dir>`.
9. Smells: TODO/FIXME/HACK count, files over 1,000 lines, generated-code markers.

Haiku never judges "is this important" or "what does this do"; it lists. Lists only.

## Verify wave

For each area, one agent (haiku, may run commands) runs the area's typecheck and test command
ONCE with a timeout and records: command, exit code, pass/fail counts, date, wall time, and the
first failure line. Failing today is a finding, not a blocker: record it in the area's gotchas
("baseline red: N failures, as of date"). Never run commands that deploy, migrate or write to
real systems; list those as UNVERIFIED with the reason.
Also record, per area, how reality is observed (a live query, a running service, a real
request) as BOOTSTRAP-PROMPT demands: "run the unit tests" alone is not a verification recipe.

## Sonnet synthesis brief

Input: only the sweep and verify scratch files plus the templates. Task: fill the templates.
Rules to give it verbatim: every claim cites path:line or says UNVERIFIED; do not add facts from
general knowledge of the framework; do not merge two areas the sweeps kept apart; keep each area
file under 200 lines and the root under 8,192 bytes, checking with `wc`; put the dependency
table in `dependency-rules.md`, not in the root. Report 40 lines max (audit tier): files written,
sizes, UNVERIFIED count, decisions it was least sure about.

## Top-tier review (small)

The session model reads only: the area table, the dependency rules, each "do not touch" and
"invariants" section, and the UNVERIFIED list. Not the sweeps. It decides boundaries, flags
fabrications, and asks the owner the questions only the owner can answer (who owns what, which
paths are production-critical).

## Production-critical paths

Ask or derive from CI/deploy config: which paths, if changed, alter something customers or live
infrastructure depend on. Mark them in the root "Rules for every area" and in the area file
"Do not touch without the owner".
