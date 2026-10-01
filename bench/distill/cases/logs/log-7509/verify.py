# DISTILL-CANARY-b9f1f543 : distillation case
import json

case = json.load(open("case.json"))
lines = case["files"]["logs/edge-access.log"].splitlines()

rename = {"paymentsvc": "payment-svc"}
merged = {}
outside = {}
minutes = {}
minute_detail = {}
for line in lines:
    if not line.strip():
        continue
    f = line.split()
    status = int(f[5])
    if not (500 <= status <= 599):
        continue
    ts = f[0]
    edge = rename.get(f[6], f[6])
    minute = ts[14:16]
    stamp = ts[11:16]
    merged[edge] = merged.get(edge, 0) + 1
    if not ("2026-09-26T03:14:00Z" <= ts <= "2026-09-26T03:19:59Z"):
        outside[edge] = outside.get(edge, 0) + 1
    minutes[stamp] = minutes.get(stamp, 0) + 1
    minute_detail.setdefault(stamp, {})
    minute_detail[stamp][edge] = minute_detail[stamp].get(edge, 0) + 1

top = sorted(merged.items(), key=lambda kv: (-kv[1], kv[0]))[0][0]
top_out = sorted(outside.items(), key=lambda kv: (-kv[1], kv[0]))[0][0]
peak = sorted(minutes.items(), key=lambda kv: (-kv[1], kv[0]))[0][0]
peak_top = sorted(minute_detail[peak].items(), key=lambda kv: (-kv[1], kv[0]))[0][0]

forms = [top, top_out, peak, peak_top]
print(json.dumps({"expected_contains_any": sorted(set(forms))}))
