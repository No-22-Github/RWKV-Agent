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

_cg = case["files"].get('logs/auth-login.log', "")
if '2026-09-26 14:16:21 att-66152 user=chen.yang src=10.8.9.1 result=failed code=mfa_failed' not in _cg:
    raise SystemExit(1)
print(json.dumps({"expected_number": len(d27_all)}))
