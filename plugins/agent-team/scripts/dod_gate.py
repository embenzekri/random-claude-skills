#!/usr/bin/env python3
"""agent-team Stop/SubagentStop gate. Stdlib only. Fails OPEN on any error.

Blocks stopping while .agent-team/ticket.json (found walking up from cwd) has an unmet
definition of done. No ticket, stop_hook_active, or non-empty "waived" -> allow.
"""
import json
import os
import sys


def find_ticket(cwd):
    d = os.path.realpath(cwd)
    while True:
        p = os.path.join(d, ".agent-team", "ticket.json")
        if os.path.isfile(p):
            return p
        parent = os.path.dirname(d)
        if parent == d:
            return None
        d = parent


def nonempty(path):
    try:
        with open(path, encoding="utf-8", errors="replace") as f:
            return bool(f.read().strip())
    except OSError:
        return False


def main():
    data = json.loads(sys.stdin.read())
    if not isinstance(data, dict) or data.get("stop_hook_active"):
        return
    cwd = data.get("cwd") if isinstance(data.get("cwd"), str) and data.get("cwd") else os.getcwd()
    tp = find_ticket(cwd)
    if not tp:
        return
    with open(tp, encoding="utf-8") as f:
        t = json.load(f)
    if not isinstance(t, dict):
        return
    w = t.get("waived")
    if isinstance(w, str) and w.strip():
        return
    wt = t.get("worktree")
    if not isinstance(wt, str) or not os.path.isabs(wt):
        wt = os.path.dirname(os.path.dirname(tp))
    dod = t.get("dod") if isinstance(t.get("dod"), dict) else {}
    missing = []
    for key, rel in dod.items():
        if rel is None:
            continue
        if not isinstance(rel, str) or not nonempty(os.path.join(wt, rel)):
            missing.append("dod.%s (%s) is missing or empty" % (key, rel))
    vl = dod.get("verify_log")
    if not isinstance(vl, str):
        missing.append("dod.verify_log is not set in the ticket")
    elif nonempty(os.path.join(wt, vl)):
        with open(os.path.join(wt, vl), encoding="utf-8", errors="replace") as f:
            lines = [ln.lstrip() for ln in f.read().splitlines()]
        if not any(ln.startswith("VERIFIED:") for ln in lines):
            missing.append("%s has no line starting 'VERIFIED:'" % vl)
        failed = [ln for ln in lines if ln.startswith("FAILED:")]
        if failed:
            missing.append("%s has %d unresolved 'FAILED:' line(s), e.g. %s" % (vl, len(failed), failed[0][:120]))
    if missing:
        reason = ("Ticket %s is not done. Fix before stopping: " % t.get("id", "?")
                  + "; ".join(missing)
                  + ". Use the verify-against-reality skill: run the real check, append 'VERIFIED: <what you proved>' "
                    "to the verify log, fix or remove every 'FAILED:' line, and write the note/changelog. "
                    "If the ticket is genuinely not doable, ask the team lead to set \"waived\" with a reason.")
        sys.stdout.write(json.dumps({"decision": "block", "reason": reason}))


if __name__ == "__main__":
    try:
        main()
    except BaseException:
        pass
    sys.exit(0)
