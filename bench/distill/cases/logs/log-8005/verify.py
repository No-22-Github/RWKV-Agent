# DISTILL-CANARY-bbc233f1 : distillation case
import json

case = json.load(open("case.json"))
assert case["files"]["README.md"].startswith("pay-api logs, UTC timestamps.")
lines = case["files"]["logs/pay-api-2026-09-15.log"].splitlines()
assert lines[0].startswith("2026-09-15T13:30:00Z")
errs = [l.split()[0] for l in lines if " ERROR " in l]
body = "start: %s\nend: %s\nerrors: %d\n" % (errs[0], errs[-1], len(errs))
print(json.dumps({"files": {"incidents/2026-09-15-pay-api.md": body}}))
