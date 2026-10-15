# EXAM-CANARY-5e82a4c7 : sol pilot case
import csv,io,json
from collections import defaultdict
case=json.load(open("case.json",encoding="utf-8"))
totals=defaultdict(int)
for row in csv.DictReader(io.StringIO(case["files"]["inspection.csv"])):
    if row["state"]=="accepted":
        totals[row["station"]]+=int(row["units"])
lines=["station,accepted_units"]+[f"{station},{totals[station]}" for station in sorted(totals)]
print(json.dumps({"expected_stdout":"\n".join(lines)},ensure_ascii=False))
