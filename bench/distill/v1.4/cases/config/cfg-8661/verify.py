# DISTILL-CANARY-9f9fe1fe : distillation case
import json

case = json.load(open("case.json"))
SPEC = {"path": "etc/crontab.jobs", "start": 3, "end": 4, "new": ["45 3 * * * /opt/jobs/vacuum-db.sh", "0 4 * * 6 /opt/jobs/full-backup.sh"]}
lines = case["files"][SPEC["path"]].splitlines(keepends=True)
assert len(lines) >= SPEC["end"]
lines[SPEC["start"] - 1:SPEC["end"]] = [l + "\n" for l in SPEC["new"]]
print(json.dumps({"files": {SPEC["path"]: "".join(lines)}}, ensure_ascii=False))
