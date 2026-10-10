# DISTILL-CANARY-f42b96a0 : distillation case
import csv
import io
import json

case = json.load(open("case.json"))
rows = list(csv.DictReader(io.StringIO(case["files"]["trips_2026-q2.csv"])))
terms = case["files"]["reimbursement_terms.md"]
assert "0.62 per kilometre" in terms and "0.38 per kilometre" in terms and "25.00" in terms
trips = {r["trip_id"]: r for r in rows}
total = 0.0
for trip in trips.values():
    if trip["route_code"] == "R-7":
        total += 25.0
    elif trip["vehicle_id"].startswith("EV"):
        total += 0.38 * float(trip["distance_km"])
    else:
        total += 0.62 * float(trip["distance_km"])
print(json.dumps({"expected_number": round(total, 2)}))
