#!/usr/bin/env python3
"""Replay a saved text request without executing generated tools.

Records every HTTP attempt and exact prompt/sampling hashes. Credentials stay
outside the artifact. This probes transport/generation, not task success.
"""
import argparse
import hashlib
import json
from pathlib import Path
import time
import urllib.error
import urllib.request


def main():
    ap = argparse.ArgumentParser(description=__doc__)
    ap.add_argument("run")
    ap.add_argument("case")
    ap.add_argument("output")
    ap.add_argument("--step", type=int, default=1)
    ap.add_argument("--turn", type=int, default=1)
    ap.add_argument("--repeat", type=int, default=3)
    ap.add_argument("--max-tokens", type=int)
    ap.add_argument("--credentials", required=True)
    args = ap.parse_args()
    dest = Path(args.output)
    if dest.exists():
        raise SystemExit("Refusing to overwrite " + str(dest))
    run = Path(args.run)
    summary = json.loads((run / "summary.json").read_text())
    manifest = json.loads((run / "run.json").read_text())
    case = next(c for c in summary["cases"] if c["id"] == args.case)
    step = next(s for s in case["turns"][args.turn - 1]["result"]["steps"] if s["number"] == args.step)
    req = step["request"]
    sampling = manifest["sampling"]
    body = {
        "model":manifest["model"]["identifier"], "contents":[req["prompt"]],
        "max_tokens":args.max_tokens or req["max_output_tokens"],
        "temperature":sampling["temperature"], "top_k":sampling["top_k"], "top_p":sampling["top_p"],
        "alpha_presence":sampling["presence_penalty"], "alpha_frequency":sampling["frequency_penalty"],
        "alpha_decay":sampling["penalty_decay"], "stop_tokens":[0], "stream":False, "chunk_size":1,
    }
    credentials = json.loads(Path(args.credentials).read_text())
    headers = {"CF-Access-Client-Id":credentials["WIRE_CF_ID"],
        "CF-Access-Client-Secret":credentials["WIRE_CF_SECRET"], "User-Agent":"curl/8.7.1", "Content-Type":"application/json"}
    encoded = json.dumps(body, ensure_ascii=False).encode()
    report = {"diagnostic_only":True, "source_run":str(run), "case":args.case,
        "turn":args.turn,"step":args.step, "request":body,
        "body_sha256":hashlib.sha256(encoded).hexdigest(), "original_output":step["model_output"],
        "note":"Buffered raw response; no client text-stop truncation, no parser, no tool execution. HTTP failures are recorded, never silently retried.", "attempts":[]}
    for repeat in range(args.repeat):
        started = time.time()
        attempt = {"repeat":repeat + 1, "started_unix":started}
        request = urllib.request.Request("https://api-7b.rwkvos.com/v1/batch/completions", data=encoded, headers=headers)
        try:
            with urllib.request.urlopen(request, timeout=180) as response:
                data = json.load(response)
                attempt.update(http_status=response.status, response=data)
        except urllib.error.HTTPError as error:
            attempt.update(http_status=error.code, error="HTTP failure")
        except Exception as error:
            attempt.update(error=type(error).__name__ + ": " + str(error))
        attempt["elapsed_seconds"] = time.time() - started
        report["attempts"].append(attempt)
        dest.write_text(json.dumps(report, ensure_ascii=False, indent=2) + "\n")
        print("attempt",repeat+1,"http",attempt.get("http_status"),"seconds",round(attempt["elapsed_seconds"]),flush=True)


if __name__ == "__main__":
    main()
