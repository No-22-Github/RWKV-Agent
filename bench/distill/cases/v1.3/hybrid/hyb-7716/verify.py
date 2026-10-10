# DISTILL-CANARY-a4680f3d : distillation case
import csv
import io
import json

case = json.load(open("case.json"))
aug = case["files"]["site/delays-2026-08.csv"]
sep = case["files"]["site/delays-2026-09.csv"]
for name, text in (("2026-08", aug), ("2026-09", sep)):
    first = text.splitlines()[0] if text.splitlines() else ""
    if not first.startswith("site,"):
        raise SystemExit("fixture shape changed: %s header missing" % name)
rows = list(csv.DictReader(io.StringIO(sep)))
out = {
    "expected_number": sum(int(r["delay_days"]) for r in rows),
    "expected_turn_3": sum(int(r["delay_days"]) for r in rows if r["cause"] == "weather"),
}
print(json.dumps(out))
