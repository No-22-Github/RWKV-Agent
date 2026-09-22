# WORKBANK-CANARY-7b3d1f9c : bank artifact, excluded from training corpora
import csv
import io
import json

case = json.load(open("case.json", encoding="utf-8"))
blobs = dict(case["files"])
blobs.update(case["expect"]["run"].get("hidden_files") or {})
overdue = {}
for name in sorted(blobs):
    if "tickets-" not in name or not name.endswith(".csv"):
        continue
    for row in csv.DictReader(io.StringIO(blobs[name])):
        if row["first_response_ok"] != "no":
            continue
        queue = row["queue"]
        overdue[queue] = overdue.get(queue, 0) + int(row["first_response_minutes"])
lines = ["queue,overdue_minutes"]
for queue in sorted(overdue):
    lines.append("%s,%d" % (queue, overdue[queue]))
lines.append("total,%d" % sum(overdue.values()))
print(json.dumps({"expected_stdout": "\n".join(lines)}))
