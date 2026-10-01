# DISTILL-CANARY-f2d377e2 : distillation case
import json

case = json.load(open("case.json"))
lines = case["files"]["logs/cdn-edge.log"].splitlines()

rename = {"qcd-hz2": "qcd-hz-b"}
errs = []
for line in lines:
    if not line.strip() or "cache=ERR" not in line:
        continue
    f = line.split()
    ts = f[0] + " " + f[1]
    edge = f[4].split("=")[1]
    errs.append((ts, rename.get(edge, edge)))

total = {}
for ts, edge in errs:
    total[edge] = total.get(edge, 0) + 1
top = sorted(total.items(), key=lambda kv: (-kv[1], kv[0]))[0][0]

after = {}
first_bj1 = ""
for ts, edge in errs:
    hhmm = ts.split(" ")[1]
    if hhmm >= "12:00:00":
        after[edge] = after.get(edge, 0) + 1
        if edge == "qcd-bj1" and not first_bj1:
            first_bj1 = hhmm
top_after = sorted(after.items(), key=lambda kv: (-kv[1], kv[0]))[0][0]

forms = [top, top_after, first_bj1, first_bj1[:5]]
print(json.dumps({"expected_contains_any": sorted(set(forms))}))
