# DISTILL-CANARY-d4c36f08 : distillation case
import json

with open("case.json") as handle:
    case = json.load(handle)

wanted = "drop-extra-files"
canonical = ""
accepted = []
for line in case["files"]["transfer/mirror-option-cards.tsv"].splitlines():
    if not line.strip():
        continue
    fields = line.split("\t")
    if fields[0] == wanted:
        canonical = fields[1]
        accepted = [canonical] + [part for part in fields[2].split("|") if part]
        break
print(json.dumps({'expected_contains_any': accepted}))
