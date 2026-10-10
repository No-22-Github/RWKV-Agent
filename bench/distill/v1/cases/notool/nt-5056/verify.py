# DISTILL-CANARY-8202e98f : distillation case
import csv
import json

with open("case.json") as handle:
    case = json.load(handle)

rows = list(csv.DictReader(case["files"]["ops/pipeline-rules.tsv"].splitlines(), delimiter="\t"))
row = [r for r in rows if r["rule"] == "pipefail"][0]
accepted = [row["canonical"]] + [part for part in row["also_accept"].split("|") if part]
print(json.dumps({"expected_contains_any": accepted}))
