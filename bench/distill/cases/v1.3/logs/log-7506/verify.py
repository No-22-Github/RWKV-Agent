# DISTILL-CANARY-34717af9 : distillation case
import json

case = json.load(open("case.json"))
lines = case["files"]["logs/smtp-delivery.log"].splitlines()

window = 0
day = 0
for line in lines:
    if not line.strip():
        continue
    f = line.split()
    ts = f[0] + " " + f[1]
    if "status=deferred" not in line:
        continue
    day += 1
    if "2026-09-24 08:00:00" <= ts < "2026-09-24 09:00:00":
        window += 1

_sabotage_guard = case["files"].get('logs/smtp-delivery.log', "")
if not _sabotage_guard.splitlines() or _sabotage_guard.splitlines()[0] != '2026-09-24 07:10:22 Q-91088 rcpt=li.wen@bramblehill.cn status=deferred reason="451 4.4.1 greylisted"':
    raise SystemExit(1)
_cg = case["files"].get('logs/smtp-delivery.log', "")
if '2026-09-24 08:03:11 Q-91120 rcpt=fang.lu@bramblehill.cn status=deferred reason="451 4.4.1 greylisted"' not in _cg:
    raise SystemExit(1)
print(json.dumps({"expected_number": window}))
