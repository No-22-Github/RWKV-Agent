# DISTILL-CANARY-6304095f : distillation case
import csv
import json

with open("case.json") as handle:
    case = json.load(handle)

rows = list(csv.DictReader(case["files"]["schedule/pan-tasks.tsv"].splitlines(),
                          delimiter="\t", quoting=csv.QUOTE_NONE))
row = [r for r in rows if r["need"] == "brine-recycle"][0]
print(json.dumps({"expected_string": row["canonical"]}))
