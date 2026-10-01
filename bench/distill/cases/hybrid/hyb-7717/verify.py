# DISTILL-CANARY-e09c52b6 : distillation case
import csv
import io
import json

case = json.load(open("case.json"))
rows = list(csv.DictReader(io.StringIO(case["files"]["tests/germination-2026q3.csv"])))
sums, counts = {}, {}
for r in rows:
    b = r["batch"]
    sums[b] = sums.get(b, 0.0) + float(r["rate"])
    counts[b] = counts.get(b, 0) + 1
out = {
    "expected_number": round(sums["BT-2201"] / counts["BT-2201"], 2),
    "expected_turn_3": round(sums["BT-2201"] / counts["BT-2201"] - sums["BT-2210"] / counts["BT-2210"], 2),
    "expected_turn_4": counts["BT-2210"],
}
print(json.dumps(out))
