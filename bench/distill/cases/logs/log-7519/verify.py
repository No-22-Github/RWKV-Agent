# DISTILL-CANARY-103a54d3 : distillation case
import json
import re

case = json.load(open("case.json"))
lines = case["files"]["logs/auth-login.log"].splitlines()


def count(day, drop_jump):
    rows = []
    for line in lines:
        if "result=failed" not in line:
            continue
        f = line.split()
        if not f[0].startswith(day):
            continue
        user = re.search(r"user=(\S+)", line).group(1)
        src = re.search(r"src=(\S+)", line).group(1)
        if user == "-":
            continue
        if drop_jump and src.startswith("10.8."):
            continue
        rows.append(user)
    return rows


d27_all = count("2026-09-27", False)
d27_kept = count("2026-09-27", True)
d26_kept = count("2026-09-26", True)
accounts = {}
for u in d27_kept:
    accounts[u] = accounts.get(u, 0) + 1
top = sorted(accounts.items(), key=lambda kv: (-kv[1], kv[0]))[0][0]

forms = ["%d 次" % len(d27_all), "%d 次" % len(d27_kept), "%d 次" % len(d26_kept), top]
print(json.dumps({"expected_contains_any": sorted(set(forms))}))
