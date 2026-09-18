---
name: autopilot
description: Run a task to completion without check-in pauses - resolve every ambiguity by choosing the most reasonable option, log each decision and assumption to a decision log, self-verify, and keep going until the stated goal is actually met. Use when the user says "autopilot", "go", "don't ask me", "figure it out", "push to the maximum", "do it all", "keep going until done", or otherwise hands over a goal and steps away.
---

# Autopilot

Default mode asks when unsure. Autopilot **decides** when unsure, writes down
what it decided, and keeps moving. The user is away; a question costs them hours,
a documented assumption costs them thirty seconds of review.

## 1. Open the decision log first

Before the first substantive action, create `AUTOPILOT.md` in the working
directory (or the scratchpad if the workspace must stay clean):

```markdown
# Autopilot — <goal in one line>
Started: <date>
Goal (verbatim from user): "<paste>"
Done when: <the concrete, checkable condition>

## Plan
- [ ] step
- [ ] step

## Decisions
## Assumptions
## Blocked
```

Keep it current as you go, not at the end. It is the deliverable's receipt.

## 2. Define "done" before starting

Write the completion condition as something you can **check**, not something you
can feel. "Tests pass and the CLI prints the parsed result for all 3 sample
files" — not "the parser works". If the goal is too vague to make checkable,
pick the most useful concrete reading, record it under Assumptions, and build
that.

## 3. The decision rule

At every fork, do not stop. Instead:

1. Pick the option a careful colleague on this codebase would pick — match
   existing conventions, prefer the reversible option, prefer the smaller one.
2. Log one line under `## Decisions`:
   `- <choice> — because <reason>. Alternative: <what you rejected>. Reversible: yes/no.`
3. Continue.

If the fork is genuinely 50/50 and both branches are cheap, **build the one you
recommend** and note in the log what switching would cost. Do not build both.

Unknowns get the same treatment under `## Assumptions`:
`- Assumed <X> — because <evidence>. If wrong: <what breaks, where to change it>.`

Do everything that does not depend on the unknown first.

## 4. Order of work

Front-load the risky and the uncertain. Discovering at step 9 that step 2's
assumption was wrong is the expensive failure this mode is prone to. Probe the
shakiest assumption early and cheaply.

Fan out with the `fanout` skill when parts are independent. Autopilot is not a
reason to work serially.

## 5. Self-verify — this replaces the user's review

Nothing is "done" on the strength of having written it. Before marking a step
complete: run it, test it, curl it, open it, read the output. If there is a way
to observe the result, observe it.

When something fails, you get **three genuine attempts** at a fix, each with a
different hypothesis — not the same fix retried. If all three fail, log it under
`## Blocked` with the exact error and what you ruled out, then route around it
and finish everything else.

Never report a pass you did not see. A skipped verification is logged as skipped.

## 6. What still stops you

Autonomy is over scope and judgment, not over safety. Autopilot does **not**
authorize, and you still confirm in chat before:

- deleting or overwriting anything you have not inspected
- `git push`, opening a PR, or any commit the user did not ask for
- sending a message, email or post; anything outward-facing or public
- spending money, changing account settings, touching production
- anything irreversible that was not explicitly part of the goal

For these, park the task, keep working on the rest, and list the pending gates
at the end. If the user pre-authorized a specific one, note that in the log with
their wording and proceed.

Also stop for real: if the goal turns out to rest on a false premise, or
finishing would require an action in the list above with no way around it. Say
so immediately rather than burning an hour.

## 7. Finish

Report in this shape, short:

- **Goal + whether it is met**, stated plainly. If partially, say which parts.
- **What I verified, and how** — the actual command or check.
- **Assumptions the user should confirm** — the two or three that matter, not
  all of them.
- **Blocked / awaiting your go-ahead** — with what you need.
- Link to `AUTOPILOT.md` for the full trail.

Do not pad it with a narrative of the session. The log holds that.
