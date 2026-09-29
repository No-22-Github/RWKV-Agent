# DISTILL-CANARY-5b0ac2ee : distillation case
import json

with open("case.json") as handle:
    case = json.load(handle)

wanted = "pull-in-and-stay-down-if-the-store-fails"
accepted = []
for line in case["files"]["units/dependency-cards.tsv"].splitlines():
    if not line.strip():
        continue
    fields = line.split("\t")
    if fields[0] == wanted:
        accepted = [fields[1]]
        if len(fields) > 2:
            accepted += [part for part in fields[2].split("|") if part]
        break
if not accepted:
    raise SystemExit("no card row for " + wanted)
print(json.dumps({'expected_contains_any': accepted}))
