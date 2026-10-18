# Severity, verdict mapping, JSON schema

## Severity

| Severity | Meaning | Examples (all from the owner's projects) |
|---|---|---|
| `blocker` | Wrong, unsafe or unprovable as shipped. Must be confirmed. | Postgres-fatal SQL under a green suite (UNION ALL + ORDER BY, TASK-136/150/157); contract changed without the lead; acceptance command fails on rerun; secret or auth bypass; destructive step without owner yes |
| `major` | Real defect or decorative proof, fixable on this ticket | mutation leaves suite green (PR #127: 92 -> 99 tests, zero added detection); log claims a value the rerun does not give; constant that already caused the same bug twice; scope creep into other areas |
| `minor` | Correctness-neutral or unconfirmed | stale comment, naming, missing edge test, any `confirmed: false` finding |
| `nit` | Taste | Do not list nits unless asked. They cause ticket spam |

Only `confirmed: true` findings may be `blocker` or `major`. An unconfirmed suspicion is capped at `minor`.

## Verdict mapping

- `blocked`: at least one confirmed `blocker`; or acceptance rerun failed; or scope/contract
  violation; or no VERIFY LOG at all; or the reviewer cannot run the acceptance command (say why).
- `merge-with-follow-up`: no blocker, sound; has confirmed `major` findings that are `fix: new-ticket`
  (complex) or UNVERIFIED items with a named owner; or merged-is-not-running with a deploy step to file.
  State why each does not block.
- `merge-ready`: acceptance reruns match, mutation goes red on production file, scope clean, no
  confirmed blocker/major open. Trivial (`fix: inline`) findings must be fixed and re-checked first,
  otherwise the verdict is not merge-ready; return it to the implementer, then review again.

## JSON schema (file `<ticket>.verdict.json`)

```
{
  "ticket": "T-123",
  "branch": "agent/T-123",
  "base_sha": "<origin/main sha reviewed against>",
  "head_sha": "<branch head reviewed>",
  "reviewer_model": "sonnet | opus",
  "verdict": "merge-ready | merge-with-follow-up | blocked",
  "auto_merge_eligible": false,
  "restricted_domains": ["infra","sql","auth","contracts"],   // those the diff touches, [] if none
  "scope": {"touches_ok": true, "out_of_scope_files": []},
  "findings": [
    {
      "severity": "blocker | major | minor",
      "file": "/ABS/WT/path/file.ts",
      "line": 42,
      "claim": "one sentence, falsifiable",
      "evidence": "command + observed output, or trace; empty only if confirmed=false",
      "confirmed": true,
      "fix": "inline | new-ticket | none",
      "source": "own | code-reviewer | silent-failure-hunter | pr-test-analyzer | type-design-analyzer | claude-security | past-defect"
    }
  ],
  "reruns": [
    {"command": "cd /ABS/WT && npm test", "expected": "90 passed", "result": "90 passed", "matches_log": true},
    {"command": "mutation: delete line 42 of /ABS/WT/src/a.ts; npm test", "expected": "red", "result": "2 failed / 90", "matches_log": true}
  ],
  "unverified": ["what could not be checked and who can"],
  "follow_ups": [
    {"title": "...", "complexity": "complex", "reason": "why inline is not enough"}
  ],
  "summary": "max 3 sentences"
}
```

Rules: comments above are explanatory only (real file is strict JSON, see `templates/verdict.json`).
`auto_merge_eligible` is true only when verdict is `merge-ready` and `restricted_domains` is empty.
A finding with `fix: inline` blocks `merge-ready` until the implementer fixed it and you re-ran.
