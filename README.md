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
/plugin install random-claude-skills
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
prompt. It caps the reply at 15 lines in a fixed `VERDICT / EVIDENCE / DETAIL /
GAPS` shape, and forbids pasting file contents, diffs or logs into the reply —
bulk output goes to a scratch file that the report cites by path.

That inversion is the whole point. A subagent that returns raw file dumps costs
more context than doing the work inline; delegation only pays when the agent
*collapses* a lot of reading into a little conclusion. The skill also carries a
delegate/don't-delegate test, agent-type and model routing (cheap models for
mechanical fan-out), and a concurrency ceiling with parallel batching.

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

It grants autonomy over **scope and judgment, not safety**. Pushes, PRs, sends,
spending, production, and deleting anything uninspected still park for your
go-ahead — it keeps working on everything else and lists the pending gates at
the end. Without that floor, "push to the maximum" eventually means an
unrequested force-push.

## Caveats

Personal skills, shared as-is. They may lag behind changes to Claude Code.

`fanout` and `autopilot` are prompting patterns and should age well. **`my-chrome`
is the brittle one** — it names specific MCP tools from the Claude desktop app's
Chrome extension, and those names can change. If it starts telling Claude to
call a tool that no longer exists, that section is the first thing to check.

The 15-line cap in `fanout` is the one number worth tuning; raise it for
research-heavy work.

## License

MIT
