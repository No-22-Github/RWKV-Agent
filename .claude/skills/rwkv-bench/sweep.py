#!/usr/bin/env python3
"""sweep.py — run a grid of sampling arms x suites x replicas against an RWKV endpoint.

Implements docs/evaluations/benchmark-protocol.md: g1k wire, unified budget, endpoint
snapshots, validity gate per run, whole-run retry on infrastructure errors.

  sweep.py --out runs/bench-20260923 --arms greedy,t03-p10 --suites workbank,bfcl-product --k 0
  sweep.py ... --k 0-2          # replicas 0,1,2
  sweep.py ... --dry-run        # print the commands only

A run counts as done only when <run>/experiment.json exists with "gate_passed": true.
Anything else found at a run path (an interrupted or failed attempt) is moved to
<out>/aborted/ and the run starts over. Credentials come from RWKV_CF_ID / RWKV_CF_SECRET
and are passed to rwkv-cli by variable name only; they never reach a file.
Standard library only.
"""
import argparse
import hashlib
import importlib.util
import json
import os
import shutil
import subprocess
import sys
import time
import urllib.request
from pathlib import Path

SKILL_DIR = Path(__file__).resolve().parent
REPO = SKILL_DIR.parents[2] if (SKILL_DIR.parents[2] / "go.mod").exists() else Path.cwd()
BINARY = REPO / "bin" / "rwkv-cli"
CHECK_RUN = SKILL_DIR / "check_run.py"
sys.path.insert(0, str(REPO / "bench" / "workbank" / "tools"))
from wire_metrics import infrastructure_failure  # noqa: E402

_spec = importlib.util.spec_from_file_location("check_run", CHECK_RUN)
_check_run = importlib.util.module_from_spec(_spec)
_spec.loader.exec_module(_check_run)
ARMS = _check_run.ARMS

# name -> (short name for run dirs, rwkv-cli suite args, case count, parallelism, uses g1k wire)
SUITES = {
    "workbank": ("workbank", ["--cases", "bench/workbank/cases", "--tool-catalog", "work-v1",
                              "--file-tools", "lines", "--include-draft"], 148, 148, True),
    "bfcl-product": ("bfclp", ["--suite", "bfcl-product"], 60, 20, True),
    "boundary": ("boundary", ["--suite", "boundary"], 18, 18, True),
    "assistant": ("assistant", ["--suite", "assistant"], 6, 6, True),
    "smoke": ("smoke", ["--suite", "smoke"], 10, 10, True),
    "primitive-orig30": ("porig30", ["--suite", "primitive-orig30"], 30, 30, False),
    "primitive-feedback30": ("pfb30", ["--suite", "primitive-feedback30"], 30, 30, False),
}


def arm_flags(arm):
    s = ARMS[arm]
    return ["--temperature", str(s["temperature"]), "--top-k", str(s["top_k"]), "--top-p", str(s["top_p"]),
            "--presence-penalty", str(s["presence_penalty"]), "--frequency-penalty", str(s["frequency_penalty"]),
            "--penalty-decay", str(s["penalty_decay"])]


def endpoint_get(base, path):
    request = urllib.request.Request(base.rstrip("/") + path, headers={
        "CF-Access-Client-Id": os.environ["RWKV_CF_ID"],
        "CF-Access-Client-Secret": os.environ["RWKV_CF_SECRET"],
        # Cloudflare answers python-urllib's default User-Agent with a bare 403.
        "User-Agent": "curl/8.7.1",
    })
    with urllib.request.urlopen(request, timeout=30) as response:
        return json.loads(response.read())


def snapshot(args, label):
    models = endpoint_get(args.api_url, "/models")
    status = endpoint_get(args.api_url, "/server/status")
    (args.out / f"endpoint-{label}-models.json").write_text(json.dumps(models, indent=2) + "\n")
    (args.out / f"endpoint-{label}-server-status.json").write_text(json.dumps(status, indent=2) + "\n")
    ids = [m.get("id") for m in models.get("data", [])]
    queue = status.get("prefill_queue") or {}
    return ids, status.get("engine_version"), queue.get("hard_max_bsz")


def git(*argv):
    return subprocess.check_output(["git", *argv], cwd=REPO)


def case_source_sha256(root):
    digest = hashlib.sha256()
    for path in sorted(root.rglob("case.json")):
        digest.update(str(path.relative_to(root)).encode())
        digest.update(b"\0")
        digest.update(path.read_bytes())
    return digest.hexdigest()


def parse_k(value):
    if "-" in value:
        low, high = value.split("-", 1)
        return list(range(int(low), int(high) + 1))
    return [int(part) for part in value.split(",")]


def done(path):
    meta = path / "experiment.json"
    if not meta.is_file():
        return False
    try:
        return json.loads(meta.read_text()).get("gate_passed") is True
    except json.JSONDecodeError:
        return False


def set_aside(args, path):
    if not path.exists() and not Path(str(path) + ".log").exists():
        return
    aborted = args.out / "aborted"
    aborted.mkdir(exist_ok=True)
    stamp = time.strftime("%Y%m%d-%H%M%S")
    for source in (path, Path(str(path) + ".log")):
        if source.exists():
            shutil.move(str(source), str(aborted / f"{source.name}.{stamp}"))


def command(args, suite, arm, output):
    _, suite_args, _, parallelism, g1k = SUITES[suite]
    cmd = [str(BINARY), "agent-eval", "--completion", "rwkv-lightning-cuda", "--model", args.model,
           "--api-url", args.api_url,
           "--api-header-env", "CF-Access-Client-Id=RWKV_CF_ID",
           "--api-header-env", "CF-Access-Client-Secret=RWKV_CF_SECRET",
           "--max-steps", "16", "--max-tokens", "4096", "--case-parallelism", str(parallelism),
           # The CLI default is 2m; with ~150 cases sharing the backend a 16-step case needs far
           # longer, and the 2m clock cut 56/148 greedy cases on 2026-09-23. run.json does not
           # record this value, so it cannot be gated after the fact — keep it fixed here.
           "--case-timeout", "30m",
           # Without this the decision step falls back to the protocol default (512). g1k thinks
           # spontaneously on 142/148 first steps, so 512 cut half the think blocks and scored them
           # as protocol-invalid. 2048 lets a normal think close and still stops a repetition loop.
           "--decision-max-tokens", "2048",
           # Client-side coalescing hands every call its result only when the whole merged
           # response ends, so one looping member stalls the short replies batched with it
           # (2026-09-23: ~4 min per call, 25/148 cases to the 30m deadline). The CUDA server
           # batches concurrent requests itself; send one request per call.
           "--remote-batch-wait", "0s"]
    if g1k:
        cmd += ["--profile", "g1k", "--strict-spec"]
    return cmd + suite_args + arm_flags(arm) + ["--output", str(output)]


def finish(args, suite, arm, output, cmd, started, exit_code):
    """Gate one finished run. Returns (provenance or None, gate_ok, one-line report)."""
    _, _, count, _, g1k = SUITES[suite]
    summary_path = output / "summary.json"
    if not summary_path.is_file():
        return None, True, f"no summary.json (exit {exit_code}); see {output}.log"
    summary = json.loads(summary_path.read_text())
    errors = [f for c in summary["cases"] for t in c["turns"] for f in t.get("failures", [])
              if infrastructure_failure(f)]
    errors += [c.get("invalid_reason", "") for c in summary["cases"] if c.get("invalid")]
    gate_cmd = [sys.executable, str(CHECK_RUN), str(output), "--arm", arm, "--rwkv", "--cases", str(count)]
    if not g1k:
        gate_cmd.append("--primitive")
    gate = subprocess.run(gate_cmd, capture_output=True, text=True)
    task = summary["metrics"]["task_success"]
    strict_total = len(summary["cases"])
    provenance = {
        "command": cmd,
        "arm": arm, "suite": suite, "sampling": ARMS[arm],
        "binary_sha256": hashlib.sha256(BINARY.read_bytes()).hexdigest(),
        "git_head": git("rev-parse", "HEAD").decode().strip(),
        "diff_sha256": hashlib.sha256(git("diff", "HEAD")).hexdigest(),
        "state_id": "",
        "started_unix": started, "exit_code": exit_code, "elapsed_seconds": time.time() - started,
        "infrastructure_errors": errors,
        "valid_for_model_comparison": not errors,
        "gate_output": gate.stdout,
        "strict": {"correct": task["correct"], "total": strict_total},
    }
    if suite == "workbank":
        root = REPO / "bench" / "workbank" / "cases"
        provenance["case_source"] = str(root)
        provenance["case_source_sha256"] = case_source_sha256(root)
    line = (f"strict {task['correct']}/{strict_total}  invalid {summary['metrics'].get('invalid_cases', 0)}"
            f"  infra_errors {len(errors)}  gate {'PASS' if gate.returncode == 0 else 'FAIL'}"
            f"  {round(time.time() - started)}s")
    if gate.returncode != 0:
        line += "\n" + "\n".join(l for l in gate.stdout.splitlines() if l.startswith("FAIL"))
    return provenance, gate.returncode == 0, line


def run_arm(args, arm, k):
    """Run every suite for one arm/replica; suites run concurrently within the bsz budget."""
    pending = []
    for suite in args.suites:
        output = args.out / f"{args.prefix}-{SUITES[suite][0]}-{arm}-k{k}"
        if done(output):
            print(f"SKIP {output.name} (done)", flush=True)
            continue
        pending.append((suite, output))
    for attempt in range(1, args.max_attempts + 1):
        if not pending:
            return True
        batches, current, used = [], [], 0
        for suite, output in pending:
            need = SUITES[suite][3]
            if current and used + need > args.bsz:
                batches.append(current)
                current, used = [], 0
            current.append((suite, output))
            used += need
        if current:
            batches.append(current)
        retry = []
        for batch in batches:
            procs = []
            for suite, output in batch:
                set_aside(args, output)
                cmd = command(args, suite, arm, output)
                print(f"START {output.name} attempt {attempt}  {time.strftime('%H:%M:%S')}", flush=True)
                log = open(str(output) + ".log", "w")
                procs.append((suite, output, cmd, time.time(), subprocess.Popen(
                    cmd, cwd=REPO, stdout=log, stderr=subprocess.STDOUT), log))
            for suite, output, cmd, started, proc, log in procs:
                code = proc.wait()
                log.close()
                provenance, gate_ok, line = finish(args, suite, arm, output, cmd, started, code)
                if not gate_ok:
                    # The run was configured wrongly; repeating it cannot help.
                    sys.exit(f"GATE FAIL {output.name}  {line}\nfix the configuration; nothing marked done")
                errors = provenance["infrastructure_errors"] if provenance else ["no summary"]
                final = attempt == args.max_attempts
                if provenance and (not errors or final):
                    # Last attempt: keep the run and count its invalid cases as failures
                    # (protocol §6) instead of retrying forever on a reproducible break.
                    provenance["gate_passed"] = True
                    provenance["accepted_with_infra_errors"] = bool(errors)
                    (output / "experiment.json").write_text(
                        json.dumps(provenance, indent=2, ensure_ascii=False) + "\n")
                    tag = "DONE" if not errors else "KEEP"
                else:
                    retry.append((suite, output))
                    tag = "RETRY"
                print(f"{tag} {output.name}  {line}", flush=True)
        pending = retry
    for _, output in pending:
        print(f"GIVE-UP {output.name}: no summary after {args.max_attempts} attempts", flush=True)
    return not pending


def main():
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("--out", required=True, type=Path)
    ap.add_argument("--arms", required=True, help="comma-separated arm names: " + ", ".join(sorted(ARMS)))
    ap.add_argument("--suites", default="workbank,bfcl-product", help="comma-separated: " + ", ".join(SUITES))
    ap.add_argument("--k", default="0", help="replica indices: 0 | 0-2 | 1,2")
    ap.add_argument("--model", default="rwkv-g1k-7b-temp-3601")
    ap.add_argument("--api-url", default="https://api-7b.rwkvos.com/v1")
    ap.add_argument("--prefix", default="g1k", help="run directory prefix")
    ap.add_argument("--max-attempts", type=int, default=2, help="whole-run attempts on infra errors; the last attempt is kept")
    ap.add_argument("--dry-run", action="store_true")
    args = ap.parse_args()
    args.arms = args.arms.split(",")
    args.suites = args.suites.split(",")
    bad = [a for a in args.arms if a not in ARMS] + [s for s in args.suites if s not in SUITES]
    if bad:
        sys.exit(f"unknown arm/suite: {bad}")
    replicas = parse_k(args.k)
    if args.dry_run:
        for k in replicas:
            for arm in args.arms:
                for suite in args.suites:
                    output = args.out / f"{args.prefix}-{SUITES[suite][0]}-{arm}-k{k}"
                    print(("DONE  " if done(output) else "TODO  ") + " ".join(command(args, suite, arm, output)))
        return 0
    if not (os.environ.get("RWKV_CF_ID") and os.environ.get("RWKV_CF_SECRET")):
        sys.exit("RWKV_CF_ID and RWKV_CF_SECRET must be set")
    if not BINARY.is_file():
        sys.exit(f"missing {BINARY}; run: go build -o bin/rwkv-cli ./cmd/rwkv-cli")
    args.out.mkdir(parents=True, exist_ok=True)
    label = time.strftime("%Y%m%d-%H%M%S")
    ids, engine, bsz = snapshot(args, "before-" + label)
    print(f"ENDPOINT {ids} {engine} hard_max_bsz={bsz}", flush=True)
    if args.model not in ids:
        sys.exit(f"endpoint serves {ids}, not {args.model}")
    args.bsz = bsz or 148
    ok = True
    for k in replicas:
        for arm in args.arms:
            current = [m.get("id") for m in endpoint_get(args.api_url, "/models").get("data", [])]
            if current != ids:
                sys.exit(f"endpoint model changed {ids} -> {current}; stopping, this stage is void")
            ok = run_arm(args, arm, k) and ok
    after, _, _ = snapshot(args, "after-" + label)
    if after != ids:
        print(f"ENDPOINT CHANGED {ids} -> {after}: runs from this invocation are void", flush=True)
        return 1
    print("ALL DONE" if ok else "FINISHED WITH GIVE-UPS", flush=True)
    return 0 if ok else 1


if __name__ == "__main__":
    sys.exit(main())
