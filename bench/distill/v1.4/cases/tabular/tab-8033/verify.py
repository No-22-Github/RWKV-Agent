# DISTILL-CANARY-fbffc5a0 : distillation case
import csv
import io
import json

case = json.load(open("case.json"))
rows = list(csv.DictReader(io.StringIO(case["files"]["press/Aug-2026-output.csv"])))
assert rows and set(rows[0]) == {"entry", "date", "press", "shift", "sheets"}
p8 = [r for r in rows if r["press"] == "press-8"]
filled = [r for r in p8 if r["sheets"].strip()]
blank = [r for r in p8 if not r["sheets"].strip()]
assert filled and blank
assert max(r["date"] for r in filled) <= "2026-08-08"
assert min(r["date"] for r in blank) >= "2026-08-09"
assert any(r["press"] == "press-3" and r["sheets"].strip() for r in rows)
n = sum(int(r["sheets"]) for r in filled)
print(json.dumps({"expected_contains_any": list(dict.fromkeys([str(n), "{:,}".format(n)]))}))
