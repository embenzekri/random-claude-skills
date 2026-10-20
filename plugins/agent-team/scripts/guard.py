#!/usr/bin/env python3
"""agent-team PreToolUse guard. Stdlib only. Fails OPEN: any error -> exit 0, no output.

Bash rules (denied): git add -A/--all/./ ; git commit -a/-am/--all ; gh pr merge ;
git push --force/-f/+refspec (--force-with-lease and --force-if-includes allowed).
Commands are split on unquoted ; & | ( ) ` newline and tokenised with shlex, and only a
`git`/`gh` at COMMAND position is inspected, so `echo "git add ."` and `git add .gitignore`
are allowed. Heredoc bodies are stripped first (quoted: ignored; unquoted: only $(...) and
backticks inspected). Known gap: `eval "$var"`, scripts and aliases are not inspected.
File rule: if a .agent-team/ticket.json is found walking up from cwd, writes outside its
"worktree" are denied (tmp dirs allowed). Set AGENT_TEAM_GUARD_OFF=1 to disable.
"""
import json
import os
import re
import shlex
import sys

WRAPPERS = {"env", "command", "sudo", "time", "nohup", "exec", "builtin", "nice", "xargs"}
SHELLS = {"bash", "sh", "zsh", "dash"}
GIT_OPT_WITH_VALUE = {"-C", "-c", "--git-dir", "--work-tree", "--namespace", "--super-prefix", "--exec-path"}
COMMIT_VALUE_FLAGS = set("mFCctSu")
WRITE_TOOLS = {"Edit", "Write", "MultiEdit", "NotebookEdit"}

R_ADD = ("Blanket staging is blocked (it sweeps in other agents' files in a shared checkout). "
         "Stage explicit paths instead: git add path/to/file1 path/to/file2.")
R_COMMIT = ("`git commit -a/-am` is blocked (it commits every tracked change, including other agents' work). "
            "Stage explicit paths with git add <paths>, then run git commit -m '...'.")
R_MERGE = ("`gh pr merge` is blocked for agents. Open or update the PR and report it; "
           "the integrator merges.")
R_PUSH = ("Force push is blocked. Use git push --force-with-lease (or --force-if-includes) "
          "so you cannot overwrite commits you have not seen.")


def subst_in_body(body):
    """Command substitutions ($(...) and backticks) inside an UNQUOTED heredoc body."""
    out, i, n = [], 0, len(body)
    while i < n:
        c = body[i]
        if c == "\\":
            i += 2
            continue
        if c == "$" and body.startswith("$(", i):
            depth, j = 1, i + 2
            while j < n and depth:
                depth += (body[j] == "(") - (body[j] == ")")
                j += 1
            out.append(body[i + 2:j - 1 if depth == 0 else j])
            i = j
            continue
        if c == "`":
            j = body.find("`", i + 1)
            if j < 0:
                break
            out.append(body[i + 1:j])
            i = j + 1
            continue
        i += 1
    return out


def strip_heredocs(cmd):
    """Return (cmd without heredoc bodies, substitutions found in unquoted bodies)."""
    out, extra, pending = [], [], []
    q = None
    i, n = 0, len(cmd)
    while i < n:
        c = cmd[i]
        if q:
            out.append(c)
            if c == "\\" and q == '"' and i + 1 < n:
                out.append(cmd[i + 1])
                i += 1
            elif c == q:
                q = None
        elif c == "\\" and i + 1 < n:
            out.append(cmd[i:i + 2])
            i += 1
        elif c in "'\"":
            q = c
            out.append(c)
        elif c == "<" and cmd.startswith("<<", i) and not cmd.startswith("<<<", i):
            m = re.match(r"<<(-?)[ \t]*(?:'([^'\n]*)'|\"([^\"\n]*)\"|([^\s;&|()<>'\"`]+))", cmd[i:])
            if m:
                quoted = m.group(2) is not None or m.group(3) is not None
                delim = next(g for g in m.group(2, 3, 4) if g is not None)
                pending.append((delim, m.group(1) == "-", quoted))
                out.append(" ")
                i += m.end()
                continue
            out.append(c)
        elif c == "\n" and pending:
            out.append("\n")
            i += 1
            for delim, strip, quoted in pending:
                body = []
                while i < n:
                    e = cmd.find("\n", i)
                    line = cmd[i:] if e < 0 else cmd[i:e]
                    i = n if e < 0 else e + 1
                    if (line.lstrip("\t") if strip else line) == delim:
                        break
                    body.append(line)
                if not quoted:
                    extra.extend(subst_in_body("\n".join(body)))
            pending = []
            continue
        else:
            out.append(c)
        i += 1
    return "".join(out), extra


def split_segments(cmd):
    segs, cur, q = [], [], None
    i, n = 0, len(cmd)
    while i < n:
        c = cmd[i]
        if q:
            cur.append(c)
            if c == "\\" and q == '"' and i + 1 < n:
                cur.append(cmd[i + 1])
                i += 1
            elif c == q:
                q = None
        elif c == "\\" and i + 1 < n:
            cur.append(c)
            cur.append(cmd[i + 1])
            i += 1
        elif c in "'\"":
            q = c
            cur.append(c)
        elif c in ";&|()`\n":
            segs.append("".join(cur))
            cur = []
        else:
            cur.append(c)
        i += 1
    segs.append("".join(cur))
    return [s for s in segs if s.strip()]


def check_git(args):
    i = 0
    while i < len(args):
        a = args[i]
        if a in GIT_OPT_WITH_VALUE:
            i += 2
            continue
        if a.startswith("-"):
            i += 1
            continue
        break
    if i >= len(args):
        return None
    sub, rest = args[i], args[i + 1:]
    if sub == "add":
        for a in rest:
            if a in (".", "./", "--all"):
                return R_ADD
            if a.startswith("-") and not a.startswith("--") and "A" in a:
                return R_ADD
    elif sub == "commit":
        skip = False
        for a in rest:
            if skip:
                skip = False
                continue
            if a == "--all":
                return R_COMMIT
            if a.startswith("--"):
                continue
            if a.startswith("-") and len(a) > 1:
                for j, ch in enumerate(a[1:]):
                    if ch == "a":
                        return R_COMMIT
                    if ch in COMMIT_VALUE_FLAGS:
                        skip = (j == len(a) - 2)
                        break
    elif sub == "push":
        for a in rest:
            if a == "--":
                break
            if a in ("--force",):
                return R_PUSH
            if a.startswith("--"):
                continue
            if a.startswith("-") and len(a) > 1:
                if "f" in a[1:] and "o" not in a[1:a.index("f") + 1]:
                    return R_PUSH
            elif a.startswith("+") and len(a) > 1:
                return R_PUSH
    return None


def check_gh(args):
    pos, i = [], 0
    while i < len(args) and len(pos) < 2:
        a = args[i]
        if a in ("-R", "--repo"):
            i += 2
            continue
        if not a.startswith("-"):
            pos.append(a)
        i += 1
    return R_MERGE if pos == ["pr", "merge"] else None


def check_tokens(toks, depth):
    i = 0
    while i < len(toks):
        t = toks[i]
        if "=" in t and not t.startswith("-") and t.split("=", 1)[0].replace("_", "a").isalnum():
            i += 1
        elif os.path.basename(t) in WRAPPERS:
            i += 1
            while i < len(toks) and toks[i].startswith("-"):
                i += 1
        else:
            break
    if i >= len(toks):
        return None
    prog, args = os.path.basename(toks[i]), toks[i + 1:]
    if prog == "git":
        return check_git(args)
    if prog == "gh":
        return check_gh(args)
    if prog in SHELLS and depth < 3 and "-c" in args:
        k = args.index("-c")
        if k + 1 < len(args):
            return check_command(args[k + 1], depth + 1)
    return None


def check_command(cmd, depth=0):
    cmd, extra = strip_heredocs(cmd)
    segs = split_segments(cmd)
    for e in extra:
        segs.extend(split_segments(e))
    for seg in segs:
        try:
            toks = shlex.split(seg)
        except ValueError:
            toks = seg.split()
        r = check_tokens(toks, depth)
        if r:
            return r
    return None


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


def within(path, root):
    return path == root or path.startswith(root.rstrip("/") + "/")


def check_write(inp, cwd):
    fp = inp.get("file_path") or inp.get("notebook_path")
    if not isinstance(fp, str) or not fp:
        return None
    tp = find_ticket(cwd)
    if not tp:
        return None
    with open(tp, encoding="utf-8") as f:
        wt = json.load(f).get("worktree")
    if not isinstance(wt, str) or not os.path.isabs(wt):
        return None
    if not os.path.isabs(fp):
        fp = os.path.join(cwd, fp)
    fp, wt = os.path.realpath(fp), os.path.realpath(wt)
    if within(fp, wt):
        return None
    for ok in ("/tmp", "/private/tmp", "/var/folders", "/private/var/folders", os.path.realpath(os.environ.get("TMPDIR") or "/tmp")):
        if within(fp, ok):
            return None
    return ("Write blocked: %s is outside your ticket worktree %s. Edit only files inside your "
            "worktree (scratch files go in the scratchpad or /tmp); if the change truly belongs "
            "elsewhere, report it to the team lead instead." % (fp, wt))


def main():
    if os.environ.get("AGENT_TEAM_GUARD_OFF"):
        return
    data = json.loads(sys.stdin.read())
    if not isinstance(data, dict):
        return
    tool, inp = data.get("tool_name"), data.get("tool_input")
    if not isinstance(inp, dict):
        return
    cwd = data.get("cwd") if isinstance(data.get("cwd"), str) and data.get("cwd") else os.getcwd()
    reason = None
    if tool == "Bash" and isinstance(inp.get("command"), str):
        reason = check_command(inp["command"])
    elif tool in WRITE_TOOLS:
        reason = check_write(inp, cwd)
    if reason:
        sys.stdout.write(json.dumps({"hookSpecificOutput": {
            "hookEventName": "PreToolUse",
            "permissionDecision": "deny",
            "permissionDecisionReason": reason}}))


if __name__ == "__main__":
    try:
        main()
    except BaseException:
        pass
    sys.exit(0)
