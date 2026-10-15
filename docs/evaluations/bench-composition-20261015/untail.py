"""Drop the "if you can't find it, tell me why" endings from exam prompts.

naturalize.py (same directory) replaced the old "Reply with only the final
answer ... UNKNOWN" tail with four natural-sounding endings. All four still
say "if you can't pin it down / can't find it, say so", which nudges a model
to give up after one look (gap-fill-spec §2.1 rule 2: DeepSeek abandoned 7
web cases that way), and 79 workbank prompts ending the same four ways read
like a template. Each such ending becomes, by a stable hash of case id and
turn: nothing (half the cases), "A short answer is fine." or "Keep it brief."

Idempotent: prompts that no longer end with one of the four are untouched.
tags.version is bumped once per changed case.

    python3 docs/evaluations/bench-composition-20261015/untail.py
"""
import hashlib
import json

OLD_TAILS = [
    "Just give me the answer. If you can't pin it down, tell me why.",
    "A short answer is fine. If you can't find it, say so and tell me what you checked.",
    "Just tell me the result; if you can't find it, tell me that instead.",
    "Keep it brief, and if it can't be worked out, let me know why.",
]
NEW_TAILS = ["", "A short answer is fine.", "", "Keep it brief."]


def pick(key):
    return NEW_TAILS[hashlib.sha256(key.encode()).digest()[0] % len(NEW_TAILS)]


def main():
    changed = 0
    # Only cases on the exam; training data under bench/distill must never change.
    with open("bench/exam/full.json", encoding="utf-8") as f:
        paths = [c["path"] + "/case.json" for c in json.load(f)["cases"]]
    for path in sorted(paths):
        with open(path, encoding="utf-8") as f:
            case = json.load(f)
        touched = False
        for i, turn in enumerate(case.get("turns") or []):
            prompt = turn.get("prompt", "")
            for tail in OLD_TAILS:
                if prompt.endswith(tail):
                    head = prompt[: -len(tail)].rstrip()
                    turn["prompt"] = (head + " " + pick(f"{case['id']}#{i}")).strip()
                    touched = True
                    break
        if not touched:
            continue
        case["tags"]["version"] = case["tags"].get("version", 1) + 1
        with open(path, "w", encoding="utf-8") as f:
            f.write(json.dumps(case, indent=2, ensure_ascii=False) + "\n")
        changed += 1
    print(f"{changed} case(s) rewritten")


if __name__ == "__main__":
    main()
