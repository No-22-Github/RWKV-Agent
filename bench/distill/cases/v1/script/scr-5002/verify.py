# DISTILL-CANARY-4b7e9c22 : distillation case
import csv
import io
import json

case = json.load(open("case.json"))
files = case["files"]
hidden = case["expect"]["run"]["hidden_files"]

rows = list(csv.DictReader(io.StringIO(files["jobs/2026-09.csv"])))
rows += list(csv.DictReader(io.StringIO(hidden["jobs/2026-10.csv"])))


def pounds(pence):
    return "%d.%02d" % (pence // 100, pence % 100)


total = 0
lines = []
for row in sorted(rows, key=lambda r: r["job_id"]):
    cost = int(row["sheet_count"]) * int(row["rate_pence"]) + int(row["ink_ml"])
    total += cost
    lines.append("%s,%s,%s" % (row["job_id"], row["client"], pounds(cost)))
lines.append("TOTAL,%s" % pounds(total))

print(json.dumps({
    "expected_stdout": "\n".join(lines),
    "files": {"jobs/2026-09.csv": files["jobs/2026-09.csv"]},
}))
