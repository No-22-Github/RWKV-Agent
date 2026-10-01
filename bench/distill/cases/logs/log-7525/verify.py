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

forms = ["%d failed" % w1, "%d logins" % w1,
         top_day, "%d failed" % v2, "%d were" % v2,
         top_biz, last.strftime("%H:%M"), last.strftime("%H:%M:%S")]
print(json.dumps({"expected_contains_any": sorted(set(forms))}))
