<!-- Root AGENTS.md template. HARD CAP 8,192 bytes. Delete these comments. Every claim: path:line or UNVERIFIED. -->
# AGENTS.md — {{PROJECT}}

First file every agent reads. Then read ONLY your area's file below. Map generated {{DATE}}.

## Mission
{{Three sentences: what this system does, for whom, what breaks if it is wrong.}}

Principles (priority order):
1. {{e.g. configuration lives in the database, never per-customer branches in code}}
2. {{...}}

Anti-example: `{{one-line shape of the mistake this codebase keeps making}}`

## Areas
Read this file, then only your area's file. Full table: `docs/architecture/codebase-map.md`.

| Area | File | Owns | Prod-critical |
|---|---|---|---|
| {{area}} | [`{{dir}}/AGENTS.md`]({{dir}}/AGENTS.md) | {{one phrase}} | {{yes/no}} |

## Rules for every area
- Stay in your area; a fix elsewhere is handed over, not made. Cross-area = the lead decides.
- Shared contracts ({{list: schemas, tables, event shapes, env names}}) change only by a lead-approved ticket.
- Allowed dependency directions: `docs/architecture/dependency-rules.md` (gate: `{{command or "none yet"}}`).
- `git add <exact paths>` only; never `-A`, `.`, `commit -a`. Never print or enter credentials.
- Prod-critical paths: {{paths}}. Changes there need the owner's yes.

## Commands (verified {{DATE}}; failing baselines noted in the area file)
| Do | Command (absolute path form: `cd /ABS/REPO && ...`) |
|---|---|
| install | {{...}} |
| test all | {{...}} |
| typecheck / lint | {{...}} |
| check context caps | `sh /ABS/REPO/scripts/check-context-caps.sh` |

## Definition of done
Verified against reality (live query, real run, a test that fails before and passes after), not
exit 0. Details: {{link to DoD doc or task-packet skill}}.

## Keeping this file small
Cap 8,192 bytes here, 200 lines per area file. History goes to `docs/architecture/archive/`, never
here. Do not raise caps. A repeated lesson becomes a gate.
