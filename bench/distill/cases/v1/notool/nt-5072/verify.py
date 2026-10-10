# DISTILL-CANARY-edd7bf10 : distillation case
import csv
import json

with open("case.json") as handle:
    case = json.load(handle)

rows = list(csv.DictReader(case["files"]["test/selection-options.tsv"].splitlines(),
                          delimiter="\t", quoting=csv.QUOTE_NONE))
row = [r for r in rows if r["need"] == "skip-slow"][0]
accepted = [row["canonical"]] + [part for part in row["also_accept"].split("|") if part]
print(json.dumps({"expected_contains_any": accepted}))
