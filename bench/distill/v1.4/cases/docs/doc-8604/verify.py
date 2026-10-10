# DISTILL-CANARY-2262d73e : distillation case
import json

case = json.load(open("case.json"))
SPEC = {"path": "制度/差旅报销.md", "start": 9, "end": 11, "new": ["高铁二等座据实报销，商务座须提前审批。", "飞机经济舱据实报销，须提前 7 天订票。", "市内打车每次不超过 100 元。"]}
lines = case["files"][SPEC["path"]].splitlines(keepends=True)
assert len(lines) >= SPEC["end"]
lines[SPEC["start"] - 1:SPEC["end"]] = [l + "\n" for l in SPEC["new"]]
print(json.dumps({"files": {SPEC["path"]: "".join(lines)}}, ensure_ascii=False))
