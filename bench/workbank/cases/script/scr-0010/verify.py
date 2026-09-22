# WORKBANK-CANARY-c52e8a40 : bank artifact, excluded from training corpora
import csv
import io
import json

case = json.load(open("case.json", encoding="utf-8"))
blobs = dict(case["files"])
blobs.update(case["expect"]["run"].get("hidden_files") or {})
cases = {}
for row in csv.DictReader(io.StringIO(blobs["data/raw_2026.csv"])):
    line = row["line"]
    cases[line] = cases.get(line, 0) + int(row["cases_ok"])
for row in csv.DictReader(io.StringIO(blobs["data/adjustments.csv"])):
    line = row["line"]
    cases[line] = cases.get(line, 0) + int(row["delta_cases"])
lines = ["line,cases"]
for line in sorted(cases):
    lines.append("%s,%d" % (line, cases[line]))
lines.append("total,%d" % sum(cases.values()))
print(json.dumps({"expected_stdout": "\n".join(lines)}))
