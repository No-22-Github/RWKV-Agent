# DISTILL-CANARY-05a3d6f8 : distillation case
import csv
import io
import json

case = json.load(open("case.json"))
transfers = list(csv.DictReader(io.StringIO(case["files"]["transfers-2026-09.csv"])))
store = list(csv.DictReader(io.StringIO(case["files"]["storefront-2026-09.csv"])))
for name, text in (("storefront", case["files"]["storefront-2026-09.csv"]),
                   ("transfers", case["files"]["transfers-2026-09.csv"])):
    first = text.splitlines()[0] if text.splitlines() else ""
    if not first.startswith("date,"):
        raise SystemExit("fixture shape changed: %s header missing" % name)
out = {
    "expected_number": sum(int(r["copies"]) for r in transfers),
    "expected_turn_2": sum(int(r["copies"]) for r in store),
}
print(json.dumps(out))
