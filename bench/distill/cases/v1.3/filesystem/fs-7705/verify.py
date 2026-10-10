# DISTILL-CANARY-8c4d536b : distillation case
import json

case = json.load(open("case.json"))
keys = list(case["files"].keys())
current = [k for k in keys if "/2026/" in k]
old = [k for k in keys if "/2025/" in k]
if not current or not old:
    raise SystemExit(1)
cur_text = case["files"][current[0]]
old_lines = [l for l in case["files"][old[0]].splitlines() if l.strip()]
if "2026-05-22" not in cur_text or "Loon Basin" not in cur_text:
    raise SystemExit(1)
if "2025 backcountry camping permit" not in old_lines[0]:
    raise SystemExit(1)
_data = case["files"].get('permits/2025/camping-permit-may.txt', "")
if not _data.splitlines() or _data.splitlines()[0] != 'Silver Ridge Hiking Club - 2025 backcountry camping permit.':
    raise SystemExit(1)
facts = ["2026-05-22", "May 22, 2026", "22 May 2026"]
print(json.dumps({"expected_contains_any": facts}))
