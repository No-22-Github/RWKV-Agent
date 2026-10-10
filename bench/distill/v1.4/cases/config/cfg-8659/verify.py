# DISTILL-CANARY-0bebe7ce : distillation case
import json

case = json.load(open("case.json"))
SPEC = {"path": "logging.yaml", "start": 7, "end": 9, "new": ["    level: DEBUG", "    format: json", "    path: /var/log/app/debug.log"]}
lines = case["files"][SPEC["path"]].splitlines(keepends=True)
assert len(lines) >= SPEC["end"]
lines[SPEC["start"] - 1:SPEC["end"]] = [l + "\n" for l in SPEC["new"]]
print(json.dumps({"files": {SPEC["path"]: "".join(lines)}}, ensure_ascii=False))
