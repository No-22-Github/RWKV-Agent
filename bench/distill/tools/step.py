#!/usr/bin/env python3
"""Drive one distill case through the real eval harness, one model output at a time.

The solver plays the student model: it only ever sees what the harness would
show the model (system block, tool receipts, reminders, next-turn prompts),
never case.json / NOTES.md / verify.py. Each call replays the whole script from
scratch through `rwkv-cli agent-eval --script` (no model, milliseconds), so
every tool receipt is a real execution and the saved outputs are a replay
script `corpus render` accepts unchanged.

  step.py show <case_dir>            print what the model sees now (full prompt on step 1)
  step.py add  <case_dir> <text>     append one output (tool call or final answer), then show
  step.py add  <case_dir> -          same, text read from stdin (use for multi-line answers)
  step.py undo <case_dir>            drop the last output (only before the case finishes)

State lives in local/runs/distill/b04/solve/<case_id>.json. When the case finishes the
file gets "status": "pass" | "fail" and further add/undo are refused: a failed
case goes to triage, it is not retried until it passes.
"""
import json
import os
import shutil
import subprocess
import sys
import tempfile

REPO = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "..", ".."))
CLI = os.path.join(REPO, "local", "bin", "rwkv-cli")
SOLVE_DIR = os.environ.get("STEP_SOLVE_DIR") or os.path.join(REPO, "local", "runs", "distill", "b04", "solve")
# Same arm as internal/lab/corpus/render.go benchFlags: the replay must see the
# exact wire the rows will be rendered under.
# STEP_TOOL_CATALOG=work-v2 solves v1.41 b12 cases (bash + get_weather offered).
TOOL_CATALOG = os.environ.get("STEP_TOOL_CATALOG", "work-v1")
BENCH_FLAGS = [
    "--tool-catalog", TOOL_CATALOG, "--file-tools", "lines",
    "--max-steps", "16", "--max-tokens", "4096", "--decision-max-tokens", "2048",
    "--profile", "g1k", "--strict-spec", "--trace-prompt-bytes", "-1",
]
PLACEHOLDER = "\x00step-placeholder\x00"


def die(msg):
    print("error: " + msg, file=sys.stderr)
    sys.exit(2)


def load_state(case_dir):
    case = json.load(open(os.path.join(case_dir, "case.json")))
    path = os.path.join(SOLVE_DIR, case["id"] + ".json")
    if os.path.exists(path):
        state = json.load(open(path))
    else:
        state = {"case_id": case["id"], "outputs": [], "status": "open"}
    return case, path, state


def save_state(path, state):
    os.makedirs(SOLVE_DIR, exist_ok=True)
    tmp = path + ".tmp"
    with open(tmp, "w") as f:
        json.dump(state, f, ensure_ascii=False, indent=1)
    os.replace(tmp, path)


def replay(case_dir, case, outputs):
    work = tempfile.mkdtemp(prefix="step-")
    try:
        scenario = os.path.basename(os.path.dirname(os.path.abspath(case_dir)))
        shutil.copytree(case_dir, os.path.join(work, "cases", scenario, case["id"]))
        texts = outputs or [PLACEHOLDER]
        with open(os.path.join(work, "script.jsonl"), "w") as f:
            f.write(json.dumps({"case_id": case["id"],
                                "outputs": [{"text": t, "supervised": True} for t in texts]},
                               ensure_ascii=False) + "\n")
        cmd = [CLI, "agent-eval", "--script", os.path.join(work, "script.jsonl"),
               "--cases", os.path.join(work, "cases"), "--include-draft",
               "--case-parallelism", "1", "--output", os.path.join(work, "run")] + BENCH_FLAGS
        proc = subprocess.run(cmd, cwd=REPO, capture_output=True, text=True)
        trace_path = os.path.join(work, "run", "trace.jsonl")
        if not os.path.exists(trace_path):
            die("agent-eval produced no trace:\n" + proc.stdout[-2000:] + proc.stderr[-2000:])
        prompts, exhausted, other_errors = [], False, []
        for line in open(trace_path):
            r = json.loads(line)
            if r["kind"] == "model_call":
                prompts.append(r["model_call"]["request"]["prompt"])
            elif r["kind"] == "runner_event":
                err = r["runner_event"].get("error", "")
                if "script exhausted" in err:
                    exhausted = True
                elif err:
                    other_errors.append(err)
        summary = json.load(open(os.path.join(work, "run", "summary.json")))
        passed = bool(summary["cases"] and summary["cases"][0]["passed"])
        return prompts, exhausted, passed, other_errors
    finally:
        shutil.rmtree(work, ignore_errors=True)


def show(case_dir):
    case, path, state = load_state(case_dir)
    outputs = state["outputs"]
    if state["status"] != "open":
        print("CASE FINISHED: " + state["status"].upper())
        return
    prompts, exhausted, passed, errors = replay(case_dir, case, outputs)
    if not outputs:
        print(prompts[0])
        print("\n[step 1 — write the model's next output with: step.py add <case_dir> '<text>']")
        return
    if exhausted:
        # The harness asked for one more generation: show what is new since the
        # last output (tool receipt + reminder, a retry notice, or the next turn).
        prev = outputs[-1]
        cur = prompts[-1]
        cut = cur.rfind(prev)
        print(cur[cut + len(prev):] if cut >= 0 else cur)
        for e in errors:
            print("[harness: " + e + "]")
        print("\n[step %d — write the model's next output]" % (len(outputs) + 1))
        return
    # The harness finished the case without asking for more. Only PASS/FAIL is
    # printed: failure details quote the expected answer, which the solver must
    # never see.
    state["status"] = "pass" if passed else "fail"
    save_state(path, state)
    print("CASE FINISHED: " + state["status"].upper())


def main():
    if len(sys.argv) < 3 or sys.argv[1] not in ("show", "add", "undo"):
        print(__doc__)
        sys.exit(2)
    action, case_dir = sys.argv[1], sys.argv[2]
    if not os.path.exists(os.path.join(case_dir, "case.json")):
        die("no case.json in " + case_dir)
    case, path, state = load_state(case_dir)
    if action in ("add", "undo") and state["status"] != "open":
        die("case already finished (%s); failed cases go to triage, not retry" % state["status"])
    if action == "add":
        if len(sys.argv) < 4:
            die("add needs the output text")
        text = sys.stdin.read() if sys.argv[3] == "-" else sys.argv[3]
        text = text.strip()
        if not text:
            die("empty output")
        state["outputs"].append(text)
        save_state(path, state)
    elif action == "undo":
        if not state["outputs"]:
            die("nothing to undo")
        state["outputs"].pop()
        save_state(path, state)
    show(case_dir)


if __name__ == "__main__":
    main()
