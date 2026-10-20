import json
import os
import subprocess
import sys
import tempfile
import unittest

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
GUARD = os.path.join(ROOT, "scripts", "guard.py")
GATE = os.path.join(ROOT, "scripts", "dod_gate.py")


def run(script, payload, raw=None):
    stdin = raw if raw is not None else json.dumps(payload)
    p = subprocess.run([sys.executable, "-I", script], input=stdin, capture_output=True, text=True, timeout=10)
    return p.returncode, p.stdout


def bash(cmd, cwd="/tmp"):
    return run(GUARD, {"tool_name": "Bash", "tool_input": {"command": cmd}, "cwd": cwd})


def make_ticket(tmp, **over):
    wt = os.path.realpath(tmp)
    os.makedirs(os.path.join(wt, ".agent-team"), exist_ok=True)
    t = {"id": "T-1", "role": "dev", "worktree": wt,
         "dod": {"note": "note.md", "verify_log": "verify.log", "changelog": None}, "waived": None}
    t.update(over)
    with open(os.path.join(wt, ".agent-team", "ticket.json"), "w") as f:
        json.dump(t, f)
    return wt


def write(path, text):
    with open(path, "w") as f:
        f.write(text)


class BashGuard(unittest.TestCase):
    def assertDenied(self, cmd):
        rc, out = bash(cmd)
        self.assertEqual(rc, 0)
        d = json.loads(out)["hookSpecificOutput"]
        self.assertEqual(d["permissionDecision"], "deny")
        self.assertEqual(d["hookEventName"], "PreToolUse")
        self.assertTrue(d["permissionDecisionReason"])

    def assertAllowed(self, cmd):
        rc, out = bash(cmd)
        self.assertEqual((rc, out), (0, ""), cmd)

    def test_deny_add_A(self): self.assertDenied("git add -A")
    def test_deny_add_all(self): self.assertDenied("git add --all")
    def test_deny_add_dot(self): self.assertDenied("git add .")
    def test_deny_add_A_dot(self): self.assertDenied("git add -A .")
    def test_deny_C_add_dot(self): self.assertDenied("git -C x add .")
    def test_deny_chain_and(self): self.assertDenied("cd foo && git add . && git commit -m x")
    def test_deny_chain_semicolon(self): self.assertDenied("ls; git add -A; ls")
    def test_deny_add_dashdash_dot(self): self.assertDenied("git add -- .")
    def test_deny_commit_a(self): self.assertDenied("git commit -a")
    def test_deny_commit_am(self): self.assertDenied('git commit -am "msg"')
    def test_deny_commit_all(self): self.assertDenied("git commit --all -m x")
    def test_deny_pr_merge(self): self.assertDenied("gh pr merge 12 --squash")
    def test_deny_pr_merge_repo_flag(self): self.assertDenied("gh -R o/r pr merge 3")
    def test_deny_push_force(self): self.assertDenied("git push --force origin main")
    def test_deny_push_f(self): self.assertDenied("git push -f")
    def test_deny_push_plus_refspec(self): self.assertDenied("git push origin +main")
    def test_deny_in_bash_c(self): self.assertDenied('bash -c "git add ."')
    def test_deny_subshell(self): self.assertDenied("echo hi && (git add -A)")
    def test_deny_env_prefix(self): self.assertDenied("FOO=1 git add .")

    def test_reason_guidance(self):
        self.assertIn("explicit paths", json.loads(bash("git add .")[1])["hookSpecificOutput"]["permissionDecisionReason"])
        self.assertIn("force-with-lease", json.loads(bash("git push -f")[1])["hookSpecificOutput"]["permissionDecisionReason"])
        self.assertIn("integrator", json.loads(bash("gh pr merge 1")[1])["hookSpecificOutput"]["permissionDecisionReason"])

    def test_allow_add_explicit(self): self.assertAllowed("git add src/a.ts src/b.ts")
    def test_allow_add_dot_slash_file(self): self.assertAllowed("git add ./src/x.ts")
    def test_allow_add_gitignore(self): self.assertAllowed("git add .gitignore")
    def test_allow_echo_quoted(self): self.assertAllowed('echo "git add ."')
    def test_allow_commit_m(self): self.assertAllowed('git commit -m "fix -a bug and git add ."')
    def test_allow_commit_amend(self): self.assertAllowed("git commit --amend --no-edit")
    def test_allow_force_with_lease(self): self.assertAllowed("git push --force-with-lease origin feat")
    def test_allow_force_with_lease_value(self): self.assertAllowed("git push --force-with-lease=feat:abc123 --force-if-includes")
    def test_allow_plain_push(self): self.assertAllowed("git push -u origin feat")
    def test_allow_pr_view(self): self.assertAllowed("gh pr view 12 && gh pr create --fill")
    def test_allow_status(self): self.assertAllowed("git status && git diff")
    def test_allow_quoted_heredoc_prose(self):
        self.assertAllowed("cat >> notes.md <<'EOF'\nDo not run `git add -A` here.\ngit add .\nEOF")

    def test_allow_dash_heredoc_double_quoted(self):
        self.assertAllowed('cat <<-"EOF"\n\t`git add -A`\n\tEOF\ngit status')

    def test_deny_after_heredoc_terminator(self):
        self.assertDenied("cat >> n.md <<'EOF'\nprose `git add -A`\nEOF\ngit add -A")

    def test_deny_unquoted_heredoc_substitution(self):
        self.assertDenied("cat <<EOF\nrun $(git add -A) now\nEOF")

    def test_deny_unquoted_heredoc_backtick(self):
        self.assertDenied("cat <<EOF\nrun `git add -A` now\nEOF")

    def test_allow_unquoted_heredoc_plain_prose(self):
        self.assertAllowed("cat <<EOF\ngit add -A is blocked\nEOF")

    def test_allow_non_bash_tool(self):
        self.assertEqual(run(GUARD, {"tool_name": "Read", "tool_input": {"file_path": "/x"}}), (0, ""))


class FailOpen(unittest.TestCase):
    def test_garbage(self): self.assertEqual(run(GUARD, None, raw="not json{{"), (0, ""))
    def test_empty(self): self.assertEqual(run(GUARD, None, raw=""), (0, ""))
    def test_wrong_types(self): self.assertEqual(run(GUARD, {"tool_name": "Bash", "tool_input": "x"}), (0, ""))
    def test_list_payload(self): self.assertEqual(run(GUARD, [1, 2]), (0, ""))
    def test_unbalanced_quote(self): self.assertEqual(bash('echo "unterminated'), (0, ""))
    def test_gate_garbage(self): self.assertEqual(run(GATE, None, raw="}{"), (0, ""))
    def test_gate_empty(self): self.assertEqual(run(GATE, None, raw=""), (0, ""))


class WriteGuard(unittest.TestCase):
    def setUp(self):
        self.td = tempfile.mkdtemp(prefix="at-wt-", dir=os.path.expanduser("~"))
        self.addCleanup(lambda: subprocess.run(["rm", "-rf", self.td]))
        self.wt = make_ticket(self.td)
        os.makedirs(os.path.join(self.wt, "sub"), exist_ok=True)

    def w(self, tool, path, cwd=None, key="file_path"):
        return run(GUARD, {"tool_name": tool, "tool_input": {key: path}, "cwd": cwd or self.wt})

    def test_inside_allowed(self): self.assertEqual(self.w("Write", self.wt + "/sub/a.txt"), (0, ""))
    def test_relative_inside_allowed(self): self.assertEqual(self.w("Edit", "a.txt"), (0, ""))
    def test_cwd_subdir_finds_ticket(self):
        rc, out = self.w("Write", "/Users/nobody/elsewhere.txt", cwd=self.wt + "/sub")
        self.assertIn("deny", out)

    def test_outside_denied(self):
        rc, out = self.w("Write", os.path.expanduser("~/outside.txt"))
        self.assertEqual(rc, 0)
        self.assertEqual(json.loads(out)["hookSpecificOutput"]["permissionDecision"], "deny")

    def test_dotdot_escape_denied(self): self.assertIn("deny", self.w("Edit", self.wt + "/../escape.txt")[1])
    def test_multiedit_denied(self): self.assertIn("deny", self.w("MultiEdit", "/etc/hosts")[1])
    def test_notebook_denied(self): self.assertIn("deny", self.w("NotebookEdit", "/etc/n.ipynb", key="notebook_path")[1])
    def test_tmp_allowed(self): self.assertEqual(self.w("Write", "/tmp/scratch.txt"), (0, ""))
    def test_private_tmp_allowed(self): self.assertEqual(self.w("Write", "/private/tmp/claude-501/x/scratchpad/a.md"), (0, ""))
    def test_sibling_prefix_denied(self): self.assertIn("deny", self.w("Write", self.wt + "-other/a.txt")[1])

    def test_no_ticket_allows(self):
        with tempfile.TemporaryDirectory() as d:
            rc, out = run(GUARD, {"tool_name": "Write", "tool_input": {"file_path": "/etc/hosts"}, "cwd": d})
            self.assertEqual((rc, out), (0, ""))

    def test_bad_ticket_fails_open(self):
        write(os.path.join(self.wt, ".agent-team", "ticket.json"), "{broken")
        self.assertEqual(self.w("Write", "/etc/hosts"), (0, ""))

    def test_bash_deny_still_works_with_ticket(self):
        self.assertIn("deny", run(GUARD, {"tool_name": "Bash", "tool_input": {"command": "git add ."}, "cwd": self.wt})[1])


class DodGate(unittest.TestCase):
    def setUp(self):
        self.td = tempfile.mkdtemp(prefix="at-gate-")
        self.addCleanup(lambda: subprocess.run(["rm", "-rf", self.td]))

    def gate(self, **extra):
        p = {"hook_event_name": "Stop", "cwd": self.td}
        p.update(extra)
        return run(GATE, p)

    def good(self, wt):
        write(wt + "/note.md", "done\n")
        write(wt + "/verify.log", "VERIFIED: ran tests, 12 pass\n")

    def test_no_ticket_silent(self): self.assertEqual(self.gate(), (0, ""))

    def test_pass(self):
        wt = make_ticket(self.td); self.good(wt)
        self.assertEqual(self.gate(), (0, ""))

    def test_missing_files_block(self):
        make_ticket(self.td)
        rc, out = self.gate()
        d = json.loads(out)
        self.assertEqual(d["decision"], "block")
        self.assertIn("note.md", d["reason"])
        self.assertIn("verify-against-reality", d["reason"])

    def test_empty_note_blocks(self):
        wt = make_ticket(self.td); self.good(wt); write(wt + "/note.md", "  \n")
        self.assertIn("note.md", json.loads(self.gate()[1])["reason"])

    def test_no_verified_line_blocks(self):
        wt = make_ticket(self.td); self.good(wt); write(wt + "/verify.log", "ran stuff\n")
        self.assertIn("VERIFIED", json.loads(self.gate()[1])["reason"])

    def test_failed_line_blocks(self):
        wt = make_ticket(self.td); self.good(wt)
        write(wt + "/verify.log", "VERIFIED: a\nFAILED: b broke\n")
        self.assertIn("FAILED", json.loads(self.gate()[1])["reason"])

    def test_changelog_required_when_set(self):
        wt = make_ticket(self.td, dod={"note": "note.md", "verify_log": "verify.log", "changelog": "CHANGELOG.md"}); self.good(wt)
        self.assertIn("CHANGELOG.md", json.loads(self.gate()[1])["reason"])
        write(wt + "/CHANGELOG.md", "- x\n")
        self.assertEqual(self.gate(), (0, ""))

    def test_waived(self):
        make_ticket(self.td, waived="docs-only ticket, owner approved")
        self.assertEqual(self.gate(), (0, ""))

    def test_empty_waived_does_not_waive(self):
        make_ticket(self.td, waived="  ")
        self.assertIn("block", self.gate()[1])

    def test_stop_hook_active(self):
        make_ticket(self.td)
        self.assertEqual(self.gate(stop_hook_active=True), (0, ""))

    def test_subagent_stop_same_behaviour(self):
        make_ticket(self.td)
        rc, out = run(GATE, {"hook_event_name": "SubagentStop", "cwd": self.td})
        self.assertIn("block", out)

    def test_ticket_found_from_subdir(self):
        make_ticket(self.td); os.makedirs(self.td + "/a/b")
        self.assertIn("block", run(GATE, {"cwd": self.td + "/a/b"})[1])


if __name__ == "__main__":
    unittest.main()
