# WORKBANK-CANARY-7e2a95b4 : bank artifact, excluded from training corpora
import csv
import io
import json

case = json.load(open("case.json"))
files = case["files"]
inventory = files["devices/pumpnet_inventory.csv"]
reader = csv.DictReader(io.StringIO(inventory))
rows = list(reader)
if list(reader.fieldnames or []) != ["ward", "unit_count", "config_file", "last_reviewed"]:
    raise SystemExit("unexpected pump-network inventory header")
listed = {row["ward"]: row["config_file"] for row in rows}
target = "devices/configs/" + listed["oncology"]
answer = target if target in files else "UNKNOWN"
print(json.dumps({"expected": answer}))
