# random-claude-skills

Three skills I use with [Claude Code](https://claude.com/claude-code). They are
about *how* Claude works, not about any particular stack — delegation, browsing,
and autonomy.

| Skill | What it does |
|---|---|
| **`fanout`** | Delegates to subagents on a strict context budget. Each agent returns a capped summary and writes bulk output to disk. |
| **`my-chrome`** | Routes browser work to your own logged-in Chrome instead of the isolated built-in pane. |
| **`autopilot`** | Runs a task to completion without check-in pauses, logging every decision and assumption as it goes. |

## Install

As a plugin (gets all three):

```
/plugin marketplace add embenzekri/random-claude-skills
/plugin install random-claude-skills@embenzekri
```

Or copy just the ones you want:

```bash
git clone https://github.com/embenzekri/random-claude-skills
cp -R random-claude-skills/skills/fanout ~/.claude/skills/
```

Both routes work the same way — the skills fire on natural phrasing ("fan out
and…", "use my chrome", "autopilot this"), or you can invoke them explicitly
with `/fanout`, `/my-chrome`, `/autopilot`.

## What's actually in them

### `fanout`

The useful part is a **report contract** you paste verbatim into every subagent
prompt. It fixes the reply to a `VERDICT / EVIDENCE / DETAIL / GAPS /
CONFIDENCE` shape under a line budget, and forbids pasting file contents, diffs
or logs into the reply — bulk output goes to a scratch file the report cites by
path.

That inversion is the point. A subagent returning raw file dumps costs more
context than doing the work inline; delegation only pays when the agent
*collapses* a lot of reading into a little conclusion. The budget is tiered —
15 lines to locate something, 40 to audit, 80 for research — because a cap too
tight for the job just forces the parent to open the detail file anyway.

Around that: an explicit anti-delegation case (multi-agent runs cost roughly 15x
a chat interaction, and interdependent code edits are the canonical bad fit —
fan out reads, serialize writes), a partition contract so agents don't duplicate
each other, cost levers in order, and a failure-mode table.

### `my-chrome`

Picks the right browser deliberately — your real Chrome with your sessions, not
the clean pane that is logged into nothing — and loads all the extension tools
in a single call instead of one round-trip each. Prefers the accessibility tree
over screenshots, clicks by element reference rather than coordinates.

Because it is your actual account, it carries an explicit confirm-before list
(send, post, submit, purchase, settings) and a never list (passwords, payment
details, CAPTCHAs), and it forbids silently falling back to the isolated pane —
a logged-out failure looks identical to a real one.

### `autopilot`

Opens a decision log, forces a *checkable* definition of done, then at every
fork picks the option a careful colleague would pick and records
`choice — because — alternative — reversible` instead of stopping to ask. It
front-loads risky assumptions, allows three fix attempts with *different*
hypotheses before routing around a blocker, and requires observing verification
rather than asserting it.

Its largest section exists to stop one specific failure. "Don't stop until it's
done" is pressure to reach a green check, and the cheapest way to reach a green
check is to move it — deleting a failing test, changing an expected value to
whatever the code now produces, stubbing the thing under test, quietly narrowing
the done-list. So verification is treated as immutable: a wrong test is a
*finding, not a licence*, and "7 of 9 conditions met, here's why" counts as a
success. A green report over a hollowed-out check is the one outcome worse than
stopping to ask, because the log still looks clean.

It grants autonomy over **scope and judgment, not safety**. Pushes, PRs, sends,
spending, production, destructive local git, and forced schema pushes still park
for your go-ahead — local commits are *encouraged*, since a cheap undo is what
makes autonomy safe in the first place.

## Caveats

Personal skills, shared as-is. They may lag behind changes to Claude Code.

`fanout` and `autopilot` are mostly prompting patterns and should age well,
though `fanout` cites current Claude Code limits (20 concurrent subagents, spawn
depth 3) that could change. **`my-chrome` is the brittle one** — it names
specific MCP tools from the Claude desktop app's Chrome extension, and those
names can change. If it starts telling Claude to call a tool that no longer
exists, that section is the first thing to check.

Figures attributed to Anthropic come from their published engineering and
security writing; the skills cite it inline. Numbers I could only trace to
secondary coverage were left out rather than dressed up.

## License

MIT
