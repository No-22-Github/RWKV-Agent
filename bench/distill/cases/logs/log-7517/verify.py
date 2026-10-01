# DISTILL-CANARY-4ebeb734 : distillation case
import json
from datetime import datetime, timezone, timedelta

case = json.load(open("case.json"))
lines = case["files"]["logs/telemetry-0926.jsonl"].splitlines()

CN = timezone(timedelta(hours=8))


def parse(ts):
    if "T" in ts:
        return datetime.fromisoformat(ts)
    return datetime.strptime(ts, "%d-%m-%Y %H:%M:%S%z")


rows = []
for line in lines:
    if not line.strip():
        continue
    r = json.loads(line)
    t = parse(r["ts"]).astimezone(CN).replace(tzinfo=None)
    rows.append((t, r["sensor"], r["site"], r["temp_c"], r["status"]))

window = [r for r in rows if r[2] == "冷库B" and datetime(2026, 9, 26, 8, 0, 0) <= r[0] < datetime(2026, 9, 26, 12, 0, 0) and r[3] > -18]
warm = [r for r in rows if r[1] == "TH-0114" and r[3] > -18]
per_sensor = {}
for r in window:
    per_sensor[r[1]] = per_sensor.get(r[1], 0) + 1
top = sorted(per_sensor.items(), key=lambda kv: (-kv[1], kv[0]))[0][0]
first = min(r[0] for r in warm if datetime(2026, 9, 26, 8, 0, 0) <= r[0] < datetime(2026, 9, 26, 12, 0, 0))
in_window = [r for r in warm if datetime(2026, 9, 26, 8, 0, 0) <= r[0] < datetime(2026, 9, 26, 12, 0, 0)]
warmest = max(r[3] for r in in_window)
defrost = sum(1 for r in rows if r[4] == "defrost")

forms = ["%d 条" % len(window), top,
         first.strftime("%H:%M"), first.strftime("%H:%M:%S"),
         "%s" % warmest, "%d 条" % defrost]
print(json.dumps({"expected_contains_any": sorted(set(forms))}))
