# DISTILL-CANARY-a55193ff : distillation case
import csv
import io
import json

case = json.load(open("case.json"))
entries = dict(case["files"])
entries.update(case["expect"]["run"]["hidden_files"])

rows = []
for name in sorted(entries):
    if not name.startswith("sessions/") or not name.endswith(".csv"):
        continue
    if "/" in name[len("sessions/"):]:
        continue
    rows.extend(csv.DictReader(io.StringIO(entries[name])))
lines = []
for row in sorted(rows, key=lambda r: (r["session_date"], r["session_id"])):
    if row["state"] == "open":
        lines.append(f"{row['session_id']},{row['session_date']},{row['rink']},{row['state']},{row['pence']}")

print(json.dumps({"expected_stdout": "\n".join(lines)}))
