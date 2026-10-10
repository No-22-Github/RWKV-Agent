# DISTILL-CANARY-84c502ef : distillation case
import csv
import io
import json
import re

case = json.load(open("case.json"))
rows = list(csv.DictReader(io.StringIO(case["files"]["abstraction/september-2026.csv"])))
if not rows:
    raise SystemExit("the abstraction log is empty")
licences = {row["licence"] for row in rows}
if len(licences) != 1:
    raise SystemExit("the log must sit under one licence")
licence = licences.pop()
page = next(entry["content"] for entry in case["web_fixture"] if licence in entry["content"])
rate = float(re.search(r"LR-22/451 is charged at ([\d.]+) per\s+cubic metre abstracted", page).group(1))
other = float(re.search(r"LR-22/302, held in the Cranmoor catchment, is charged at ([\d.]+) per\s+cubic metre", page).group(1))
if rate == other:
    raise SystemExit("the two licences must not be charged the same")
volume = sum(int(row["volume_m3"]) for row in rows)
assert volume > 0, "the log must record some abstraction"
print(json.dumps({"expected_number": round(volume * rate, 2)}))
