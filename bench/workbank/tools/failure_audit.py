#!/usr/bin/env python3
"""Mechanical failure observations; overlapping flags are not causal buckets."""
import argparse
from collections import Counter
import json
from pathlib import Path
import re

from wire_metrics import infrastructure_failure


def audit(run):
    summary = json.loads((Path(run) / "summary.json").read_text())
    rows, totals = [], Counter()
    for case in summary["cases"]:
        flags = set()
        traces = []
        for turn in case["turns"]:
            result = turn["result"]
            steps = result.get("steps", [])
            if result.get("forced_answer_reason"):
                flags.add(result["forced_answer_reason"])
            if not result.get("output"):
                flags.add("empty_output")
            if any(infrastructure_failure(f) for f in turn.get("failures", [])):
                flags.add("infrastructure_failure")
            if any(s.get("stage") == "answer" and s.get("action_type") == "tool" for s in steps):
                flags.add("answer_stage_tool")
            if any(s.get("tool") in ("read_file", "read_lines") and (s.get("tool_result") or {}).get("ok") for s in steps):
                flags.add("successful_file_read")
            for a, b in zip(steps, steps[1:]):
                receipt = a.get("tool_result")
                if not receipt:
                    continue
                payloads = []
                for text in re.findall(r"<tool_response>(.*?)</tool_response>", b["request"]["prompt"], re.S):
                    try:
                        payloads.append(json.loads(text))
                    except ValueError:
                        pass
                totals["receipts_checked"] += 1
                totals["receipts_present_in_next_prompt"] += receipt in payloads
            traces.append({
                "output": result.get("output"), "failures": turn.get("failures", []),
                "actions": [{"step":s["number"], "stage":s.get("stage"),
                    "action":s.get("action_type"), "tool":s.get("tool"),
                    "arguments":s.get("tool_arguments"), "tool_ok":(s.get("tool_result") or {}).get("ok"),
                    "tool_error":(s.get("tool_result") or {}).get("error"),
                    "protocol_error":s.get("protocol_error")} for s in steps],
            })
        for flag in flags:
            totals[flag] += 1
        totals["cases"] += 1
        totals["passed"] += bool(case["passed"])
        rows.append({"id":case["id"], "passed":case["passed"],
            "case_failures":case.get("failures", []), "case_error":case.get("error"),
            "flags":sorted(flags), "turns":traces})
    return {"run":run,"warning":"Flags overlap. Empty output is not proof that reasoning was absent.","totals":dict(totals),"cases":rows}


if __name__ == "__main__":
    ap = argparse.ArgumentParser(description=__doc__)
    ap.add_argument("run")
    args = ap.parse_args()
    print(json.dumps(audit(args.run), ensure_ascii=False, indent=2))
