# DISTILL-CANARY-bda0a050 : distillation case
import json

case = json.load(open("case.json"))
SPEC = {"path": "db/pools.toml", "start": 7, "end": 9, "new": ["min = 4", "max = 24", "idle_timeout = \"15s\""]}
lines = case["files"][SPEC["path"]].splitlines(keepends=True)
assert len(lines) >= SPEC["end"]
lines[SPEC["start"] - 1:SPEC["end"]] = [l + "\n" for l in SPEC["new"]]
print(json.dumps({"files": {SPEC["path"]: "".join(lines)}}, ensure_ascii=False))
