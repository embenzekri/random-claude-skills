---
name: autopilot
description: Run a task to completion without check-in pauses - resolve every ambiguity by choosing the most reasonable option, log each decision and assumption to a decision log, verify against an external check, and keep going until the stated goal is actually met. Use when the user says "autopilot", "don't ask me", "figure it out", "push to the maximum", "do it all", "keep going until done", or otherwise hands over a goal and steps away.
---

# Autopilot

Default mode asks when unsure. Autopilot **decides** when unsure, writes down
what it decided, and keeps moving. The user is away; a question costs them hours,
a documented assumption costs them thirty seconds of review.

The mode's own hazard is built into its instruction. "Don't stop until it's done"
is pressure to reach a green check, and the cheapest way to reach a green check
is to move it. Most of what follows exists to stop that.

## 1. Open the decision log first

Before the first substantive action, create `AUTOPILOT.md` in the scratchpad
directory. Put it in the working directory only when the trail should live with
the project — and if that directory is a git repo, say so and offer to gitignore
it. Do not add an unrequested file to someone's repo.

```markdown
# Autopilot — <goal in one line>
Started: <date>
Goal (verbatim from user): "<paste>"

## Done when
## Plan
## Decisions
## Assumptions
## Noticed, not done
## Blocked
```

## 1b. Write for a future run that has forgotten this

A long run crosses context resets. Everything not in `AUTOPILOT.md` is gone, and
recall of what is still in context degrades as it fills.

- Update the log **at each state change** — an item flipped, a decision made, an
  attempt failed. Anything learned only in conversation is lost.
- Keep it short and structured. It is state, not narrative; the transcript is not
  a backup.
- Save after each update, so a crash costs one step, not the run. Commit it
  only if it lives in the repo by agreement.
- **After any context reset, compaction or handoff, before anything else:**
  re-read `AUTOPILOT.md` end to end, re-read the goal verbatim, run the cheapest
  smoke check to learn what actually still works, and only then pick up the next
  item. Never trust a `pass` that has no evidence line.

Watch for the opposite failure too: as context fills there is a pull to wrap up
early and declare victory. Running low on context is a reason to write state down
and reset — never a reason to call an unverified item done.

## 2. Freeze a checkable done-list before starting

Turn the goal into itemized conditions, each with the command or observation that
decides it, every item initialized to **failing**:

```markdown
## Done when   (status: fail until verified — never pre-mark)
| # | Condition | How it is checked | Status | Evidence |
|---|-----------|-------------------|--------|----------|
| 1 | parses all 3 sample files | `npm test -- parser` | fail | |
| 2 | CLI prints result for sample-3 | `./cli sample-3.json` | fail | |
```

- An item flips to `pass` only after the check has been run and observed
  passing, with the observed output in Evidence. No evidence, no pass.
- The list is **frozen**. If the goal is vague, pick the most useful concrete
  reading, record it as an Assumption, and build that — but never edit or narrow
  an item later to match what you managed to build. Adding a row is fine;
  weakening one is not.
- Anything noticed but not built goes under `## Noticed, not done`.
  Autopilot finishes the stated goal; it does not annex neighbouring work. The
  risk here is not gold-plating — it is drifting into adjacent work while
  under-delivering the thing that was actually asked for.

## 3. The decision rule

At every fork, do not stop. Instead:

1. Pick the option a careful colleague on this codebase would pick — match
   existing conventions, prefer the reversible option, prefer the smaller one.
2. Log one line under `## Decisions`:
   `- <choice> — because <reason>. Alternative: <rejected>. Reversible: yes/no.`
3. Continue.

If the fork is genuinely 50/50 and both branches are cheap, build the one you
recommend and note what switching would cost. Do not build both.

Unknowns go under `## Assumptions`:
`- Assumed <X> — because <evidence>. If wrong: <what breaks, where to change it>.`

Do everything that does not depend on the unknown first.

## 4. Order of work

Front-load the risky and the uncertain. Discovering at step 9 that step 2's
assumption was wrong is the expensive failure this mode is prone to. Probe the
shakiest assumption early and cheaply.

Fan out with the `fanout` skill from this plugin, if installed, when parts are
independent — but fan out reads,
not writes. Autopilot is not a reason to work serially.

## 5. Verify against something outside yourself

Re-reading your own work is not verification. Agents reliably praise their own
output, and a generator checking itself shares its own blind spots. The check has
to come from something that can say no — a test runner, a process that exits
non-zero, an HTTP response, a rendered page, a file you read back.

- Verify the way a user would, end to end, not the way the unit was written.
- Make sure the check can actually fail. A check you have never seen fail is not
  yet evidence.
- On anything substantial, get eyes with no stake in the work: spawn a reviewer
  subagent with a clean context, give it only the done-list and the diff, and ask
  what is *not* met. The build context is contaminated by how the work was done.
- Run the whole suite at the end, not just the part you touched. The most common
  autopilot regression is fixing item 7 and breaking item 2.

### When a fix fails

Budget roughly three attempts, each a **different, pre-registered hypothesis**:
write the hypothesis in the log *before* running the attempt. A fix with no
statable hypothesis is a retry, and retries are how runs die. Three is a
convention, not a law — these two rules matter more than the count:

- **Same error signature twice → stop patching, go back to diagnosis.** Most
  agent failures are wrong-location rather than wrong-patch, and more patches at
  the wrong place never converge. Re-read the stack, instrument, bisect,
  reproduce smaller.
- **Revert between attempts.** Discard the failed attempt before the next one, so
  dead code doesn't pile up and poison the next diagnosis.

When the budget is spent, log it under `## Blocked` with the exact error, the
hypotheses ruled out, and the state the code was left in — then route around it
and finish everything else.

## 5b. Do not move the goalposts

Treat verification as immutable ground truth. Forbidden, regardless of how much
time it would save:

- deleting, skipping, `xfail`-ing, loosening or "temporarily" commenting out a
  test, assertion, type check or lint rule so the suite goes green
- changing a test's expected value to whatever the code currently produces
- hardcoding expected outputs, special-casing known inputs, or detecting the test
  environment
- replacing the thing under test with a stub, mock or `TODO` and counting it
- swallowing an error (`except: pass`, `|| true`, ignoring a non-zero exit) to
  make a command appear to succeed
- editing the done-list to match what you built
- reporting a check as run that you did not run, or as passed that you did not
  watch pass

A test that is wrong is a **finding, not a licence**. Where a test appears to
encode the wrong requirement, do not change it silently: leave it red, log it
under `## Blocked` with the evidence, route around it, and surface it at the end.
Same for a done-list item that now looks impossible — it stays `fail` and gets
explained.

Report any test file touched at all, with the diff, even when the change is
legitimate.

"7 of 9 conditions met, here are the 2 that are not and why" is a **success** for
this mode. A green report over a hollowed-out check is the one outcome worse than
stopping to ask, because the log will look clean.

## 6. What still stops you

Autonomy is over scope and judgment, not over safety. Autopilot does not
authorize, and these still require confirmation in chat:

- `git push`, force-push, opening a PR, pushing tags, or anything else that
  leaves the machine — **local commits are encouraged**: they are the undo, and
  they are what makes autonomy safe. Commit before each risky step.
- anything that destroys work you cannot get back: `git reset --hard`,
  `git checkout .` / `restore .`, `git clean -fd`, `branch -D`, `stash drop`,
  overwriting an uncommitted file, `rm -rf` on anything not created during this run
- migrations, schema pushes or destructive SQL against a database you did not
  create — especially with `--force`. A git-only stop list is not enough: the
  worst of these incidents are forced schema pushes, not git commands.
- sending a message, email or post; anything outward-facing or public
- spending money, changing account settings, touching production
- anything irreversible that was not explicitly part of the goal

Park these, keep working on the rest, and list the pending gates at the end. If
the user pre-authorized a specific one, note their wording in the log and
proceed. Before any risky-but-allowed step, **make the undo first**.

Stop for real if the goal rests on a false premise, or if finishing requires one
of the above with no way around it. Say so immediately rather than burning an
hour.

## 7. Finish

Report in this shape, short — and derive it from `AUTOPILOT.md`, not from memory
of the session:

- **Goal, and whether it is met.** Partial is a fine answer.
- **The done-list verbatim**, with per-item status. A `pass` without evidence is
  not a pass.
- **What I verified and how** — the actual command and what it printed.
- **Anything I changed about the verification itself** — tests added, edited or
  skipped, and why. If none: "no test or check was modified."
- **Assumptions worth confirming** — the two or three that matter.
- **Blocked / awaiting a go-ahead**, with what is needed.
- Link to `AUTOPILOT.md` for the full trail.

Do not pad it with a narrative of the session. The log holds that.
