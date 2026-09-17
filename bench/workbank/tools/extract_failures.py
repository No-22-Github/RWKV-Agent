#!/usr/bin/env python3
"""Extract failed agent-eval trajectories into a reviewable bundle.

For every failed case, walk the steps in order and find the FIRST step where
something observable went wrong. Categories are defined only by facts recorded
in summary.json (raw model output, parser verdict, harness verdict, tool
result) - never by guessing intent.

Usage:
  python3 extract_failures.py runs/workbank/closeout-v0-g1k --out bundle-v0-g1k \
      [--contrast runs/workbank/closeout-v0-deepseek] [--cases cases_dir]
"""
import argparse
import collections
import json
import pathlib
import re

CATEGORY_ORDER = [
    "A1_think_unclosed",   # output opens <think> without </think>
    "A2_protocol_error",   # parser/protocol rejected the output
    "A3_answer_stage_call",  # tool call emitted after tools were closed
    "B1_abs_path",         # call rejected: absolute path
    "B2_bad_args",         # call rejected: other argument validation
    "B3_unknown_tool",     # call rejected: tool not in catalog
    "B4_duplicate",        # call rejected: duplicate
    "C1_tool_error",       # call executed, tool returned an error (e.g. not found)
    "D1_empty_final",      # run ended, final output empty
    "D2_wrong_final",      # run ended with an answer, scorer failed it
]


# Text the harness substitutes when the model's final output broke the protocol.
HARNESS_FALLBACK = "I could not provide a reliable answer because the model output violated"


def load_json_lines(path):
    with open(path) as handle:
        return [json.loads(line) for line in handle if line.strip()]


def as_dict(value):
    if isinstance(value, dict):
        return value
    if isinstance(value, str):
        try:
            return json.loads(value)
        except json.JSONDecodeError:
            return {}
    return {}


def classify_step(step):
    output = str(step.get("model_output") or "")
    stripped = output.lstrip()
    stage = step.get("stage")
    tool_error = str(step.get("tool_error") or "")
    rejected = str(step.get("tool_rejected_reason") or "")
    # harness v21: step.tool_error is gone; failed/rejected calls are recorded
    # as tool_result = {"ok": false, "tool": ..., "error": ...}
    tool_result_obj = step.get("tool_result")
    if not tool_error and isinstance(tool_result_obj, dict) and tool_result_obj.get("ok") is False:
        tool_error = str(tool_result_obj.get("error") or "")
    think_unclosed = stripped.startswith("<think>") and "</think>" not in output
    if think_unclosed and (step.get("protocol_error") or not step.get("action_type")):
        return "A1_think_unclosed"
    # harness v21: no protocol_error field; an unparsed call envelope is itself
    # the protocol failure, and answer-stage parsed calls are stage violations
    if not step.get("action_type") and '"name"' in output:
        return "A2_protocol_error"
    if stage == "answer" and step.get("action_type") == "tool":
        return "A3_answer_stage_call"
    if stage == "answer" and step.get("action_type") == "no_tool":
        return None  # sanctioned semantic exit; wrong content surfaces as D2
    if step.get("protocol_error") or step.get("protocol_failure"):
        if stage == "answer" and "<tool_call>" in output:
            return "A3_answer_stage_call"
        return "A2_protocol_error"
    if step.get("stage_violation") or (stage == "answer" and "<tool_call>" in output):
        return "A3_answer_stage_call"
    if rejected == "duplicate_tool_call" or "duplicate tool call" in tool_error:
        return "B4_duplicate"
    if "absolute path" in tool_error:
        return "B1_abs_path"
    if tool_error.startswith("invalid tool arguments"):
        return "B2_bad_args"
    if "unknown tool" in tool_error or rejected == "unknown_tool":
        return "B3_unknown_tool"
    if tool_error:
        return "C1_tool_error"
    return None


def new_prompt_bytes(previous, current):
    if previous and current.startswith(previous):
        return current[len(previous):]
    if previous:
        return "[[PROMPT NOT A PREFIX EXTENSION - showing tail]]\n" + current[-3000:]
    return current


def step_outline(steps):
    parts = []
    for step in steps:
        label = step.get("tool") or step.get("action_type") or "?"
        verdict = classify_step(step)
        parts.append(f"{step.get('number')}:{step.get('stage','?')[0]}:{label}" + (f"[{verdict}]" if verdict else ""))
    return " → ".join(parts)


def load_run(run_dir):
    summary = json.load(open(run_dir / "summary.json"))
    return {case["id"]: case for case in summary["cases"]}


def load_expectations(cases_dir):
    expectations = {}
    if not cases_dir:
        return expectations
    for path in pathlib.Path(cases_dir).glob("*/*/case.json"):
        case = json.load(open(path))
        expectations[case["id"]] = {
            "expect": [turn.get("expect") for turn in case.get("turns", [])],
            "decoys": (case.get("tags") or {}).get("trap_decoys"),
            "ref_calls": (case.get("tags") or {}).get("ref_calls"),
        }
    return expectations


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("run_dir", type=pathlib.Path)
    parser.add_argument("--out", type=pathlib.Path, required=True)
    parser.add_argument("--contrast", type=pathlib.Path)
    parser.add_argument("--cases", default="bench/workbank/cases")
    parser.add_argument("--include-passed", action="store_true")
    args = parser.parse_args()

    run = load_run(args.run_dir)
    contrast = load_run(args.contrast) if args.contrast else {}
    expectations = load_expectations(args.cases if pathlib.Path(args.cases).exists() else None)
    (args.out / "cases").mkdir(parents=True, exist_ok=True)

    table = []
    first_counts = collections.Counter()
    all_counts = collections.Counter()
    for case_id, case in sorted(run.items()):
        passed = str(case.get("passed")) == "True"
        if passed and not args.include_passed:
            continue
        tags = as_dict(case.get("tags"))
        first = None
        per_case = collections.Counter()
        lines = [f"# {case_id} ({tags.get('level')}, {tags.get('scenario')}) passed={passed}", ""]
        exp = expectations.get(case_id, {})
        if exp:
            lines += [f"- expect: `{json.dumps(exp.get('expect'), ensure_ascii=False)}`",
                      f"- trap_decoys: `{json.dumps(exp.get('decoys'), ensure_ascii=False)}`",
                      f"- ref_calls: {exp.get('ref_calls')}"]
        if case_id in contrast:
            other = contrast[case_id]
            other_steps = [s for t in other["turns"] for s in t["result"].get("steps", [])]
            lines.append(f"- contrast ({args.contrast.name}) passed={other.get('passed')}: {step_outline(other_steps)}")
        lines.append("")
        for turn in case["turns"]:
            result = turn["result"]
            steps = result.get("steps", [])
            lines += [f"## turn {turn.get('number')}",
                      f"- user prompt: {turn.get('prompt')}",
                      f"- outline: {step_outline(steps)}",
                      f"- runner_error: {turn.get('runner_error')}",
                      f"- turn_outcome: {turn.get('outcome')} · forced_answer_reason: {result.get('forced_answer_reason')}",
                      f"- final output: `{result.get('output')}`",
                      f"- failures: {turn.get('failures')}", ""]
            previous_prompt = ""
            for step in steps:
                verdict = classify_step(step)
                if verdict:
                    per_case[verdict] += 1
                    all_counts[verdict] += 1
                    if first is None:
                        first = (verdict, turn.get("number"), step.get("number"))
                request = as_dict(step.get("request")) if not isinstance(step.get("request"), dict) else step["request"]
                prompt = str(request.get("prompt") or "")
                delta = new_prompt_bytes(previous_prompt, prompt)
                if not previous_prompt:
                    marker = delta.rfind("\nUser:")
                    delta = ("[[system block omitted]]\n" + delta[marker:]) if marker > 0 else delta
                previous_prompt = prompt
                lines += [f"### step {step.get('number')} · stage={step.get('stage')} · verdict={verdict or '-'}",
                          f"max_output={request.get('max_output_tokens')} stops={request.get('stops')} finish={step.get('finish_reason')}",
                          "", "NEW PROMPT BYTES:", "```", delta[-4000:], "```",
                          "RAW OUTPUT:", "```", str(step.get("model_output")), "```",
                          f"- parsed: action_type={step.get('action_type')} tool={step.get('tool')} args={json.dumps(step.get('tool_arguments'), ensure_ascii=False)}",
                          f"- channel={step.get('channel')} executed={step.get('tool_executed')} protocol_error={step.get('protocol_error')} stage_violation={step.get('stage_violation')} rejected={step.get('tool_rejected_reason')}",
                          f"- tool_result: `{str(step.get('tool_result'))[:1200]}`", ""]
        if first is None:
            output = str(case["turns"][-1]["result"].get("output") or "")
            if HARNESS_FALLBACK in output:
                verdict = "A2_protocol_error"
            elif not output.strip():
                verdict = "D1_empty_final"
            else:
                verdict = "D2_wrong_final"
            first = (verdict, case["turns"][-1].get("number"), None)
            per_case[first[0]] += 1
            all_counts[first[0]] += 1
        first_counts[first[0]] += 1
        last_output = str(case["turns"][-1]["result"].get("output") or "")[:80].replace("|", "/").replace("\n", " ")
        table.append((case_id, tags.get("level"), first[0], f"t{first[1]}s{first[2]}", dict(per_case), last_output))
        (args.out / "cases" / f"{case_id}.md").write_text("\n".join(lines))

    report = [f"# failure bundle: {args.run_dir.name}", "",
              "## first-divergence category (one per failed case)", ""]
    for name in CATEGORY_ORDER:
        if first_counts[name]:
            report.append(f"- {name}: {first_counts[name]}")
    report += ["", "## all flagged steps (can be several per case)", ""]
    for name in CATEGORY_ORDER:
        if all_counts[name]:
            report.append(f"- {name}: {all_counts[name]}")
    report += ["", "| case | level | first | at | all flags | final output |", "|---|---|---|---|---|---|"]
    for row in table:
        report.append(f"| {row[0]} | {row[1]} | {row[2]} | {row[3]} | {row[4]} | `{row[5]}` |")
    (args.out / "SUMMARY.md").write_text("\n".join(report) + "\n")
    print("\n".join(report[:30]))


if __name__ == "__main__":
    main()
