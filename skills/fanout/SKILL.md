---
name: fanout
description: Delegate work to subagents with a strict context budget - each subagent reports only a compressed summary and writes bulk output to disk, so the parent context stays small. Use when a task needs broad search across many files, several independent workstreams that can run in parallel, reading or auditing more material than should enter the main conversation, or whenever the user says "fan out", "spawn agents", "delegate this", "use subagents", or "parallelize".
---

# Fanout: context-optimized delegation

The parent context is the scarce resource. A subagent that returns raw file dumps
costs more than doing the work inline. Delegation is only a win when the agent
**collapses** a large amount of reading into a small amount of conclusion.

This skill authorizes use of the `Agent` tool.

## 1. Decide whether to delegate

Delegate when **at least one** holds:
- Answering requires sweeping many files/dirs and you only need the conclusion.
- Two or more workstreams are independent and can run concurrently.
- The material to read is larger than the answer it produces (compression ratio > ~5:1).

Do **not** delegate when:
- You already know the file and just need one value → read it directly.
- The task is one edit in one known file.
- The subagent would need most of the parent's context to be briefed — briefing
  cost exceeds the savings.

Never run a search yourself that you already handed to an agent.

## 2. Pick the agent type

| Need | Type |
|---|---|
| Locate code / sweep for patterns, read-only | `Explore` |
| Research a question, multi-step, may run commands | `general-purpose` |
| Design an implementation strategy | `Plan` |
| Anything else | `claude` |

Use `model: haiku` for mechanical fan-out (grep-and-list, file triage, format
checks). Reserve the default model for judgment.

## 3. The prompt contract — copy this into every `Agent` prompt

Every subagent prompt has four blocks, in this order:

1. **Context** — the minimum standalone briefing. The agent cannot see this
   conversation. Give absolute paths, the exact question, and any constraint it
   would otherwise have to rediscover.
2. **Task** — one concrete objective. Bound it ("check these 4 dirs", not "check
   the repo"). One objective per agent; split anything with an "and".
3. **Scratch path** — where bulk output goes. Give it a file under the
   scratchpad directory. Full listings, raw excerpts, per-file notes are written
   there, not returned.
4. **Report contract** — paste verbatim:

```
REPORT CONTRACT — follow exactly:
- Return at most 15 lines of plain text. No preamble, no restating the task.
- Format:
  VERDICT: <one line answering the objective>
  EVIDENCE: <up to 5 bullets, each `path:line — 10-word claim`>
  DETAIL: <absolute path to the file where you wrote the full output, or "none">
  GAPS: <what you could not determine, or "none">
- Never paste file contents, diffs, logs, or code blocks into this report.
  Write them to the scratch file and cite the path.
- If the answer is "no" or "nothing found", say so in one line and stop.
```

Add `schema`-shaped expectations in the task text when you need structured
fields back; keep the total under the 15-line cap regardless.

## 4. Fan out in parallel

Independent agents go in **one message with multiple `Agent` tool calls** — they
then run concurrently. Sequential calls serialize for no reason.

Default ceiling: **5 concurrent agents**. Beyond that, batch in waves and merge
between waves — more agents in flight than that usually means the task wasn't
decomposed, it was shredded.

Leave `run_in_background` at its default (true) unless your very next action
depends on that one result and nothing else can usefully happen meanwhile.

## 5. Continue, don't respawn

To follow up with an agent that already has the context, use `SendMessage` with
its name — a fresh `Agent` call pays the whole briefing cost again. `ListAgents`
shows who is reachable.

## 6. Merge

- The agent's report is **not** shown to the user. Relay what matters.
- Read a scratch DETAIL file only when the verdict alone is not enough to act.
- Conflicting verdicts → do not average them. Open the cited evidence and
  resolve it yourself.
- Treat a subagent's claim as a claim, not a fact, when it drives a
  destructive or outward-facing action. Verify first.

## Worked example

```
Agent(subagent_type: "Explore", model: "haiku", description: "find auth entrypoints",
prompt: """
CONTEXT: Repo at /Users/x/proj. Express + TypeScript. I need to know every place
a request is authenticated before I refactor the middleware.

TASK: Find all authentication entry points — middleware, route guards, manual
token checks. Search src/ and api/ only. Do not read node_modules.

SCRATCH: Write the full per-file breakdown to
/private/tmp/.../scratchpad/auth-entrypoints.md

REPORT CONTRACT — follow exactly:
- Return at most 15 lines of plain text. No preamble, no restating the task.
- Format:
  VERDICT: <one line answering the objective>
  EVIDENCE: <up to 5 bullets, each `path:line — 10-word claim`>
  DETAIL: <absolute path to the file where you wrote the full output, or "none">
  GAPS: <what you could not determine, or "none">
- Never paste file contents, diffs, logs, or code blocks into this report.
  Write them to the scratch file and cite the path.
- If the answer is "no" or "nothing found", say so in one line and stop.
""")
```
