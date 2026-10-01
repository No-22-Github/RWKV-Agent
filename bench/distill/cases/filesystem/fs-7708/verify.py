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
_data = case["files"].get('scores/term-2025autumn/score-qingchun.txt', "")
if not _data.splitlines() or _data.splitlines()[0] != '星野合唱团 2025 秋季用谱：青春舞曲（旧版）。':
    raise SystemExit(1)
facts = ["2025 秋季", "2025 年秋季", "2025 年秋"]
print(json.dumps({"expected_contains_any": facts}))
