# DISTILL-CANARY-9f24d0a6 : distillation case
import json

with open("case.json") as handle:
    case = json.load(handle)

wanted = "save-to-disk"
canonical = ""
accepted = []
for line in case["files"]["headers/download-header-cards.tsv"].splitlines():
    if not line.strip():
        continue
    fields = line.split("\t")
    if fields[0] == wanted:
        canonical = fields[1]
        accepted = [canonical] + [part for part in fields[2].split("|") if part]
        break
print(json.dumps({'expected_contains_any': accepted}))
