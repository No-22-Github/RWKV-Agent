# DISTILL-CANARY-4317f9ca : distillation case
import json

case = json.load(open("case.json"))
lines = case["files"]["logs/telemetry-0926.jsonl"].splitlines()

rows = []
for line in lines:
    if not line.strip():
        continue
    r = json.loads(line)
    rows.append((r["ts"], r["site"], float(r["temp_delta_c"]), r["status"]))

lo, hi = "2026-09-26T08:00:00+08:00", "2026-09-26T12:00:00+08:00"
above = [r for r in rows if r[1] == "冷库A" and lo <= r[0] < hi and r[2] < 0]
kept = [r for r in above if r[3] != "defrost"]
defrost = sum(1 for r in rows if r[3] == "defrost")
worst = "%.1f" % max(abs(r[2]) for r in kept)

_cg = case["files"].get('logs/telemetry-0926.jsonl', "")
if '{"ts":"2026-09-26T22:40:07+08:00","site":"冷库A","temp_delta_c":-1.1,"status":"ok"}' not in _cg:
    raise SystemExit(1)
print(json.dumps({"expected_number": len(above)}))
