# DISTILL-CANARY-0c6e9d52 : distillation case
import json

with open("case.json") as handle:
    case = json.load(handle)

wanted = "go-back-to-the-previous-revision"
accepted = []
for line in case["files"]["deploys/rollback-cards.tsv"].splitlines():
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
