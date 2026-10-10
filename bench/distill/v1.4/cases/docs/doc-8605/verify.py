# DISTILL-CANARY-786b7eb3 : distillation case
import json

case = json.load(open("case.json"))
SPEC = {"path": "docs/api/list.md", "start": 7, "end": 8, "new": ["| sort | string | updated |", "| order | string | asc |"]}
lines = case["files"][SPEC["path"]].splitlines(keepends=True)
assert len(lines) >= SPEC["end"]
lines[SPEC["start"] - 1:SPEC["end"]] = [l + "\n" for l in SPEC["new"]]
print(json.dumps({"files": {SPEC["path"]: "".join(lines)}}, ensure_ascii=False))
