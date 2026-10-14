# DISTILL-CANARY-fc2e4d63 : distillation case
import json

case = json.load(open("case.json"))
SPEC = {"path": "systemd/export.service", "start": 7, "end": 9, "new": ["Restart=always", "RestartSec=10", "LimitNOFILE=65536"]}
lines = case["files"][SPEC["path"]].splitlines(keepends=True)
assert len(lines) >= SPEC["end"]
lines[SPEC["start"] - 1:SPEC["end"]] = [l + "\n" for l in SPEC["new"]]
print(json.dumps({"files": {SPEC["path"]: "".join(lines)}}, ensure_ascii=False))
