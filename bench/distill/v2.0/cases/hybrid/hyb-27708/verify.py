# DISTILL-CANARY-c74f19b8 : distillation case
import csv
import io
import json
from datetime import datetime, timedelta, timezone

case = json.load(open("case.json"))
rows = list(csv.DictReader(io.StringIO(case["files"]["telemetry/weighbridge-2026-09.csv"])))
def day_shift(start_hour):
    n = 0
    for r in rows:
        ts = datetime.fromisoformat(r["timestamp_utc"].replace("Z", "+00:00"))
        local = ts.astimezone(timezone(timedelta(hours=10)))
        if start_hour <= local.hour < 18:
            n += 1
    return n
out = {
    "expected_number": day_shift(6),
    "expected_turn_2": day_shift(5),
}
print(json.dumps(out))
