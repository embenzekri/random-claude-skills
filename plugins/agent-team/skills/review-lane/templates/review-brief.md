# Review brief (lead pastes this when dispatching the reviewer)

Dispatch with the `Agent` tool: explicit `model` (sonnet; top tier if diff touches
infra/sql/auth/contracts), fresh subagent, never the implementer. Use the `review-lane` skill.

```
You are the reviewer for ticket <T-123>. Use the review-lane skill. Read-only; do not merge.
Worktree: /ABS/WT        Base: origin/main        Repo: /ABS/REPO
Task packet: /ABS/PATH/T-123.md
Note: <dod.note>   VERIFY LOG: <dod.verify_log>   Changelog fragment: <path>
Restricted domains expected in diff: <none | infra | sql | auth | contracts>
Live query tool (read-only): <command, or "none">
Write the verdict to /ABS/WT/.agent-team/review/T-123.verdict.json
Report (max 15 lines, no file contents): verdict, blocking findings with file:line,
reruns that disagreed with the log, what you did not verify, model used.
Last line: {"verdict":"...","summary":"..."}
I am not giving you my opinion of the change on purpose.
```
