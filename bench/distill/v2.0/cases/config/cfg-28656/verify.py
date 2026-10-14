# DISTILL-CANARY-4ac1bd91 : distillation case
import json

case = json.load(open("case.json"))
SPEC = {"path": "配置/缓存.json", "start": 4, "end": 5, "new": ["    \"用户\": { \"ttl\": 900, \"最大条数\": 30000 },", "    \"券\": { \"ttl\": 60, \"最大条数\": 1500 },"]}
lines = case["files"][SPEC["path"]].splitlines(keepends=True)
assert len(lines) >= SPEC["end"]
lines[SPEC["start"] - 1:SPEC["end"]] = [l + "\n" for l in SPEC["new"]]
print(json.dumps({"files": {SPEC["path"]: "".join(lines)}}, ensure_ascii=False))
