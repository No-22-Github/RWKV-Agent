# DISTILL-CANARY-71a3cd37 : distillation case
import csv
import json

with open("case.json") as handle:
    case = json.load(handle)

rows = list(csv.DictReader(case["files"]["test/suite-options.tsv"].splitlines(),
                          delimiter="\t", quoting=csv.QUOTE_NONE))
row = [r for r in rows if r["need"] == "slowest-phases"][0]
print(json.dumps({"expected_string": row["canonical"]}))
