# DISTILL-CANARY-a80ab7ca : distillation case
import csv
import io
import json

with open("case.json") as handle:
    case = json.load(handle)

accepted = ["damage", "damage_crates"]
reader = csv.DictReader(io.StringIO(case["files"]["deliveries_2026-08.csv"]))
rows = list(reader)
_ = sum(int(r["crates"]) for r in rows)
fields = reader.fieldnames or []
damage_fields = [f for f in fields if "damage" in f.lower()]
if damage_fields:
    raise SystemExit("deliveries_2026-08.csv now carries a damage field: " + ", ".join(damage_fields))
if "damage" in case["files"]["README.md"].lower():
    raise SystemExit("README.md now mentions damage; the TR-ABSENT premise is broken")
print(json.dumps({"expected_contains_any": accepted}))
