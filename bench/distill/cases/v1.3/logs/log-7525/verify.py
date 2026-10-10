# DISTILL-CANARY-66d4dcb7 : distillation case
import json
from datetime import datetime, timezone

case = json.load(open("case.json"))
lines = case["files"]["logs/auth-login.log"].splitlines()


def utc(ts):
    return datetime.fromisoformat(ts.replace("Z", "+00:00")).astimezone(timezone.utc)


failed = []
for line in lines:
    if "result=failed" not in line:
        continue
    f = line.split()
    row = {
        "ts": utc(f[0]),
        "node": f[4].split("=")[1],
        "endpoint": f[5].split("=")[1],
    }
    failed.append(row)

w1 = sum(1 for r in failed if datetime(2026, 9, 28, 13, 0, tzinfo=timezone.utc) <= r["ts"] < datetime(2026, 9, 28, 14, 0, tzinfo=timezone.utc))
day = {}
for r in failed:
    day[r["node"]] = day.get(r["node"], 0) + 1
top_day = sorted(day.items(), key=lambda kv: (-kv[1], kv[0]))[0][0]
v2 = sum(1 for r in failed if r["node"] == top_day and r["endpoint"] == "/v2/login")
biz = {}
for r in failed:
    if datetime(2026, 9, 28, 8, 0, tzinfo=timezone.utc) <= r["ts"] < datetime(2026, 9, 28, 20, 0, tzinfo=timezone.utc):
        biz[r["node"]] = biz.get(r["node"], 0) + 1
top_biz = sorted(biz.items(), key=lambda kv: (-kv[1], kv[0]))[0][0]
last = max(r["ts"] for r in failed if r["node"] == top_biz)

_cg = case["files"].get('logs/auth-login.log', "")
if '2026-09-28T13:11:38Z att-88141 user=ivy.zhao src=180.168.3.4 node=auth-cn-3 endpoint=/v1/login result=failed code=locked_out' not in _cg:
    raise SystemExit(1)
print(json.dumps({"expected_number": w1}))
