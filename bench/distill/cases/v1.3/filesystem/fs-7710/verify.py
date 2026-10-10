# DISTILL-CANARY-4f25d2bf : distillation case
import json

case = json.load(open("case.json"))
keys = list(case["files"].keys())
current = [k for k in keys if "/2026/" in k]
old = [k for k in keys if "/2025/" in k]
if not current or not old:
    raise SystemExit(1)
cur_text = case["files"][current[0]]
old_lines = [l for l in case["files"][old[0]].splitlines() if l.strip()]
if "2026-06-30" not in cur_text or "钉耙" not in cur_text:
    raise SystemExit(1)
if "2025 年工具借用登记" not in old_lines[0]:
    raise SystemExit(1)
_data = case["files"].get('records/2025/borrow-form-rakes.txt', "")
if not _data.splitlines() or _data.splitlines()[0] != '望泽园社区花园 2025 年工具借用登记：钉耙（已归档）。':
    raise SystemExit(1)
facts = ["2026-06-30", "2026 年 6 月 30 日", "6 月 30 日"]
print(json.dumps({"expected_contains_any": facts}))
