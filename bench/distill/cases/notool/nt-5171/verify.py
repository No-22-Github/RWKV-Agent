# DISTILL-CANARY-6b40f2a9 : distillation case
import json

with open("case.json") as handle:
    case = json.load(handle)

wanted = "hold-until-commit"
canonical = ""
accepted = []
for line in case["files"]["sql/lock-clauses.tsv"].splitlines():
    if not line.strip():
        continue
    fields = line.split("\t")
    if fields[0] == wanted:
        canonical = fields[1]
        accepted = [canonical] + [part for part in fields[2].split("|") if part]
        break
print(json.dumps({'expected_string': canonical}))
