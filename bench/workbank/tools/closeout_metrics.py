#!/usr/bin/env python3
"""Closeout experiment metrics from agent-eval run artifacts.

Usage:
    uv run python tools/closeout_metrics.py RUNDIR [RUNDIR...] [--json OUT]

Each RUNDIR must contain run.json, summary.json and trace.jsonl.
With multiple run dirs, the first is treated as the baseline for flip lists.
"""

import argparse
import json
import re
import sys
from collections import Counter, defaultdict
from pathlib import Path

TOOL_CALL_RE = re.compile(r"<tool_call>.*?</tool_call>", re.DOTALL)


def load_json(path):
    with open(path, encoding="utf-8") as f:
        return json.load(f)


def load_jsonl(path):
    records = []
    with open(path, encoding="utf-8") as f:
        for line in f:
            line = line.strip()
            if line:
                records.append(json.loads(line))
    return records


def iter_steps(summary):
    for case in summary.get("cases", []):
        for turn in case.get("turns", []):
            result = turn.get("result") or {}
            for step in result.get("steps", []):
                yield case, turn, step


def case_tags(run, summary_case):
    tags = summary_case.get("tags")
    if tags:
        return tags
    for c in run.get("cases", []):
        if c.get("id") == summary_case.get("id"):
            return c.get("tags") or {}
    return {}


def strict_pass(run, summary):
    """Strict pass: normalized pass, except (a) expected_number cases are
    re-checked with a plain float() parse of the recorded answer, and
    (b) output_equals_any accepts only the first listed alternative."""
    expects = {}
    for c in run.get("cases", []):
        turns = c.get("turns") or []
        if turns:
            expects[c.get("id")] = turns[-1].get("expect") or {}

    strict_by_id = {}
    normalized_by_id = {}
    strict_fail_reasons = {}
    for case in summary.get("cases", []):
        cid = case.get("id")
        normalized = bool(case.get("passed"))
        normalized_by_id[cid] = normalized
        strict = normalized
        reason = None
        expect = expects.get(cid, {})
        turns = case.get("turns") or []
        result = (turns[-1].get("result") or {}) if turns else {}
        answer = result.get("original_output") or result.get("output") or ""
        if strict and "expected_number" in expect:
            try:
                want = float(expect["expected_number"])
            except (TypeError, ValueError):
                want = None
            tol = expect.get("tolerance") or 0
            try:
                got = float(answer.strip())
            except (TypeError, ValueError):
                got = None
            if want is None or got is None or abs(got - want) > tol:
                strict = False
                reason = "strict_number_parse"
        elif strict and "output_equals_any" in expect:
            alts = expect.get("output_equals_any") or []
            first = alts[0] if alts else None
            if first is None or answer.strip() != str(first).strip():
                strict = False
                reason = "strict_output_equals_first_only"
        strict_by_id[cid] = strict
        if reason:
            strict_fail_reasons[cid] = reason
    return normalized_by_id, strict_by_id, strict_fail_reasons


def answer_stage_completion(summary):
    hits = 0
    total = 0
    for _case, _turn, step in iter_steps(summary):
        if step.get("stage") == "answer":
            total += 1
            if step.get("action_type") in ("final", "no_tool"):
                hits += 1
    return hits, total


def repetition_stats(trace):
    total = 0
    last = 0
    earlier = 0
    plain = 0
    for rec in trace:
        if rec.get("kind") != "model_call":
            continue
        mc = rec.get("model_call") or {}
        if mc.get("stage") != "answer":
            continue
        total += 1
        text = ((mc.get("response") or {}).get("text") or "").strip()
        prompt = (mc.get("request") or {}).get("prompt") or ""
        if not text.startswith("<tool_call>"):
            plain += 1
            continue
        calls = [m.strip() for m in TOOL_CALL_RE.findall(prompt)]
        if calls and text == calls[-1]:
            last += 1
        elif any(text == c for c in calls[:-1]):
            earlier += 1
    return {"total": total, "last_call_repeat": last,
            "earlier_call_repeat": earlier, "plain_text": plain}


def rejected_kind(step):
    # harness v20 records tool_rejected_reason; v21 records tool_rejected
    return step.get("tool_rejected") or step.get("tool_rejected_reason")


def duplicate_rejects(summary):
    n = 0
    for _case, _turn, step in iter_steps(summary):
        if rejected_kind(step) == "duplicate_tool_call":
            n += 1
    return n


def max_turn_cases(run, summary):
    """Two counts: step-cap cases (last step number == harness.max_steps) and
    runner-error cases (any turn failed with a runner error)."""
    max_steps = (run.get("harness") or {}).get("max_steps")
    pattern = re.compile(r"max steps|step limit|runner error", re.IGNORECASE)
    step_cap = []
    runner_error = []
    for case in summary.get("cases", []):
        steps = [st.get("number") for _c, t, st in iter_steps({"cases": [case]})]
        last = max(steps) if steps else 0
        if max_steps is not None and last == max_steps:
            step_cap.append(case.get("id"))
        for turn in case.get("turns", []):
            failures = turn.get("failures") or []
            if turn.get("runner_error"):
                failures = failures + [turn["runner_error"]]
            if any(pattern.search(str(f)) for f in failures):
                runner_error.append(case.get("id"))
                break
    return {"step_cap": step_cap, "runner_error": runner_error}


def unclosed_think(summary):
    cases = []
    protocol_error_subcount = 0
    seen = set()
    for case, _turn, step in iter_steps(summary):
        if step.get("number") != 1:
            continue
        output = step.get("model_output") or ""
        if "<think>" in output and "</think>" not in output:
            cid = case.get("id")
            if cid not in seen:
                seen.add(cid)
                cases.append(cid)
                if "incomplete leading think" in (step.get("protocol_error") or ""):
                    protocol_error_subcount += 1
    return cases, protocol_error_subcount


def breakdowns(run, summary, normalized_by_id):
    def tally(keyfunc):
        counts = defaultdict(lambda: [0, 0])
        for case in summary.get("cases", []):
            for value in keyfunc(case):
                counts[value][1] += 1
                if normalized_by_id.get(case.get("id")):
                    counts[value][0] += 1
        return dict(sorted(counts.items()))

    by_level = tally(lambda c: [(case_tags(run, c).get("level") or "?")])
    by_scenario = tally(lambda c: [(case_tags(run, c).get("scenario") or "?")])
    by_axis = tally(lambda c: list(case_tags(run, c).get("axes") or []) or ["(none)"])
    return {"level": by_level, "scenario": by_scenario, "axes": by_axis}


def bfcl_split(summary, normalized_by_id):
    groups = {"irrelevance": [0, 0], "other": [0, 0]}
    for case in summary.get("cases", []):
        key = "irrelevance" if "irrelevance" in (case.get("id") or "") else "other"
        groups[key][1] += 1
        if normalized_by_id.get(case.get("id")):
            groups[key][0] += 1
    return groups


def native_consecutive_user(trace):
    dist = Counter()
    for rec in trace:
        if rec.get("kind") != "model_call":
            continue
        prompt = ((rec.get("model_call") or {}).get("request") or {}).get("prompt") or ""
        if not prompt.startswith('{"messages":'):
            continue
        try:
            messages = json.loads(prompt).get("messages") or []
        except json.JSONDecodeError:
            dist["unparseable"] += 1
            continue
        n = 0
        for msg in reversed(messages):
            if msg.get("role") == "user":
                n += 1
            else:
                break
        dist[n] += 1
    return dict(sorted(dist.items(), key=lambda kv: str(kv[0])))


def rate(part, whole):
    return (part / whole) if whole else 0.0


def analyze(run_dir):
    run_dir = Path(run_dir)
    run = load_json(run_dir / "run.json")
    summary = load_json(run_dir / "summary.json")
    trace = load_jsonl(run_dir / "trace.jsonl")

    model = run.get("model") or {}
    harness = run.get("harness") or {}
    metrics = summary.get("metrics") or {}
    channel = "native" if model.get("completion") == "chat-completions" else "text"
    suite = run.get("suite") or ""

    normalized_by_id, strict_by_id, strict_reasons = strict_pass(run, summary)
    strict_correct = sum(1 for v in strict_by_id.values() if v)
    task_success = metrics.get("task_success") or {}

    answer_hits, answer_total = answer_stage_completion(summary)
    rep = repetition_stats(trace)
    dup = duplicate_rejects(summary)
    max_turns = max_turn_cases(run, summary)
    think_cases, think_protocol = unclosed_think(summary)

    result = {
        "run_dir": str(run_dir),
        "run_name": run_dir.name,
        "run_id": summary.get("run_id") or run.get("run_id"),
        "suite": suite,
        "model_id": model.get("identifier"),
        "channel": channel,
        "wire_profile": harness.get("wire_profile"),
        "wire_hash": (harness.get("wire_hash") or "")[:12],
        "harness_version": harness.get("version"),
        "scorer_version": harness.get("scorer_version"),
        "case_parallelism": harness.get("case_parallelism"),
        "sampling": run.get("sampling"),
        "pass": {
            "strict": {"correct": strict_correct, "total": len(strict_by_id)},
            "normalized": {
                "correct": task_success.get("correct"),
                "total": task_success.get("total"),
                "rate": task_success.get("rate"),
            },
            "strict_fail_overrides": strict_reasons,
        },
        "answer_stage_text_completion": {
            "hits": answer_hits, "total": answer_total,
            "rate": rate(answer_hits, answer_total),
        },
        "answer_repetition": {
            **rep,
            "last_call_repeat_rate": rate(rep["last_call_repeat"], rep["total"]),
            "earlier_call_repeat_rate": rate(rep["earlier_call_repeat"], rep["total"]),
            "plain_text_rate": rate(rep["plain_text"], rep["total"]),
        },
        "duplicate_rejects": dup,
        "max_turn_cases": max_turns,
        "first_step_unclosed_think": {
            "cases": think_cases,
            "count": len(think_cases),
            "protocol_error_incomplete_leading_think": think_protocol,
        },
        "normalized_by_case": normalized_by_id,
        "strict_by_case": strict_by_id,
    }

    if suite == "workbank":
        result["breakdowns"] = breakdowns(run, summary, normalized_by_id)
    if "bfcl" in suite:
        result["bfcl_split"] = bfcl_split(summary, normalized_by_id)
    if channel == "native":
        result["native_consecutive_user"] = native_consecutive_user(trace)
    return result


def fmt_counts(counts):
    return ", ".join(f"{k}: {v[0]}/{v[1]}" for k, v in counts.items())


def print_report(r):
    print(f"=== {r['run_name']} ===")
    print(f"  run_id:          {r['run_id']}")
    print(f"  suite:           {r['suite']}")
    print(f"  model:           {r['model_id']}")
    print(f"  channel:         {r['channel']}")
    print(f"  wire_profile:    {r['wire_profile']}")
    print(f"  wire_hash:       {r['wire_hash']}")
    print(f"  harness:         {r['harness_version']} (scorer {r['scorer_version']})")
    print(f"  case_parallelism:{r['case_parallelism']:>2}")
    print(f"  sampling:        {json.dumps(r['sampling'], sort_keys=True)}")
    p = r["pass"]
    print(f"  pass: strict {p['strict']['correct']}/{p['strict']['total']}, "
          f"normalized {p['normalized']['correct']}/{p['normalized']['total']} "
          f"(rate {p['normalized']['rate']})")
    if p["strict_fail_overrides"]:
        print(f"    strict-only failures: {p['strict_fail_overrides']}")
    a = r["answer_stage_text_completion"]
    print(f"  answer-stage text completion: {a['hits']}/{a['total']} ({a['rate']:.3f})")
    rep = r["answer_repetition"]
    print(f"  answer repetition: {rep['total']} answer gens")
    print(f"    last-call repeat:    {rep['last_call_repeat']} ({rep['last_call_repeat_rate']:.3f})")
    print(f"    earlier-call repeat: {rep['earlier_call_repeat']} ({rep['earlier_call_repeat_rate']:.3f})")
    print(f"    plain text:          {rep['plain_text']} ({rep['plain_text_rate']:.3f})")
    print(f"  duplicate rejects: {r['duplicate_rejects']}")
    mt = r["max_turn_cases"]
    print(f"  step-cap cases ({len(mt['step_cap'])}): {', '.join(mt['step_cap']) or '-'}")
    print(f"  runner-error cases ({len(mt['runner_error'])}): {', '.join(mt['runner_error']) or '-'}")
    t = r["first_step_unclosed_think"]
    print(f"  first-step unclosed think: {t['count']} cases "
          f"(protocol_error 'incomplete leading think': {t['protocol_error_incomplete_leading_think']})")
    if t["cases"]:
        print(f"    {', '.join(t['cases'])}")
    if "breakdowns" in r:
        b = r["breakdowns"]
        print(f"  breakdown by level:    {fmt_counts(b['level'])}")
        print(f"  breakdown by scenario: {fmt_counts(b['scenario'])}")
        print(f"  breakdown by axis:     {fmt_counts(b['axes'])}")
    if "bfcl_split" in r:
        print(f"  bfcl split: {fmt_counts(r['bfcl_split'])}")
    if "native_consecutive_user" in r:
        print(f"  native consecutive trailing user msgs per gen: {r['native_consecutive_user']}")
    print()


def print_flips(baseline, other):
    print(f"=== flips: {baseline['run_name']} -> {other['run_name']} ===")
    base = baseline["normalized_by_case"]
    oth = other["normalized_by_case"]
    flips = []
    for cid in sorted(set(base) | set(oth)):
        if cid in base and cid in oth and base[cid] != oth[cid]:
            flips.append((cid, base[cid], oth[cid]))
    if not flips:
        print("  (no normalized pass flips on shared cases)")
    for cid, b, o in flips:
        b_s = "pass" if b else "fail"
        o_s = "pass" if o else "fail"
        print(f"  {cid}: {b_s} -> {o_s}  ({other['run_dir']}/trace.jsonl case_id={cid})")
    print()


def main(argv=None):
    ap = argparse.ArgumentParser(description="Closeout experiment metrics from agent-eval run artifacts.")
    ap.add_argument("rundirs", nargs="+", help="run directories containing run.json/summary.json/trace.jsonl")
    ap.add_argument("--json", dest="json_out", help="also dump machine-readable metrics to this file")
    args = ap.parse_args(argv)

    results = []
    for d in args.rundirs:
        r = analyze(d)
        results.append(r)
        print_report(r)

    if len(results) > 1:
        baseline = results[0]
        for other in results[1:]:
            print_flips(baseline, other)

    if args.json_out:
        out = [{k: v for k, v in r.items() if k not in ("normalized_by_case", "strict_by_case")}
               for r in results]
        with open(args.json_out, "w", encoding="utf-8") as f:
            json.dump(out, f, indent=2, sort_keys=True)
        print(f"wrote {args.json_out}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
