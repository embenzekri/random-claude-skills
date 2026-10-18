<!-- Area AGENTS.md template. HARD CAP 200 lines. Every claim: path:line or UNVERIFIED. -->
# AGENTS.md — `{{area}}`

Read the root [`../AGENTS.md`](../AGENTS.md) first. Map verified {{DATE}} at commit {{SHA}}.

## Purpose
{{Two sentences: what this area is responsible for and for whom. Who owns it: {{CODEOWNERS/author}}.}}

## Entry points
- {{path:line — route/handler/job/CLI/export}}

## Commands (run from the area dir; baseline {{DATE}})
| Do | Command | Baseline |
|---|---|---|
| test | `cd /ABS/REPO/{{dir}} && {{cmd}}` | {{pass N / red N: first failure}} |
| typecheck | {{...}} | {{...}} |
| run | {{...}} | {{...}} |
How to observe reality (not just unit tests): {{live query / local server + request / fixture replay}}.

## Contracts
Owns (others depend on these; changing needs the lead): 
- {{contract — path:line — consumers: areas}}
Consumes (do not redefine):
- {{contract — owner area — path:line}}

## Data stores and external services
- {{table/collection, read or write, path:line}}; {{service, env var NAME only}}

## Invariants (must stay true)
- {{rule — why — enforced by test/gate path:line, or UNVERIFIED}}

## Gotchas
- {{trap — what happened/what to do instead — path:line}}   (resolved ones are deleted, history is archived)

## Do not touch
- {{generated/vendored/prod-critical path — reason}}
- Without the owner's yes: {{paths}}

## Tests
Where: {{dirs}}. Framework: {{...}}. Known gaps (no meaningful test): {{behaviours}}.
Characterisation tests go in {{dir}} and must pass on unmodified main.

## Depends on / depended on by
Imports from: {{areas}}. Imported by: {{areas}}. Allowed per `docs/architecture/dependency-rules.md`.
