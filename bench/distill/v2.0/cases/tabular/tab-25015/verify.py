# DISTILL-CANARY-4a1e7302 : distillation case
import csv
import io
import json

case = json.load(open("case.json"))
def deliveries(name):
    rows = list(csv.DictReader(io.StringIO(case["files"][name])))
    return [r for r in rows if r["entry_id"] != "TOTAL"]

june = deliveries("crate_log_2026-06.csv")
july = deliveries("crate_log_2026-07.csv")
assert {r["entry_date"][:7] for r in june} == {"2026-06"}
print(json.dumps({"expected_number": len(july)}))
