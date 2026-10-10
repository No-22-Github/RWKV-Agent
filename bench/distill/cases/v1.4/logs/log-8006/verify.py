# DISTILL-CANARY-1b2a1425 : distillation case
import json
from datetime import datetime, timedelta

case = json.load(open("case.json"))
assert "UTC" in case["files"]["README.md"]
lines = case["files"]["logs/tide-gw.log"].splitlines()
assert lines[0].startswith("# tide-gw log, host tide-gw-01")
dep = next(i for i, l in enumerate(lines) if "deploy version=tide-gw-2.9.0" in l)
err = next(l for l in lines[dep + 1:] if " ERROR " in l)
t = datetime.strptime(err.split()[0], "%Y-%m-%dT%H:%M:%SZ") + timedelta(hours=8)
print(json.dumps({"expected_string": t.strftime("%Y-%m-%d %H:%M:%S")}))
