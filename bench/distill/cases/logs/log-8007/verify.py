# DISTILL-CANARY-cfd21aeb : distillation case
import json
from datetime import datetime, timedelta

case = json.load(open("case.json"))
f = case["files"]
assert "09:15 SGT" in f["support/T-4471.md"]
assert f["logs/checkout-api-2026-09-14.log"].startswith("# checkout-api, region ap-southeast-1")
target = datetime(2026, 9, 14, 9, 15) - timedelta(hours=8)
fails = []
for l in f["logs/checkout-api-2026-09-14.log"].splitlines():
    if " ERROR checkout failed " in l and "merchant=harbourline-florists" in l:
        t = datetime.strptime(l.split()[0], "%Y-%m-%dT%H:%M:%SZ")
        fails.append((abs((t - target).total_seconds()), l.split()[4]))
print(json.dumps({"expected_string": min(fails)[1]}))
