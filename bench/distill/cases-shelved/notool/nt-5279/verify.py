# DISTILL-CANARY-b9f5e283 : distillation case
import json

with open("case.json") as handle:
    case = json.load(handle)

wanted = "run-it-and-report-what-happened"
accepted = []
for line in case["files"]["sql/plan-prefixes.tsv"].splitlines():
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
