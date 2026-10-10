# DISTILL-CANARY-fcd0dfd0 : distillation case
import json

case = json.load(open("case.json"))
SPEC = {"path": "k8s/deploy-pipeline.yaml", "start": 8, "end": 9, "new": ["        cpu: 1000m", "        memory: 1Gi"]}
lines = case["files"][SPEC["path"]].splitlines(keepends=True)
assert len(lines) >= SPEC["end"]
lines[SPEC["start"] - 1:SPEC["end"]] = [l + "\n" for l in SPEC["new"]]
print(json.dumps({"files": {SPEC["path"]: "".join(lines)}}, ensure_ascii=False))
