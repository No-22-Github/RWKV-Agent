# DISTILL-CANARY-5d8c1f47 : distillation case
import csv
import io
import json

case = json.load(open("case.json"))
rows = list(csv.DictReader(io.StringIO(case["files"]["meter_export_2026-08.csv"])))
readings = [r for r in rows if r["reading_id"] != "TOTAL"]
volumes = [float(r["volume_m3"]) for r in readings]
print(json.dumps({"expected_number": round(sum(volumes) / len(volumes), 2)}))
