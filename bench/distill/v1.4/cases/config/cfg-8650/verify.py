# DISTILL-CANARY-813f7549 : distillation case
import json

case = json.load(open("case.json"))
SPEC = {"path": "网关/上游.conf", "start": 9, "end": 11, "new": ["    server 10.2.4.31:8080 weight=4;", "    server 10.2.4.32:8080 weight=1;", "    keepalive 64;"]}
lines = case["files"][SPEC["path"]].splitlines(keepends=True)
assert len(lines) >= SPEC["end"]
lines[SPEC["start"] - 1:SPEC["end"]] = [l + "\n" for l in SPEC["new"]]
print(json.dumps({"files": {SPEC["path"]: "".join(lines)}}, ensure_ascii=False))
