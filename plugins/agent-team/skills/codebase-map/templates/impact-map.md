# Impact map: {{ticket id / change}}

Date {{DATE}}, base commit {{SHA}}. Read-only. Every row: path:line or UNVERIFIED.

## Change in one line
{{what behaviour changes; what must stay identical}}

## Entry points altered
- {{path:line}}

## Affected areas
| Area | Why | In packet `touches`? | Area file read? |
|---|---|---|---|
| {{area}} | {{reason}} | {{yes/NO: fix the packet}} | {{yes}} |

## Contracts
| Contract | Owner | Read/write | Consumers | Compatible? |
|---|---|---|---|---|
(cross-area incompatible change = stop, lead decides)

## Callers and readers (grep of every changed name: symbol, table, column, route, env var, flag)
| Name | Hits (count) | Notable path:line | Dynamic/uncertain use |
|---|---|---|---|

## Covering tests
| Unit changed | Test file | What it really asserts | Meaningful? |
|---|---|---|---|

## Runtime signals
{{logs/metrics/jobs/dashboards that show breakage; deploy-order dependencies}}

## Characterisation tests to write BEFORE editing
| # | Behaviour to pin | Where | Run command | Passes on unmodified main? |
|---|---|---|---|---|

## Smallest compatible change
{{narrowest edit set; files that must not change}}

## UNVERIFIED
- {{...}}
