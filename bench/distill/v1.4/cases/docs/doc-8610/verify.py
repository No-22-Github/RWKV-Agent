# DISTILL-CANARY-b7f1570d : distillation case
import json

case = json.load(open("case.json"))
SPEC = {"path": "食谱/家常菜.md", "start": 4, "end": 7, "new": ["- 番茄 3 个", "- 鸡蛋 4 个", "- 盐 3 克", "- 糖 8 克"]}
lines = case["files"][SPEC["path"]].splitlines(keepends=True)
assert len(lines) >= SPEC["end"]
lines[SPEC["start"] - 1:SPEC["end"]] = [l + "\n" for l in SPEC["new"]]
print(json.dumps({"files": {SPEC["path"]: "".join(lines)}}, ensure_ascii=False))
