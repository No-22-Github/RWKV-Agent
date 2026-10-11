#!/usr/bin/env python3
"""Trajectory behavior checks for b12 (v1.41 bash + get_weather) runs.

    python3 behavior.py <run-dir> [<run-dir> ...] [--report out.tsv] [--json out.json]

The scorer decides whether a run *passed* (answer, files, required/forbidden
tools). It cannot see whether the path actually shows the behavior the case
exists to teach: a cwd-reset case answered with list_files + read_file passes
but teaches nothing about cwd, and a bash aggregation that keeps probing after
the total is on screen passes but teaches over-exploration. This reads the
same summary.json + trace.jsonl that `corpus paths` reads and labels each
passing run:

  covered   passed, no behavior problem, and the target behavior is on the path:
            only these count toward the M9/M10 sub-class quota
  ordinary  passed, no behavior problem, but the target behavior is absent
            (e.g. cfg-9012 without a bash cd); may stay as a plain path but does
            not count toward the sub-class quota
  reject    passed, but a behavior problem was found, or `corpus paths` would
            drop the run anyway (protocol retry, forced closeout, tool error)
  fail      the scorer failed the run

Behavior problems (any kind):
  post_answer_calls  tool calls after the evidence was already complete
                     (answer literal on screen and required tools called, or
                     after the write/edit was verified)
  bash_dump          a bash call printed raw data instead of a result: >= DUMP_CHARS,
                     or >= RAW_CHARS from cat/head/tail/sed -n with no awk/wc/uniq
  whole_read         read_file of a data file (.csv/.log/.jsonl) in a case
                     whose job is to aggregate it with bash
  retry_missing      the same missing command (exit 127 / not found) was run again
  truncated_output   a bash result hit the output cap (answering from cut text)
  final_selfcorrect  the final answer corrects itself mid-text ("wait, let me")

One read of the file a search_text hit named, or one web_fetch of a page a
web_search returned, right after the evidence call is allowed as context.

Per-kind target checks are in check_*; SPEC maps each pilot case to its kind
and sub-class; later batches add theirs in tools/<batch>/specs.py (see
merge_batch_specs).
"""
import argparse
import collections
import json
import os
import re
import sys

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from distill_paths import find_case  # noqa: E402

RETRY_EVENT = "protocol_retry"  # agent.EventRetry
DUMP_CHARS = 4000
RAW_CHARS = 2000
RAW_CMD = re.compile(r"\b(cat|head|tail)\b|sed\s+-n")
AGG_CMD = re.compile(r"\b(awk|wc|uniq|sort)\b|grep\s+-c")
WRITE_TOOLS = {"write_file", "replace_lines", "append_file"}
READ_TOOLS = {"read_file", "read_lines"}
# Results that never carry answer evidence: a file size or a clock reading can
# contain the answer digits by accident.
NO_EVIDENCE_TOOLS = {"list_files", "datetime"}
MUTATE = re.compile(r"\bsed\s+-i|\bmv\s|\brm\s|\bcp\s|\bmkdir\s|\btouch\s|(?<![0-9&])>>?\s*(?!/dev/null)[^\s&|;]")
CHECK = re.compile(r"\b(ls|grep|cat|find|head|tail|diff|wc)\b")
# The shell's own diagnostic, not any output that happens to say "not found".
MISSING = re.compile(r"(^|\n)(bash: )?[^\s:]+: command not found")
# Correction-shaped phrases only: "Wait until Friday" is advice, not a revision.
SELFCORRECT = re.compile(r"\bwait[,.!—-]+\s*(let me|actually|no\b|that)|let me (re)?state|let me correct|等等，|更正一下|不对，", re.I)

SPEC = {
    # M9a many-file aggregation
    "log-9001": dict(kind="bash_aggregate", sub="M9a"),
    "tab-9002": dict(kind="bash_aggregate", sub="M9a", needs=["exports/README.md"]),
    # M9b bulk edit: targets are paths a verification command must mention
    "cfg-9003": dict(kind="bash_edit", sub="M9b", targets=["部署"]),
    "fs-9004": dict(kind="bash_edit", sub="M9b", targets=["archive/2026H1", "inbox"]),
    # M9c long files (over the read cap)
    "log-9005": dict(kind="bash_aggregate", sub="M9c"),
    "log-9006": dict(kind="bash_aggregate", sub="M9c"),
    # M9d missing command -> another way
    "scr-9007": dict(kind="cmd_missing", sub="M9d", needs=["工具/汇总.py"]),
    "web-9008": dict(kind="bash_avoided", sub="M9d", via=("web_fetch", "web_search")),
    # M9e bash offered but not the right tool
    "doc-9009": dict(kind="bash_avoided", sub="M9e", via=("read_file", "read_lines", "search_text")),
    "nt-9010": dict(kind="zero_call", sub="M9e"),
    "fs-9011": dict(kind="bash_aggregate", sub="M9e", forbid_cmd=r"\brm\b"),
    # M9f cwd does not carry over between bash calls
    "cfg-9012": dict(kind="cwd_reset", sub="M9f", subdir="服务/结算", file="超时.yaml"),
    # M10 get_weather first
    "hyb-9013": dict(kind="weather", sub="M10a"),
    "hyb-9014": dict(kind="weather_landmark", sub="M10a", landmark="鼓浪屿", city=("厦门", "Xiamen")),
    "hyb-9015": dict(kind="weather_write", sub="M10b"),
    "hyb-9016": dict(kind="weather_write", sub="M10b"),
    "hyb-9017": dict(kind="weather", sub="M10c"),
    "hyb-9018": dict(kind="weather", sub="M10d"),
    "hyb-9019": dict(kind="weather", sub="M10d", needs=["site/rules.md"]),
    "nt-9020": dict(kind="zero_call", sub="M10e"),
}


def merge_batch_specs():
    """Later b12 batches keep their cases' specs beside their builders, as a
    SPEC dict in tools/<batch>/specs.py with the same shape as SPEC above.
    A batch directory without specs.py is skipped; a case id defined twice is
    an error rather than a silent override."""
    import importlib.util
    tools = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
    for batch in ("b12a",):
        path = os.path.join(tools, batch, "specs.py")
        if not os.path.exists(path):
            continue
        spec = importlib.util.spec_from_file_location(batch + "_specs", path)
        module = importlib.util.module_from_spec(spec)
        spec.loader.exec_module(module)
        clash = set(SPEC) & set(module.SPEC)
        if clash:
            sys.exit("%s redefines %s" % (path, ", ".join(sorted(clash))))
        SPEC.update(module.SPEC)


merge_batch_specs()


# ---------------------------------------------------------------- run loading


def load_runs(run_dir):
    with open(os.path.join(run_dir, "summary.json")) as f:
        summary = json.load(f)
    turns = collections.defaultdict(dict)
    retried = set()
    with open(os.path.join(run_dir, "trace.jsonl")) as f:
        for line in f:
            record = json.loads(line)
            if record.get("kind") == "turn_result" and record.get("turn_result"):
                result = record["turn_result"]["result"]
                # The committed output rides along on a marker key so unclean()
                # can make Extract's repaired-answer comparison.
                turns[record["case_id"]][record["turn"]] = \
                    list(result.get("steps") or []) + [{"_output": result.get("output") or ""}]
            elif record.get("kind") == "runner_event" and \
                    (record.get("runner_event") or {}).get("kind") == RETRY_EVENT:
                retried.add(record["case_id"])
    for case in summary["cases"]:
        ordered = [turns[case["id"]][t] for t in sorted(turns[case["id"]])]
        reason = "protocol retry" if case["id"] in retried else unclean(ordered)
        yield case["id"], bool(case["passed"]), ordered, reason


def committed(steps):
    """Split a loaded turn into its steps and the committed Result.Output."""
    if steps and "_output" in steps[-1]:
        return steps[:-1], steps[-1]["_output"]
    return steps, None


def unclean(steps_by_turn):
    """Why `corpus paths` (internal/lab/corpus/paths.go Extract) would drop
    this run, or None. A run it drops never becomes a row, so it must not be
    counted as covered either."""
    for steps in steps_by_turn:
        steps, output = committed(steps)
        if not steps:
            return "turn without steps"
        for i, step in enumerate(steps):
            if step.get("stage") != "decision":
                return "%s stage (forced closeout)" % (step.get("stage") or "None")
            if step.get("action_type") == "tool":
                error = step.get("tool_error", "")
                fixture = (step.get("tool") == "web_fetch" and not error.startswith("invalid tool arguments")) or \
                    (step.get("tool") == "get_weather" and "location not found" in error)
                if (error and not fixture) or step.get("tool_rejected_reason") or not step.get("tool_executed"):
                    return "tool error or rejection"
            elif step.get("action_type") == "final":
                if i != len(steps) - 1:
                    return "final before the last step"
                text = (step.get("model_output") or "").strip()
                if output is not None and text != output.strip():
                    return "answer repaired by the harness"
                if not text:
                    return "empty final answer"
            else:
                return "action %r" % step.get("action_type")
    return None


class Call:
    def __init__(self, step):
        self.tool = step.get("tool", "")
        self.args = step.get("tool_arguments") or {}
        self.error = step.get("tool_error", "")
        result = (step.get("tool_result") or {}).get("result")
        self.result = result if isinstance(result, dict) else {}
        if self.tool == "bash":
            self.text = (self.result.get("stdout") or "") + (self.result.get("stderr") or "")
        else:
            self.text = json.dumps(result, ensure_ascii=False) if result is not None else ""

    @property
    def command(self):
        return self.args.get("command", "") if self.tool == "bash" else ""

    @property
    def path(self):
        return self.args.get("path", "")


def split_turn(steps):
    calls = [Call(s) for s in steps if s.get("action_type") == "tool"]
    finals = [s.get("model_output") or "" for s in steps if s.get("action_type") == "final"]
    return calls, (finals[-1] if finals else "")


# ---------------------------------------------------------------- shared checks


def literals(turn_expect):
    """Answer strings the scorer looks for, as (alternatives, whole_token)
    pairs: every pair must be shown, by any one of its alternatives, with the
    scorer's token rule when the case sets it."""
    token = bool(turn_expect.get("output_contains_token"))
    out = [((x,), token) for x in turn_expect.get("output_contains", [])]
    if turn_expect.get("output_contains_any"):
        out.append((tuple(turn_expect["output_contains_any"]), bool(turn_expect.get("output_contains_any_token"))))
    return out


def _word(ch):
    return ch.isalnum()


def contains_token(text, want):
    """Port of containsToken in internal/agent/eval/scoring.go: "7521.21" is
    not found inside "17521.21", "5" not inside "2026-05" or "5,000"."""
    start = text.find(want)
    while start >= 0:
        end = start + len(want)
        before, after = text[:start], text[end:]
        ok = True
        if before:
            if _word(before[-1]) and _word(want[0]):
                ok = False
            if len(before) > 1 and before[-1] in ".," and before[-2].isdigit():
                ok = False
        if after:
            if _word(after[0]) and _word(want[-1]):
                ok = False
            if len(after) > 1 and after[0] in ".," and after[1].isdigit():
                ok = False
        if ok:
            return True
        start = text.find(want, start + 1)
    return False


def has_literal(text, item):
    alternatives, token = item
    return any(contains_token(text, x) if token else x in text for x in alternatives)


def reads(call, path):
    return (call.tool in READ_TOOLS and call.path == path) or (call.tool == "bash" and path in call.command)


def evidence_index(calls, turn_expect, needs=()):
    """Index of the call after which the turn had all its evidence, else None:
    every answer literal shown by a result, every required tool called, and
    every file in needs (rules or definitions the answer rests on) read --
    a needed file the path never reads does not hold the stopping point back."""
    want = literals(turn_expect)
    required = set(turn_expect.get("required_tools", []))
    needs = [n for n in needs if any(reads(c, n) for c in calls)]
    if not want:
        return None
    seen, called, read = "", set(), set()
    for i, call in enumerate(calls):
        called.add(call.tool)
        read.update(n for n in needs if reads(call, n))
        if call.tool not in NO_EVIDENCE_TOOLS:
            seen += "\n" + call.text
        if required <= called and read == set(needs) and all(has_literal(seen, w) for w in want):
            return i
    return None


def follow_up(found, call):
    """One read of a source the evidence call pointed at (a search_text hit's
    file, a web_search result's page) is context, not extra exploration."""
    if found.tool == "search_text" and call.tool in READ_TOOLS:
        return call.path in found.text
    if found.tool == "web_search" and call.tool == "web_fetch":
        return any(u in found.text for u in call.args.get("urls", []))
    return False


def is_dump(call):
    if call.tool != "bash":
        return False
    size = len(call.text)
    return size >= DUMP_CHARS or (size >= RAW_CHARS and RAW_CMD.search(call.command)
                                  and not AGG_CMD.search(call.command))


def common_problems(calls, final, turn_expect, kind, needs=()):
    problems = []
    done = evidence_index(calls, turn_expect, needs)
    if done is not None and done < len(calls) - 1:
        extra = calls[done + 1:]
        if not (len(extra) == 1 and follow_up(calls[done], extra[0])):
            problems.append("post_answer_calls: %s after the answer was on screen"
                            % ", ".join(c.tool for c in extra))
    for call in calls:
        if is_dump(call):
            problems.append("bash_dump: %d chars from `%s`" % (len(call.text), call.command[:60]))
        if "[output truncated" in call.text:
            problems.append("truncated_output: `%s`" % call.command[:60])
        if kind in ("bash_aggregate", "cmd_missing") and call.tool == "read_file" and \
                call.path.endswith((".csv", ".log", ".jsonl")):
            problems.append("whole_read: read_file %s" % call.path)
    missing = collections.Counter()
    for call in calls:
        if call.tool == "bash" and (call.result.get("exit_code") == 127 or MISSING.search(call.text)):
            word = (call.command.split() or [""])[0]
            missing[word] += 1
    problems += ["retry_missing: `%s` run %d times" % (w, n) for w, n in missing.items() if n > 1]
    if SELFCORRECT.search(final):
        problems.append("final_selfcorrect")
    return problems


# ---------------------------------------------------------------- per-kind targets
# Each returns (covered, problems): covered is whether the target behavior is on
# the path; problems are path defects that reject it.


def check_zero_call(turns, spec, case):
    calls = [c for t in turns for c in t[0]]
    if calls:
        return False, ["zero_call: %d tool call(s): %s" % (len(calls), ", ".join(c.tool for c in calls))]
    return True, []


def check_bash_aggregate(turns, spec, case):
    calls, _ = turns[-1]
    problems = []
    if spec.get("forbid_cmd"):
        for c in calls:
            if c.tool == "bash" and re.search(spec["forbid_cmd"], c.command):
                problems.append("forbidden command: `%s`" % c.command[:60])
    want = literals(case["turns"][-1]["expect"])
    bash_hit = any(c.tool == "bash" and all(has_literal(c.text, w) for w in want) for c in calls)
    return bash_hit, problems


def check_bash_avoided(turns, spec, case):
    calls = [c for t in turns for c in t[0]]
    if any(c.tool == "bash" for c in calls):
        return False, ["bash_avoided: bash was called"]
    # Covered only when the intended tool itself returned the answer, not
    # when some unrelated call happened next to a passing final.
    want = literals(case["turns"][-1]["expect"])
    via = spec.get("via")
    return any((c.tool in via if via else c.tool not in NO_EVIDENCE_TOOLS | {"bash"}) and all(has_literal(c.text, w) for w in want)
               for c in turns[-1][0]), []


def check_cmd_missing(turns, spec, case):
    calls, _ = turns[-1]
    failed = [i for i, c in enumerate(calls)
              if c.tool == "bash" and (c.result.get("exit_code") == 127 or MISSING.search(c.text))]
    if not failed:
        return False, []
    # Recovery means a later call produced the answer another way, not just
    # that something after the failure succeeded.
    want = literals(case["turns"][-1]["expect"])
    later = calls[failed[0] + 1:]
    return any(c.tool not in NO_EVIDENCE_TOOLS and all(has_literal(c.text, w) for w in want)
               for c in later), []


def segments(command):
    return re.split(r"&&|\|\||[;|\n]", command)


def checked_targets(command, targets):
    """Targets named by a check command of their own (`ls inbox`), not merely
    mentioned somewhere next to one (`echo archive && ls inbox`)."""
    return {t for seg in segments(command) if CHECK.search(seg) for t in targets if t in seg}


def check_bash_edit(turns, spec, case):
    calls, _ = turns[-1]
    mutating = [i for i, c in enumerate(calls) if c.tool == "bash" and MUTATE.search(c.command)]
    if not mutating:
        return False, ["bash_edit: no bash change"]
    last = mutating[-1]
    command = calls[last].command
    # What runs after the last mutating command: skip to the next separator so
    # the mutation's own arguments (the edited path) do not count as a check.
    rest = command[max(m.end() for m in MUTATE.finditer(command)):]
    sep = re.search(r"&&|\|\||;|\n", rest)
    tail = rest[sep.end():] if sep else ""
    targets = spec["targets"]
    # Every target must be checked after the change (a move has two ends).
    # A check names the target, or runs inside it: a leading `cd <target>`
    # holds for the rest of that one call.
    checked, verified_at = set(), None
    tail_checked = checked_targets(tail, targets)
    if "cd " not in tail:
        # A leading `cd <target>` holds for the rest of that one call.
        inside = [t for t in targets if re.match(r"\s*cd\s+(/workspace/)?" + re.escape(t), command)]
        if inside and any(CHECK.search(seg) for seg in segments(tail)):
            tail_checked.update(inside)
    checked.update(tail_checked)
    if checked >= set(targets):
        verified_at = last
    for i in range(last + 1, len(calls)):
        if verified_at is not None:
            break
        c = calls[i]
        if c.tool == "bash":
            checked.update(checked_targets(c.command, targets))
        elif c.tool in READ_TOOLS | {"list_files"}:
            checked.update(t for t in targets if t in c.path)
        if checked >= set(targets):
            verified_at = i
    if verified_at is None:
        missing = [t for t in targets if t not in checked]
        return False, ["bash_edit: no check of %s after the change" % ", ".join(missing)]
    if verified_at < len(calls) - 1:
        return True, ["post_answer_calls: %s after the change was verified"
                      % ", ".join(c.tool for c in calls[verified_at + 1:])]
    return True, []


def check_cwd_reset(turns, spec, case):
    if len(turns) < 2:
        return False, ["cwd_reset: needs two turns"]
    subdir, name = spec["subdir"], spec["file"]
    target = subdir + "/" + name
    first, _ = turns[0]
    second, _ = turns[1]
    problems = []
    for c in second:
        if c.tool in READ_TOOLS and c.path.strip("./") == name:
            problems.append("cwd_reset: read root %s (decoy)" % name)
        if c.tool == "bash" and name in c.command and subdir not in c.command:
            problems.append("cwd_reset: bash read %s without %s (decoy)" % (name, subdir))
    cd_sub = re.compile(r"\s*cd\s+(/workspace/)?" + re.escape(subdir) + r"/?\s*$")
    # A real `cd` command segment, not the words inside an echo.
    cd_first = any(c.tool == "bash" and any(cd_sub.match(seg) for seg in segments(c.command)) for c in first)
    return cd_first and any(reads_target(c, subdir, name, cd_sub) for c in second), problems


def reads_target(call, subdir, name, cd_sub):
    """The call reads subdir/name: a read tool on the full path, a bash check
    command naming it, or a `cd subdir` segment followed by a check of name."""
    target = subdir + "/" + name
    if call.tool in READ_TOOLS:
        return call.path.strip("./") == target
    if call.tool != "bash":
        return False
    inside = False
    for seg in segments(call.command):
        if re.match(r"\s*cd\b", seg):
            inside = bool(cd_sub.match(seg))
        elif CHECK.search(seg) and (target in seg or (inside and name in seg)):
            return True
    return False


def check_weather(turns, spec, case):
    calls = [c for t in turns for c in t[0]]
    return any(c.tool == "get_weather" and not c.error for c in calls), []


def check_weather_landmark(turns, spec, case):
    calls = [c for c in turns[-1][0] if c.tool == "get_weather"]
    if not calls:
        return False, []
    problems = []
    tried = collections.Counter(c.args.get("location", "") for c in calls if c.error)
    problems += ["weather_landmark: retried failing location %s" % loc for loc, n in tried.items() if n > 1]
    ok = [c for c in calls if not c.error]
    covered = bool(ok) and any(name in ok[0].args.get("location", "") for name in spec["city"])
    return covered, problems


def check_weather_write(turns, spec, case):
    calls, _ = turns[-1]
    problems = []
    writes = [i for i, c in enumerate(calls) if c.tool in WRITE_TOOLS]
    if not writes:
        return False, ["weather_write: nothing written"]
    path = calls[writes[-1]].path
    back = [i for i in range(writes[-1] + 1, len(calls)) if calls[i].tool in READ_TOOLS and calls[i].path == path]
    if not back:
        return False, ["weather_write: no read-back of %s" % path]
    if back[0] < len(calls) - 1:
        problems.append("post_answer_calls: %s after the read-back"
                        % ", ".join(c.tool for c in calls[back[0] + 1:]))
    # The forecast has to come before the write it backs; writing a guess and
    # looking the weather up afterwards is not the M10b sequence.
    weather_at = [i for i, c in enumerate(calls[:writes[-1]]) if c.tool == "get_weather" and not c.error]
    if any(c.tool in ("web_search", "web_fetch") for c in calls[weather_at[0]:]) if weather_at else False:
        problems.append("weather_write: web search after the forecast")
    return bool(weather_at), problems


CHECKS = {
    "zero_call": check_zero_call,
    "bash_aggregate": check_bash_aggregate,
    "bash_avoided": check_bash_avoided,
    "cmd_missing": check_cmd_missing,
    "bash_edit": check_bash_edit,
    "cwd_reset": check_cwd_reset,
    "weather": check_weather,
    "weather_landmark": check_weather_landmark,
    "weather_write": check_weather_write,
}


def label(case_id, passed, steps_by_turn, dropped=None):
    spec = SPEC.get(case_id)
    case = find_case(case_id)
    if spec is None or case is None:
        return "unknown", ["no behavior spec" if spec is None else "case not found"]
    if not passed:
        return "fail", []
    if dropped:
        return "reject", ["unclean: %s (corpus paths drops the run)" % dropped]
    turns = [split_turn(committed(steps)[0]) for steps in steps_by_turn]
    problems = []
    for (calls, final), turn in zip(turns, case["turns"]):
        # Edit/write kinds judge their own stopping point (after verification).
        expect = {} if spec["kind"] in ("bash_edit", "weather_write") else turn["expect"]
        problems += common_problems(calls, final, expect, spec["kind"], spec.get("needs", ()))
    covered, own = CHECKS[spec["kind"]](turns, spec, case)
    problems += own
    if problems:
        return "reject", problems
    return ("covered" if covered else "ordinary"), []


def main():
    ap = argparse.ArgumentParser(description=__doc__.split("\n\n")[0])
    ap.add_argument("runs", nargs="+", help="agent-eval run directories (summary.json + trace.jsonl)")
    ap.add_argument("--report", help="write one TSV row per run and case")
    ap.add_argument("--json", help="write per-sub-class counts as JSON")
    args = ap.parse_args()
    rows = []
    for run_dir in args.runs:
        for case_id, passed, steps, dropped in load_runs(run_dir):
            verdict, problems = label(case_id, passed, steps, dropped)
            rows.append((os.path.basename(run_dir.rstrip("/")), case_id, verdict, "; ".join(problems)))
    for row in rows:
        print("%s\t%s\t%s\t%s" % row)
    by_sub = collections.defaultdict(collections.Counter)
    for _, case_id, verdict, _ in rows:
        by_sub[SPEC.get(case_id, {}).get("sub", "?")][verdict] += 1
    print("\nsub-class   passed  covered  ordinary  reject  fail")
    for sub in sorted(by_sub):
        c = by_sub[sub]
        print("%-10s  %6d  %7d  %8d  %6d  %4d" % (
            sub, c["covered"] + c["ordinary"] + c["reject"], c["covered"], c["ordinary"], c["reject"], c["fail"]))
    if args.report:
        with open(args.report, "w") as f:
            for row in rows:
                f.write("%s\t%s\t%s\t%s\n" % row)
    if args.json:
        with open(args.json, "w") as f:
            json.dump({sub: dict(c) for sub, c in sorted(by_sub.items())}, f, ensure_ascii=False, indent=2)
            f.write("\n")


if __name__ == "__main__":
    main()
