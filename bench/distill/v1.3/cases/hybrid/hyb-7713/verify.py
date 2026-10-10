# DISTILL-CANARY-19e4a8c2 : distillation case
import json

case = json.load(open("case.json"))
lines = case["files"]["logs/humidity-alerts-2026-09.log"].splitlines()
if not lines or not lines[0].startswith("#"):
    raise SystemExit("fixture shape changed: log header line missing")
alerts = []
for line in lines[1:]:
    if not line.endswith("告警"):
        continue
    ts = line.split()[0]
    utc_hour = int(ts[11:13])
    local_hour = (utc_hour + 8) % 24
    local_day = int(ts[8:10]) + (1 if utc_hour + 8 >= 24 else 0)
    alerts.append((utc_hour, local_day, local_hour))
night = [a for a in alerts if a[2] >= 22 or a[2] < 6]
per_day = {}
for a in night:
    per_day[a[1]] = per_day.get(a[1], 0) + 1
top_day = max(per_day, key=lambda d: per_day[d])
out = {
    "expected_number": len(alerts),
    "expected_turn_2": len(night),
    "expected_turn_3": 20260900 + top_day,
}
print(json.dumps(out))
