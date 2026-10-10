# DISTILL-CANARY-b443bcad : distillation case
import csv
import io
import json

case = json.load(open("case.json"))
files = case["files"]
daily = list(csv.DictReader(io.StringIO(files["data/stall-fee-collections-september.csv"])))
inv = list(csv.DictReader(io.StringIO(files["data/monthly-invoices-september.csv"])))
assert daily and list(daily[0]) == ["day", "section", "amount"]
assert inv and list(inv[0]) == ["vendor", "amount"]
days9 = {"2026-09-01", "2026-09-05", "2026-09-08", "2026-09-12", "2026-09-15",
         "2026-09-19", "2026-09-22", "2026-09-26", "2026-09-29"}
assert len(daily) == 27 and {(r["day"], r["section"]) for r in daily} == {
    (d, s) for d in days9 for s in ("produce sheds", "craft barn", "flower lane")}
assert len(inv) == 8
readme = files["data/README.md"]
assert readme.splitlines()[0].startswith("# Thistledown Market stall fees")
assert "haven't been entered" in readme and "first import" in readme
total = round(sum(float(r["amount"]) for r in daily), 2)
def _both(n):
    if isinstance(n, float):
        return list(dict.fromkeys(["%.2f" % n, "{:,.2f}".format(n)]))
    return list(dict.fromkeys([str(n), "{:,}".format(n)]))
print(json.dumps({"expected_contains_any": _both(total)}))
