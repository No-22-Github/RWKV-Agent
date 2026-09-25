# DISTILL-CANARY-d18c56f2 : distillation case
import csv
import io
import json

case = json.load(open("case.json"))
rows = {row["room"]: row for row in csv.DictReader(io.StringIO(case["files"]["tariff/room-rates-2026.csv"]))}
if "double" not in rows:
    raise SystemExit("the room card carries no double room")
rate = int(rows["double"]["low_season"])
high = int(rows["double"]["high_season"])
assert rate != high, "the answer must differ from the high season figure"
print(json.dumps({"expected_number": rate}))
