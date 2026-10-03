# DISTILL-CANARY-2f5fd462 : distillation case
import json
import re
from datetime import datetime

case = json.load(open("case.json"))
assert case["files"]["README.md"].startswith("Tidal ingest worker logs")
lines = case["files"]["logs/ingest-2026-09-15.log"].splitlines()
ts = lambda l: datetime.strptime(l.split()[0], "%Y-%m-%dT%H:%M:%SZ")
start = ts([l for l in lines if "job start" in l][0])
batches = [l for l in lines if " done events=" in l]
ev = sum(int(re.search(r"events=(\d+)", l).group(1)) for l in batches)
print(json.dumps({"expected_number": round(ev / (ts(batches[-1]) - start).total_seconds(), 2)}))
