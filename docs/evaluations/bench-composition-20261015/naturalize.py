#!/usr/bin/env python3
"""One-off migration (2026-10-15): rewrite exam cases the way an App user asks.

Run from the repository root, then rebuild the exam:
    python3 docs/evaluations/bench-composition-20261015/naturalize.py
    go run ./cmd/rwkv-lab exam import-builtin   # boundary/bfcl are regenerated, see below
    go run ./cmd/rwkv-lab exam build

What changes (REPORT.md §8):
- workbank (clean cases only): the "Reply with only the final answer ... UNKNOWN"
  and "When finished, reply DONE." tails become one of a few natural phrasings
  (picked by a stable hash of the case id, so the exam does not teach one
  template). The old last-turn prompt is kept in tags.legacy_prompt.
- every exam case: expected_number gains expected_number_in_text (the figure may
  sit inside prose); output_equals / output_equals_any become whole-token
  output_contains / output_contains_any; max_output_chars is dropped.
- the three workbank cases whose answer is UNKNOWN must instead name the missing
  item (must_state_unverified) and say it is missing.
- tags.answer_style = "natural", tags.version += 1 for every changed case.

The script is idempotent: a case already tagged answer_style natural with no
remaining legacy fields is left byte-identical. bench/exam/imported/ is not
touched here; the exporter applies the same scoring rules when it writes.
"""
import glob
import hashlib
import json
import os

UNKNOWN_TAIL = "Reply with only the final answer. If you cannot determine the answer, reply exactly UNKNOWN."
DONE_TAIL = "When finished, reply DONE."

ANSWER_TAILS = [
    "Just give me the answer. If you can't pin it down, tell me why.",
    "A short answer is fine. If you can't find it, say so and tell me what you checked.",
    "Just tell me the result; if you can't find it, tell me that instead.",
    "Keep it brief, and if it can't be worked out, let me know why.",
]
DONE_TAILS = [
    "Let me know when it's done.",
    "Tell me when you're finished.",
    "Let me know once that's in place.",
    "",
]
ABSENCE_PHRASES = ["not ", "n't", "no ", "No ", "missing", "absent", "unable", "UNKNOWN", "cannot"]
ABSTAIN_ITEMS = {
    "cfg-0011": ["dispute_hold_minutes"],
    "cfg-0012": ["sfo-edge"],
    "fs-0011": ["pumpnet-oncology"],
}

SOURCES = [
    "bench/workbank/cases/*/*/case.json",
    "bench/holdout/p13/*/*/case.json",
    "bench/bashprobe/cases/*/case.json",
    "bench/bashprobe/cases-b14/*/case.json",
    "bench/weatherprobe/cases/*/case.json",
    "bench/weatherprobe/cases-b14/*/case.json",
]


def pick(options, case_id):
    digest = hashlib.sha256(case_id.encode()).digest()
    return options[digest[0] % len(options)]


def load_leaked():
    with open("bench/workbank/seeded-base700.txt") as handle:
        return {line.strip() for line in handle if line.strip() and not line.startswith("#")}


def rewrite_tail(prompt, case_id):
    if prompt.endswith(UNKNOWN_TAIL):
        head = prompt[: -len(UNKNOWN_TAIL)].rstrip()
        return (head + " " + pick(ANSWER_TAILS, case_id)).strip()
    if prompt.endswith(DONE_TAIL):
        head = prompt[: -len(DONE_TAIL)].rstrip()
        return (head + " " + pick(DONE_TAILS, case_id)).strip()
    return prompt


def rescore(expect, case_id):
    changed = False
    if "expected_number" in expect and not expect.get("expected_number_in_text"):
        expect["expected_number_in_text"] = True
        changed = True
    if "output_equals" in expect:
        value = expect.pop("output_equals")
        changed = True
        if value == "UNKNOWN":
            expect["must_state_unverified"] = ABSTAIN_ITEMS[case_id]
            expect["output_contains_any"] = ABSENCE_PHRASES
        else:
            expect.setdefault("output_contains", [])
            expect["output_contains"].append(value)
            expect["output_contains_token"] = True
    if "output_equals_any" in expect:
        values = expect.pop("output_equals_any")
        changed = True
        expect["output_contains_any"] = values
        expect["output_contains_any_token"] = True
    if "max_output_chars" in expect:
        expect.pop("max_output_chars")
        changed = True
    return changed


def dump_like(original_text, data):
    text = json.dumps(data, indent=2, ensure_ascii=False)
    if original_text.endswith("\n"):
        text += "\n"
    return text


def main():
    leaked = load_leaked()
    counts = {"changed": 0, "prompt": 0, "skipped_leaked": 0}
    for pattern in SOURCES:
        for path in sorted(glob.glob(pattern)):
            with open(path, encoding="utf-8") as handle:
                original = handle.read()
            case = json.loads(original)
            if case["id"] in leaked:
                counts["skipped_leaked"] += 1
                continue
            changed = False
            last = case["turns"][-1]
            new_prompt = rewrite_tail(last["prompt"], case["id"])
            if new_prompt != last["prompt"]:
                case["tags"].setdefault("legacy_prompt", last["prompt"])
                last["prompt"] = new_prompt
                changed = True
                counts["prompt"] += 1
            for turn in case["turns"]:
                if "expect" in turn and rescore(turn["expect"], case["id"]):
                    changed = True
            if not changed:
                continue
            case["tags"]["answer_style"] = "natural"
            case["tags"]["version"] = int(case["tags"].get("version", 1)) + 1
            with open(path, "w", encoding="utf-8") as handle:
                handle.write(dump_like(original, case))
            counts["changed"] += 1
    print(json.dumps(counts))


if __name__ == "__main__":
    os.chdir(os.path.join(os.path.dirname(os.path.abspath(__file__)), "..", "..", ".."))
    main()
