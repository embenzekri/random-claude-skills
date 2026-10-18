# Cross-referencing past defects

"A reviewer who reads only the diff catches syntax. A reviewer who remembers what broke last week
catches the thing that will break next week." (wallapopo tech-lead.md.) Every high-value finding there
came from connecting a PR to something outside it.

## Recipe (10 minutes, mostly haiku-grade greps; judgement stays with you)

1. List symbols: changed function names, constants, table/column names, env vars, endpoints.
2. For each, grep the sources that carry memory, in this order, skipping those the repo lacks:
   - injected retrospective: `/ABS/REPO/.backlog/RETROSPECTIVE.md` (or `docs/**/RETROSPECTIVE*`)
   - archive, only for the section the checklist points to (`RETROSPECTIVE-ARCHIVE.md`)
   - test registry / rejected-approaches log (xmarlin keeps accepted and rejected ones; do not
     re-approve a rejected approach: finding with the registry path:line)
   - history: `git -C /ABS/WT log --oneline -S'<symbol>' origin/main -- <path>` and `git log --grep='<TASK-id>'`
   - open and recently merged tickets sharing `touches` (is another ticket changing the same thing?)
3. If a defect has a recognisable shape, grep for the other copies of it in the repo and report them.
   The MVP-category constant caused the identical bug three times because nobody did this until the third.
4. Cite the old defect id in the finding `claim` so the lead can see the recurrence.

## Recurring shapes to test on every diff (from the owner's retrospectives)

| Shape | Check |
|---|---|
| Test passes against a reality that does not exist | fixture from captured real payload? effect asserted, not call text? |
| Read code instead of querying reality | production claims backed by a live query/API in the note? |
| Plausible wrong column/filter/value | run the query, eyeball rows; correct identity column used (not a raw legacy one)? |
| Reported done when partial | each acceptance line has a measured number |
| Uncommitted or unpushed work | `git status`, `origin/main..HEAD` non-empty |
| Union/ORDER BY, SQL never executed | statement run? ACLs rechecked? |
| Merged is not running | which image/migration must ship? |
| Counted a proxy / wrong unit | calls vs ads vs rows vs euros; key presence vs value presence |
| Shared default/constant | same constant reused where it was wrong before |
| Derived value in several places | one owner? colorway list x4 |
| Lockfile/changelog gates | stray lockfile change; fragment prefix `[FIX|FEAT|OPS|DOCS|PERF|CHORE]`; `CHANGELOG.md` not edited by hand |
| Conflict markers | `grep -rn '<<<<<<<'` on changed files; counter files take the max |
| Quota/infra mistaken for bad work | before blaming the implementer, check the ledger: ENOTFOUND/quota |

## Corrections
If your review disproves a claim in the PR summary or note, say which claim and the real value, and
say it in the verdict `summary`; corrections living only in a conversation are lost. If your own earlier
review missed something, say so.
