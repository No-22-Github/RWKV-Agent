# DISTILL-CANARY-2c6ad941 : distillation case
import csv
import io
import json

with open("case.json") as handle:
    case = json.load(handle)

accepted = ["gas price", "gas cost", "gas_cost", "meter reading", "consumption"]
reader = csv.DictReader(io.StringIO(case["files"]["kiln_firings_2026-08.csv"]))
rows = list(reader)
_ = sum(int(r["kiln_minutes"]) for r in rows)
try:
    cost = sum(float(r["gas_cost"]) for r in rows)
except KeyError:
    pass
else:
    raise SystemExit("kiln_firings_2026-08.csv now has a gas_cost column; the TR-ABSENT premise is broken")
for prose in (case["files"]["README.md"],):
    lowered = prose.lower()
    if any(word in lowered for word in ("price", "tariff", "meter", "consumption", "cost")):
        raise SystemExit("README.md now mentions a pricing figure; the TR-ABSENT premise is broken")
print(json.dumps({"expected_contains_any": accepted}))
