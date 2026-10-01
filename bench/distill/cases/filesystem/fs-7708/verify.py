# DISTILL-CANARY-05a57a38 : distillation case
import json

case = json.load(open("case.json"))
keys = list(case["files"].keys())
live = [k for k in keys if "term-2026spring" in k]
old = [k for k in keys if "term-2025autumn" in k]
if not live or not old:
    raise SystemExit(1)
live_text = case["files"][live[0]]
old_lines = [l for l in case["files"][old[0]].splitlines() if l.strip()]
if "混声四部" not in live_text:
    raise SystemExit(1)
if "2025 秋季" not in old_lines[0]:
    raise SystemExit(1)
facts = [
    "term-2026spring",
    "混声四部",
    "2025 秋季",
]
print(json.dumps({"expected_contains_any": facts}))
