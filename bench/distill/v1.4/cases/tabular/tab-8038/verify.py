# DISTILL-CANARY-44a3a673 : distillation case
import csv
import io
import json

case = json.load(open("case.json"))
files = case["files"]
ws = list(csv.DictReader(io.StringIO(files["data/wholesale-orders-september.csv"])))
stand = list(csv.DictReader(io.StringIO(files["data/farm-stand-september.csv"])))
assert ws and list(ws[0]) == ["date", "dozens"]
assert stand and list(stand[0]) == ["date", "dozens"]
assert len(stand) == 19
stand_days = {r["date"] for r in stand}
assert stand_days == {"2026-09-" + str(d).zfill(2) for d in list(range(1, 10)) + list(range(17, 27))}
missing = {"2026-09-" + str(d).zfill(2) for d in range(10, 17)}
assert not (stand_days & missing) and len({r["date"] for r in ws}) >= 18
readme = files["data/README.md"]
assert readme.splitlines()[0].startswith("# Hollis Family Farm egg ledger")
assert "didn't transfer" in readme and "re-scanning" in readme
total = sum(int(r["dozens"]) for r in ws)
def _both(n):
    if isinstance(n, float):
        return list(dict.fromkeys(["%.2f" % n, "{:,.2f}".format(n)]))
    return list(dict.fromkeys([str(n), "{:,}".format(n)]))
print(json.dumps({"expected_contains_any": _both(total)}))
