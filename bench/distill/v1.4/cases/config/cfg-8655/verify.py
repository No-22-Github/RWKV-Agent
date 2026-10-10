# DISTILL-CANARY-50c6ddf2 : distillation case
import json

case = json.load(open("case.json"))
SPEC = {"path": ".ssh/config.d/bastions", "start": 8, "end": 10, "new": ["    HostName 34.201.12.140", "    User deploy", "    Port 2222"]}
lines = case["files"][SPEC["path"]].splitlines(keepends=True)
assert len(lines) >= SPEC["end"]
lines[SPEC["start"] - 1:SPEC["end"]] = [l + "\n" for l in SPEC["new"]]
print(json.dumps({"files": {SPEC["path"]: "".join(lines)}}, ensure_ascii=False))
