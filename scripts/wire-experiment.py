#!/usr/bin/env python3
"""Sequential online wire trials. Credentials come only from env or a private file.

CLI exit 1 means failed cases, not necessarily infrastructure failure. Each run
keeps the CLI's official scoring, plus explicit command/build/config provenance.
No server state, training, product defaults or case expectations are changed.
"""
import argparse
from collections import Counter
import hashlib
import json
import os
from pathlib import Path
import subprocess
import sys
import time

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "bench/workbank/tools"))
from wire_metrics import infrastructure_failure

PROFILE = "xml-v1+align-qwen36+no-tool+bare+one-stage"
SUITES = {"workbank": ["--cases", "bench/workbank/cases", "--tool-catalog", "work-v1", "--file-tools", "lines"], "boundary": ["--suite", "boundary"], "bfcl": ["--suite", "bfcl-product"]}


def main():
    ap = argparse.ArgumentParser(description=__doc__)
    ap.add_argument("name")
    ap.add_argument("--wire", default="")
    ap.add_argument("--profile", default=PROFILE)
    ap.add_argument("--state-id", default="", help="uploaded state ID; empty uses zero state")
    ap.add_argument("--suites", default="workbank,boundary,bfcl")
    ap.add_argument("--credentials", help="private JSON mapping of env names to secrets (never copied to outputs)")
    ap.add_argument("--root", default="runs/wire-check-20260918")
    ap.add_argument("--binary", default="build/rwkv-cli-wire-experiment")
    ap.add_argument("--buffered", action="store_true", help="request buffered HTTP responses instead of SSE")
    ap.add_argument("--parallelism", type=int, default=40)
    ap.add_argument("--cases", help="diagnostic custom case directory; workbank suite only")
    ap.add_argument("--stop-mode", default="eos", help="CUDA requires integer stop IDs; eos sends [0], text is for Python servers")
    ap.add_argument("--decision-max-tokens", type=int, default=0)
    ap.add_argument("--max-tokens", type=int, default=1024, help="global generation ceiling; also caps decision-max-tokens")
    args = ap.parse_args()
    env = os.environ.copy()
    if args.credentials:
        env.update(json.loads(Path(args.credentials).read_text()))
    env["WIRE_UA"] = "curl/8.7.1"
    base = [str(Path(args.binary).resolve()), "agent-eval", "--completion", "rwkv-lightning-cuda", "--api-url", "https://api-7b.rwkvos.com/v1", "--api-header-env", "CF-Access-Client-Id=WIRE_CF_ID", "--api-header-env", "CF-Access-Client-Secret=WIRE_CF_SECRET", "--api-header-env", "User-Agent=WIRE_UA", "--model", "rwkv-g1k-7b-temp-3601", "--profile", PROFILE, "--temperature", "1", "--top-k", "1", "--max-steps", "10", "--case-parallelism", str(args.parallelism), "--case-timeout", "30m", "--duplicate-rescue-threshold", "0", "--same-tool-rescue-limit", "0"]
    base[base.index("--profile") + 1] = args.profile
    if args.state_id:
        base += ["--state-id", args.state_id]
    if args.wire:
        base += ["--wire", args.wire]
    base += ["--api-stop-tokens", args.stop_mode]
    base += ["--max-tokens", str(args.max_tokens)]
    if args.decision_max_tokens:
        base += ["--decision-max-tokens", str(args.decision_max_tokens)]
    if args.buffered:
        base += ["--api-stream=false"]
    root = Path(args.root)
    root.mkdir(parents=True, exist_ok=True)
    for suite in args.suites.split(","):
        name = args.name + "-" + suite
        output = root / name
        if output.exists():
            raise SystemExit(f"Refusing to overwrite {output}")
        suite_args = SUITES[suite].copy()
        if args.cases:
            if suite != "workbank":
                raise SystemExit("--cases requires --suites workbank")
            suite_args[1] = args.cases
        cmd = base + suite_args + ["--output", str(output)]
        print("START", name, time.strftime("%Y-%m-%d %H:%M:%S"), flush=True)
        started = time.time()
        provenance = {"command":cmd, "binary_sha256":hashlib.sha256(Path(args.binary).read_bytes()).hexdigest(), "git_head":subprocess.check_output(["git","rev-parse","HEAD"],text=True).strip(), "diff_sha256":hashlib.sha256(subprocess.check_output(["git","diff","HEAD"])).hexdigest(), "started_unix":started}
        provenance["evaluation_scope"] = "modified_evidence_diagnostic" if args.cases else "original_suite"
        provenance["state_id"] = args.state_id
        if suite == "workbank":
            case_root = Path(args.cases or "bench/workbank/cases")
            digest = hashlib.sha256()
            for case_path in sorted(case_root.rglob("case.json")):
                digest.update(str(case_path.relative_to(case_root)).encode())
                digest.update(b"\0")
                digest.update(case_path.read_bytes())
            provenance["case_source"] = str(case_root.resolve())
            provenance["case_source_sha256"] = digest.hexdigest()
        with (root / (name + ".log")).open("w") as log:
            process = subprocess.run(cmd, env=env, stdout=log, stderr=subprocess.STDOUT)
        provenance.update(exit_code=process.returncode, elapsed_seconds=time.time()-started)
        path = output / "summary.json"
        if not path.exists():
            print((root / (name + ".log")).read_text()[-2000:], flush=True)
            raise SystemExit("No summary; stopping matrix")
        summary = json.loads(path.read_text())
        budgets = Counter(
            str(st.get("request", {}).get("max_output_tokens", 0))
            for c in summary["cases"] for t in c["turns"]
            for st in t["result"].get("steps", [])
        )
        provenance["actual_request_token_budgets"] = dict(budgets)
        errors = [f for c in summary["cases"] for t in c["turns"] for f in t.get("failures",[]) if infrastructure_failure(f)]
        provenance["valid_for_model_comparison"] = not errors
        provenance["infrastructure_errors"] = errors
        (output / "experiment.json").write_text(json.dumps(provenance, indent=2)+"\n")
        print("DONE", name, summary["metrics"]["task_success"], "seconds", round(provenance["elapsed_seconds"]), "infra_errors", len(errors), flush=True)
        if errors:
            raise SystemExit("Infrastructure error: run excluded, matrix stopped")


if __name__ == "__main__":
    main()
