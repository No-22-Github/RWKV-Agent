# DISTILL-CANARY-b8050b51 : distillation case
import json

case = json.load(open("case.json"))
SPEC = {"path": "docker-compose.yml", "start": 13, "end": 15, "new": ["      interval: 10s", "      timeout: 3s", "      retries: 5"]}
lines = case["files"][SPEC["path"]].splitlines(keepends=True)
assert len(lines) >= SPEC["end"]
lines[SPEC["start"] - 1:SPEC["end"]] = [l + "\n" for l in SPEC["new"]]
print(json.dumps({"files": {SPEC["path"]: "".join(lines)}}, ensure_ascii=False))
