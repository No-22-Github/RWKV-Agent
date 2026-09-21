#!/usr/bin/env python3
"""Layered failure attribution: is a run's score a capability reading at all?

A single pass rate cannot answer that. G1K scored 2.5% on this bank and 81.7%
on BFCL with the same weights: the bank score was measuring multi-step protocol
discipline, not the reasoning the cases were written to test. Reading it as
"the model cannot do these tasks" was wrong, and no number in the run artifacts
said so.

This tool decomposes every non-pass into ordered layers and refuses to report a
capability number until the layers beneath it are clear:

  infra      upstream/transport aborted the case; it produced no answer
  protocol   the model could not form a well-formed interaction
  closeout   the model never stopped: step limit, forced answer, no final answer
  format     the answer led with the right value in the wrong shape
  capability the model answered, well-formed and in shape, and was wrong

Layers are ordered and first-match-wins, because a case that broke at
`protocol` never reached the question the case asks. The verdict reports
whether `capability` is measurable for this model, not whether the model is
good.

Diagnostic only. Official pass/fail is read from the artifacts and never
recomputed; this tool only classifies the failures the harness already scored.

Usage:
  python3 tools/capability_gate.py RUNDIR [RUNDIR ...] [--label NAME] [--json OUT]
  python3 tools/capability_gate.py runs/workbank/flash-final-k*-20260921
"""
import argparse
import json
import re
from collections import Counter, defaultdict
from pathlib import Path

VERSION = "capability-gate-v1"

# A model whose runs exceed these is not being measured on capability. The
# thresholds are deliberately loose: they mark "this score is not a capability
# reading", not "this model is bad".
PROTOCOL_CEILING = 0.10
CLOSEOUT_CEILING = 0.15

LAYERS = ["infra", "protocol", "closeout", "format", "capability"]

INFRA_MARKERS = (
    "upstream provider failure",
    "continuation error:",
    "http 4", "http 5",
    "connection refused", "connection reset", "no such host",
    "context deadline exceeded", "timeout", "unexpected eof", "broken pipe",
)
PROTOCOL_MARKERS = (
    "agent protocol error",
    "protocol error",
    "is not a json object",
    "action is not allowed",
    "stage violation",
    "envelope",
    "decode",
    "answer contract repaired",
)
CLOSEOUT_MARKERS = (
    "step limit",
    "output token limit",
    "max turns",
    "forced answer",
    "reached the step limit",
)

NUMBER = re.compile(r"[+-]?\d+(?:,\d{3})*(?:\.\d+)?")
EMPHASIS = ("**", "__", "*", "_", "`")


def normalize(text):
    """Mirror of the scorer's answer normalization, for classification only."""
    value = (text or "").strip()
    changed = True
    while changed:
        changed = False
        for marker in EMPHASIS:
            if len(value) > 2 * len(marker) and value.startswith(marker) \
                    and value.endswith(marker) and marker not in value[len(marker):-len(marker)]:
                value = value[len(marker):-len(marker)].strip()
                changed = True
    return value.rstrip(".。!！;；,，").strip().lower()


def answer_of(case):
    for turn in case.get("turns") or []:
        result = turn.get("result") or {}
        return result.get("original_output") or result.get("output") or ""
    return ""


def failures_of(case):
    out = list(case.get("failures") or [])
    if case.get("error"):
        out.append("case error: " + case["error"])
    for turn in case.get("turns") or []:
        out.extend(turn.get("failures") or [])
        if turn.get("runner_error"):
            out.append("runner error: " + turn["runner_error"])
    return out


def expected_values(spec):
    """Every accepted answer string for a case, from its frozen expectations."""
    values = []
    for turn in spec.get("turns") or []:
        expect = turn.get("expect") or {}
        if expect.get("output_equals") is not None:
            values.append(str(expect["output_equals"]))
        values.extend(str(v) for v in (expect.get("output_equals_any") or []))
        if expect.get("expected_number") is not None:
            values.append(repr(float(expect["expected_number"])))
    return values


ANSWER_MARKERS = ("final answer:", "answer:", "答案：", "答案:", "最终答案：", "最终答案:")


def salient_candidates(answer):
    """Where a reply's committed value plausibly sits: either end, or after a marker.

    Both ends are needed. Some models lead with the figure and justify it after;
    small instruct models typically reason first and commit at the end
    ("... = 9000 MiB per hour.\n\n9000", "Final answer: 8431"). Scoring only the
    leading position files that second group under wrong answers, which is
    backwards for exactly the models this bank is built to track.

    The middle is deliberately not searched: on a case whose decoy is itself a
    number, position is the only thing separating a commitment from a mention.
    """
    trimmed = (answer or "").strip()
    if not trimmed:
        return []
    lines = [l.strip() for l in trimmed.splitlines() if l.strip()]
    out = []

    def add(line):
        line = line.strip()
        if not line:
            return
        out.append(line)
        parts = line.split()
        if len(parts) > 1:
            out.append(parts[0])
            out.append(parts[-1])

    if lines:
        add(lines[0])
        add(lines[-1])
    lowered = trimmed.lower()
    for marker in ANSWER_MARKERS:
        index = lowered.rfind(marker)
        if index >= 0:
            add(trimmed[index + len(marker):])
    return out


def carries_expected(answer, spec):
    """True when an accepted value sits at a salient position but is not the whole reply."""
    normalized = normalize(answer)
    if not normalized:
        return False
    candidates = [normalize(c) for c in salient_candidates(answer)]
    for want in expected_values(spec):
        want_n = normalize(want)
        if not want_n or normalized == want_n:
            continue
        if want_n in candidates:
            return True
        try:
            target = float(want_n.replace(",", ""))
        except ValueError:
            continue
        for candidate in candidates:
            found = NUMBER.match(candidate.lstrip("$€£¥"))
            if found:
                try:
                    if abs(float(found.group().replace(",", "")) - target) <= 0.011:
                        return True
                except ValueError:
                    pass
    return False


def classify(case, spec):
    """Assign one layer to a non-passing case. First match wins."""
    if case.get("invalid"):
        return "infra"
    blob = " | ".join(failures_of(case)).lower()
    if any(marker in blob for marker in INFRA_MARKERS):
        return "infra"
    if any(marker in blob for marker in PROTOCOL_MARKERS):
        return "protocol"
    if any(marker in blob for marker in CLOSEOUT_MARKERS):
        return "closeout"
    answer = answer_of(case)
    if not normalize(answer) and blob:
        # Ran out of turns without ever committing an answer.
        return "closeout"
    if carries_expected(answer, spec):
        return "format"
    return "capability"


def decoy_hits(case, spec):
    """Which declared decoys this answer matched. An unhit trap may be inert."""
    tags = spec.get("tags") or {}
    decoys = tags.get("trap_decoys") or {}
    answer = normalize(answer_of(case))
    if not answer:
        return []
    hits = []
    for trap, value in decoys.items():
        if value is None:
            continue
        want = normalize(str(value))
        if not want:
            continue
        if answer == want or answer.startswith(want + " ") or want in answer.split():
            hits.append(trap)
            continue
        try:
            target = float(want.replace(",", ""))
        except ValueError:
            continue
        for found in NUMBER.finditer(answer.replace("$", "").replace("€", "")):
            try:
                if abs(float(found.group().replace(",", "")) - target) <= 0.011:
                    hits.append(trap)
                    break
            except ValueError:
                pass
    return hits


def analyze(run_dirs, label):
    layers = Counter()
    scored = passed = voided = 0
    per_case = defaultdict(lambda: {"pass": 0, "runs": 0, "layers": Counter()})
    decoy_total = Counter()
    decoy_hit = Counter()
    for run_dir in run_dirs:
        run_dir = Path(run_dir)
        summary = json.loads((run_dir / "summary.json").read_text())
        manifest = json.loads((run_dir / "run.json").read_text())
        specs = {c["id"]: c for c in manifest.get("cases", [])}
        for case in summary["cases"]:
            spec = specs.get(case["id"], {})
            entry = per_case[case["id"]]
            if case.get("invalid"):
                voided += 1
                layers["infra"] += 1
                entry["layers"]["infra"] += 1
                continue
            entry["runs"] += 1
            scored += 1
            if case.get("passed"):
                passed += 1
                entry["pass"] += 1
            else:
                layer = classify(case, spec)
                layers[layer] += 1
                entry["layers"][layer] += 1
            tags = spec.get("tags") or {}
            for trap, value in (tags.get("trap_decoys") or {}).items():
                if value is not None:
                    decoy_total[trap] += 1
            for trap in decoy_hits(case, spec):
                decoy_hit[trap] += 1
    total_attempts = scored + voided
    protocol_rate = layers["protocol"] / scored if scored else 0.0
    closeout_rate = layers["closeout"] / scored if scored else 0.0
    measurable = protocol_rate <= PROTOCOL_CEILING and closeout_rate <= CLOSEOUT_CEILING
    return {
        "version": VERSION,
        "label": label,
        "runs": [str(p) for p in run_dirs],
        "attempts": total_attempts,
        "voided": voided,
        "scored": scored,
        "passed": passed,
        "pass_rate": round(passed / scored, 4) if scored else None,
        "layers": {layer: layers[layer] for layer in LAYERS},
        "protocol_rate": round(protocol_rate, 4),
        "closeout_rate": round(closeout_rate, 4),
        "capability_measurable": measurable,
        "decoys": {
            trap: {"exposed": decoy_total[trap], "hit": decoy_hit[trap],
                   "hit_rate": round(decoy_hit[trap] / decoy_total[trap], 4)}
            for trap in sorted(decoy_total)
        },
        "per_case": {
            cid: {"pass": v["pass"], "runs": v["runs"],
                  "layers": dict(v["layers"])}
            for cid, v in sorted(per_case.items())
        },
    }


def render(report):
    print(f"== {report['label']}  ({len(report['runs'])} run(s))")
    print(f"   官方通过 {report['passed']}/{report['scored']}"
          f" = {report['pass_rate']:.1%}" if report["scored"] else "   no scored cases")
    if report["voided"]:
        print(f"   作废(上游中断，不计分母) {report['voided']}")
    print("   失败分层:")
    for layer in LAYERS:
        count = report["layers"][layer]
        if count:
            print(f"      {layer:11} {count}")
    verdict = "可以当能力读数" if report["capability_measurable"] else \
              "不可当能力读数 —— 分数被协议/收尾主导"
    print(f"   判定: {verdict}"
          f"  (protocol {report['protocol_rate']:.1%}, closeout {report['closeout_rate']:.1%})")
    if report["decoys"]:
        print("   陷阱 decoy 命中率:")
        for trap, stat in report["decoys"].items():
            note = "  <- 从未命中，陷阱可能是死的" if stat["hit"] == 0 else ""
            print(f"      {trap:16} {stat['hit']:3}/{stat['exposed']:<3}"
                  f" = {stat['hit_rate']:5.1%}{note}")


def main():
    parser = argparse.ArgumentParser(description=__doc__,
                                     formatter_class=argparse.RawDescriptionHelpFormatter)
    parser.add_argument("runs", nargs="+", type=Path)
    parser.add_argument("--label", default=None, help="name for this model/config group")
    parser.add_argument("--json", type=Path, help="write the full report here")
    args = parser.parse_args()
    label = args.label or args.runs[0].name
    report = analyze(args.runs, label)
    render(report)
    if args.json:
        args.json.parent.mkdir(parents=True, exist_ok=True)
        args.json.write_text(json.dumps(report, ensure_ascii=False, indent=2) + "\n")
        print(f"   -> {args.json}")


if __name__ == "__main__":
    main()
