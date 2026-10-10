# DISTILL-CANARY-c453e131 : distillation case
import csv
import io
import json

case = json.load(open("case.json"))
files = case["files"]
card = list(csv.DictReader(io.StringIO(files["data/card-takings-september.csv"])))
mob = list(csv.DictReader(io.StringIO(files["data/mobile-reader-september.csv"])))
assert card and list(card[0]) == ["day", "terminal", "gross"]
assert mob and list(mob[0]) == ["day", "gross"]
days9 = {"2026-09-01", "2026-09-05", "2026-09-08", "2026-09-12", "2026-09-15",
         "2026-09-19", "2026-09-22", "2026-09-26", "2026-09-29"}
assert len(card) == 18 and {(r["day"], r["terminal"]) for r in card} == {
    (d, t) for d in days9 for t in ("T1", "T2")}
assert len(mob) == 6 and {r["day"] for r in mob} == {
    "2026-09-01", "2026-09-05", "2026-09-08", "2026-09-12", "2026-09-15", "2026-09-19"}
readme = files["data/README.md"]
assert readme.splitlines()[0].startswith("# Thistledown Market card takings")
assert "haven't been exported" in readme and "migration" in readme
total = round(sum(float(r["gross"]) for r in card), 2)
def _both(n):
    if isinstance(n, float):
        return list(dict.fromkeys(["%.2f" % n, "{:,.2f}".format(n)]))
    return list(dict.fromkeys([str(n), "{:,}".format(n)]))
print(json.dumps({"expected_contains_any": _both(total)}))
