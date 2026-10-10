# DISTILL-CANARY-47cceb1f : distillation case
import json

case = json.load(open("case.json"))
SPEC = {"path": "monitoring/rules.yaml", "start": 8, "end": 11, "new": ["      - alert: HighP99", "        expr: p99_ms > 1500", "        for: 10m", "        severity: critical"]}
lines = case["files"][SPEC["path"]].splitlines(keepends=True)
assert len(lines) >= SPEC["end"]
lines[SPEC["start"] - 1:SPEC["end"]] = [l + "\n" for l in SPEC["new"]]
print(json.dumps({"files": {SPEC["path"]: "".join(lines)}}, ensure_ascii=False))
