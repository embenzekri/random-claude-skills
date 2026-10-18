<!-- docs/architecture/dependency-rules.md. Human statement of the rules; machine form: see Gate. -->
# Dependency rules

Observed {{DATE}} (from imports at {{path:line}} examples). Rules marked TARGET are intended, not
yet true; violations are listed.

## Allowed directions
```
{{ui -> api -> domain -> data ; every area -> shared ; no area -> another area's internals}}
```
| From | May import | Must not import |
|---|---|---|
| {{area}} | {{areas}} | {{areas}} |

## Shared contracts (owned by one area, changed only by a lead-approved ticket)
| Contract | Owner | Consumers | Location |
|---|---|---|---|

## Known violations (allowlist; each has a ticket, new ones fail the gate)
| Edge | Example path:line | Ticket |
|---|---|---|

## Gate
Config: `{{.dependency-cruiser.cjs | .importlinter | script}}`.
Command: `cd /ABS/REPO && {{command}}`. CI step: {{job name or "NOT YET WIRED"}}.
