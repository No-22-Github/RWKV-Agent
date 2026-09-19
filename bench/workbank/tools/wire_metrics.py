#!/usr/bin/env python3
"""Read-only wire audit. Official case passes are never replaced by text heuristics.

Shape metrics use generation denominators, termination uses turns, pass uses cases.
The optional answer-text match is diagnostic only (it does not rescore a case).
"""
import argparse
from collections import Counter
import json
from pathlib import Path
import re
import statistics

VERSION = "wire-audit-v2"


def infrastructure_failure(failure):
    """Transport/provider failures are not a model or protocol score."""
    if not failure.startswith("runner error:"):
        return False
    text = failure.lower()
    if "agent protocol error:" in text:
        return False
    return any(s in text for s in (
        "rwkv_lightning continuation error:", "http 4", "http 5",
        "connection refused", "context deadline exceeded", "no such host",
        "timeout", "connection reset", "unexpected eof", "broken pipe",
    ))


def split_think(raw, prompt=""):
    text = (raw or "").strip()
    opening = prompt.rsplit("Assistant:", 1)[-1].strip() if "Assistant:" in prompt else ""
    if not text.startswith("<think>") and opening == "<think></think":
        if text.startswith(">"):
            return "empty", "", text[1:].strip()
        return "unclosed", text, ""
    if not text.startswith("<think>") and opening == "<think></think>":
        return "empty", "", text
    prefilled = opening.startswith("<think") and "</think>" not in opening
    if text.startswith("<think>"):
        text = text[len("<think>"):]
        source = "self"
    elif prefilled:
        if opening == "<think" and text.startswith(">"):
            text = text[1:]
        source = "prefilled"
    else:
        return "none", "", text
    if "</think>" not in text:
        return "unclosed", text, ""
    thought, body = text.split("</think>", 1)
    return source if thought.strip() else "empty", thought.strip(), body.strip()


def call_object(text):
    """Recognize one complete JSON call; a missing stop-consumed close is allowed.

    This is an audit recognizer, not a tool execution parser. Tags in prose or
    quoted JSON examples do not establish that a call was intended/executable.
    """
    text = text.strip()
    if text.startswith("<tool_call>"):
        text = text[len("<tool_call>"):]
    elif text.startswith("```json"):
        text = text[len("```json"):]
    elif not text.startswith("{"):
        return None
    try:
        obj, end = json.JSONDecoder().raw_decode(text.lstrip())
    except (ValueError, TypeError):
        return None
    tail = text.lstrip()[end:].strip()
    if tail not in ("", "</tool_call>", "```"):
        return None
    if not isinstance(obj, dict) or set(obj) != {"name", "arguments"}:
        return None
    if not isinstance(obj["name"], str) or not isinstance(obj["arguments"], dict):
        return None
    return obj


def answer_text_match(expect, output):
    """Possible content match, NOT evidence of an otherwise-correct answer."""
    if "expected_number" in expect:
        nums = re.findall(r"(?<![\w.])-?\d[\d,]*(?:\.\d+)?(?:[eE][+-]?\d+)?(?!\w|\.\d)", output)
        return any(abs(float(n.replace(",", "")) - expect["expected_number"]) <= expect.get("tolerance", .01) for n in nums)
    values = expect.get("output_equals_any", [expect.get("output_equals")])
    return any(isinstance(v, str) and re.search(r"(?<!\w)" + re.escape(v) + r"(?!\w)", output, re.I) for v in values)


def analyze(run, bank=None):
    run = Path(run)
    summary = json.loads((run / "summary.json").read_text())
    manifest = json.loads((run / "run.json").read_text()) if (run / "run.json").exists() else {}
    m, reasons, repairs = Counter(), Counter(), Counter()
    details, lengths, thought_lengths = [], [], []
    terminal = dict(part.split("=", 1) for part in manifest.get("harness", {}).get("wire_canonical", "").split(";") if "=" in part).get("terminal", "none")
    for case in summary["cases"]:
        m["cases"] += 1
        m["passed"] += bool(case.get("passed"))
        if "irrelevance" in case["id"]:
            m["irrelevance_cases"] += 1
            m["irrelevance_passed"] += bool(case.get("passed"))
        for ti, turn in enumerate(case.get("turns", [])):
            m["turns"] += 1
            result = turn["result"]
            steps = result.get("steps", [])
            failures = turn.get("failures", [])
            infra = any(infrastructure_failure(f) for f in failures)
            m["infra_error_turns"] += infra
            forced = result.get("forced_answer_reason", "")
            answer_steps = [st for st in steps if st.get("stage") == "answer"]
            if forced:
                reasons[forced] += 1
            m["forced_triggered"] += bool(forced)
            m["answer_turns"] += bool(answer_steps)
            m["forced_without_answer"] += bool(forced) and not answer_steps
            decisions = [st for st in steps if st.get("stage") != "answer"]
            real = [st for st in decisions if st.get("action_type") == "tool" and not (st.get("tool") == terminal and terminal != "none")]
            executed = [st for st in real if st.get("tool_executed")]
            evidence = any(st.get("tool_evidence") for st in real)
            m["tool_attempt_turns"] += bool(real)
            m["tool_executed_turns"] += bool(executed)
            last = steps[-1] if steps else {}
            terminal_ok = terminal != "none" and last.get("tool") == terminal and last.get("tool_executed") and not last.get("tool_error")
            clean_exit = bool(result.get("output")) and not last.get("stage_violation") and not last.get("protocol_error") and (last.get("action_type") in ("final", "no_tool") or terminal_ok)
            autonomous = bool(clean_exit and not forced and not answer_steps and not any(f.startswith("runner error:") for f in failures))
            m["self_term_tool_attempts"] += bool(real) and autonomous
            m["self_term_tool_executed"] += bool(executed) and autonomous
            ref = (case.get("tags") or {}).get("ref_calls")
            if ref is not None and ref > 0:
                m["needs_tool_turns"] += 1
                m["zero_evidence_exit"] += autonomous and not evidence
            previous_raw, previous_call = None, None
            for di, st in enumerate(decisions):
                raw = st.get("model_output", "")
                native = st.get("channel") == "native"
                kind, thought, body = split_think(raw, (st.get("request") or {}).get("prompt", ""))
                prefix = "first" if di == 0 else "later"
                if not native:
                    m[prefix + "_text_gens"] += 1
                    m[prefix + "_think"] += kind in ("self", "prefilled")
                    m["think_" + kind] += 1
                    if thought:
                        thought_lengths.append(len(thought))
                    if "<tool_call>" in body and not body.startswith("<tool_call>") and st.get("action_type") == "final":
                        candidate = body[body.index("<tool_call>"):]
                        if call_object(candidate):
                            m["preamble_call_as_final"] += 1
                            details.append({"case": case["id"], "turn": ti + 1, "step": st["number"], "kind": "preamble_call_as_final"})
                    if kind == "unclosed" and "<tool_call>" in raw:
                        m["unclosed_mentions_call"] += 1
                        candidate = raw[raw.rfind("<tool_call>"):]
                        if call_object(candidate):
                            m["unclosed_complete_call_candidate"] += 1
                action_call = (st.get("tool"), st.get("tool_arguments")) if st.get("action_type") == "tool" else None
                if di and not native:
                    m["adjacent_raw_repeat"] += bool(call_object(body)) and body == previous_raw
                if di and action_call:
                    m["adjacent_same_action"] += action_call == previous_call
                previous_raw, previous_call = body, action_call
                repairs.update(st.get("protocol_repairs", []))
                if st.get("tool_rejected_reason") == "duplicate_tool_call":
                    m["duplicate_reject"] += 1
                    if di + 1 < len(decisions):
                        nxt = decisions[di + 1]
                        m["duplicate_with_next_decision"] += 1
                        changed = (nxt.get("tool"), nxt.get("tool_arguments")) != action_call
                        m["duplicate_next_changed_or_exit"] += nxt.get("action_type") == "no_tool" or (nxt.get("action_type") == "final" and not nxt.get("stage_violation")) or (changed and nxt.get("tool_executed", False))
                if st.get("action_type") == "no_tool":
                    lengths.append(len(st.get("no_tool_answer") or st.get("no_tool_rationale") or ""))
            for st in answer_steps:
                m["answer_generations"] += 1
                m["answer_parsed_real_call"] += st.get("action_type") == "tool"
                _, _, body = split_think(st.get("model_output", ""), (st.get("request") or {}).get("prompt", ""))
                m["answer_call_shape"] += bool(call_object(body))
            if bank and case["id"] in bank and not turn.get("passed"):
                turns = bank[case["id"]].get("turns", [])
                if ti < len(turns) and answer_text_match(turns[ti].get("expect", {}), result.get("output", "")):
                    m["failed_answer_text_match"] += 1
                    other = [f for f in failures if not f.startswith("output ") and not f.startswith("output =")]
                    m["answer_match_with_other_failures"] += bool(other)
                    details.append({"case": case["id"], "turn": ti + 1, "kind": "answer_text_match_not_rescore", "other_failures": other})
    return {"version": VERSION, "run": str(run), "valid_for_model_comparison": m["infra_error_turns"] == 0, "metrics": dict(m), "forced_reasons": dict(reasons), "repairs": dict(repairs), "exit_payload_median": statistics.median(lengths) if lengths else None, "think_chars_median": statistics.median(thought_lengths) if thought_lengths else None, "details": details, "case_pass": {c["id"]: c["passed"] for c in summary["cases"]}, "wire": manifest.get("harness", {}).get("wire_canonical"), "model": manifest.get("model"), "sampling": manifest.get("sampling")}


def main():
    ap = argparse.ArgumentParser(description=__doc__)
    ap.add_argument("runs", nargs="+")
    ap.add_argument("--bank")
    ap.add_argument("--json", action="store_true")
    args = ap.parse_args()
    bank = {c["id"]: c for c in json.loads(Path(args.bank).read_text())["cases"]} if args.bank else None
    reports = [analyze(run, bank) for run in args.runs]
    if args.json:
        print(json.dumps(reports, ensure_ascii=False, indent=2))
        return
    rows = {"通过/cases": lambda r: ("无效 run；原始记录 " if not r["valid_for_model_comparison"] else "") + f"{r['metrics'].get('passed', 0)}/{r['metrics']['cases']}", "基础设施错误/turns": lambda r: r["metrics"].get("infra_error_turns", 0), "BFCL irrelevance": lambda r: f"{r['metrics'].get('irrelevance_passed', 0)}/{r['metrics'].get('irrelevance_cases', 0)}", "开场白调用判为final/gens": lambda r: r["metrics"].get("preamble_call_as_final", 0), "未闭合提到调用/完整候选": lambda r: f"{r['metrics'].get('unclosed_mentions_call', 0)}/{r['metrics'].get('unclosed_complete_call_candidate', 0)}", "后续有思考/text gens": lambda r: f"{r['metrics'].get('later_think', 0)}/{r['metrics'].get('later_text_gens', 0)}", "自主收尾/有工具尝试turns": lambda r: f"{r['metrics'].get('self_term_tool_attempts', 0)}/{r['metrics'].get('tool_attempt_turns', 0)}", "强制触发/answer turns": lambda r: f"{r['metrics'].get('forced_triggered', 0)}/{r['metrics'].get('answer_turns', 0)}", "dup拒绝": lambda r: r['metrics'].get('duplicate_reject', 0), "出口payload中位字符": lambda r: r['exit_payload_median'], "答案文本命中/仍有其他失败": lambda r: f"{r['metrics'].get('failed_answer_text_match', 0)}/{r['metrics'].get('answer_match_with_other_failures', 0)}"}
    print("| 指标 | " + " | ".join(Path(r['run']).name for r in reports) + " |")
    print("|---|" + "---|" * len(reports))
    for name, fn in rows.items():
        print("| " + name + " | " + " | ".join(str(fn(r)) for r in reports) + " |")
    if len(reports) > 1:
        base = reports[0]['case_pass']
        for report in reports[1:]:
            other = report['case_pass']
            if set(base) != set(other):
                continue
            print(json.dumps({'compare': Path(report['run']).name, 'gains': [k for k in base if not base[k] and other[k]], 'losses': [k for k in base if base[k] and not other[k]]}, ensure_ascii=False))


if __name__ == "__main__":
    main()
