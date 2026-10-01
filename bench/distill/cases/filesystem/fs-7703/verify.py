# DISTILL-CANARY-81ab2c02 : distillation case
import json

case = json.load(open("case.json"))
keys = list(case["files"].keys())
live = [k for k in keys if "2026-term2" in k]
old = [k for k in keys if "2026-term1" in k]
if not live or not old:
    raise SystemExit(1)
live_text = case["files"][live[0]]
old_lines = [l for l in case["files"][old[0]].splitlines() if l.strip()]
if "8 sentences" not in live_text or "term 1" not in old_lines[0]:
    raise SystemExit(1)
facts = [
    "2026-term2",
    "8 sentences",
    "term 1",
]
print(json.dumps({"expected_contains_any": facts}))
