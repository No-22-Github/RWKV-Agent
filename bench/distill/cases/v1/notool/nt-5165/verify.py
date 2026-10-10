# DISTILL-CANARY-3b7ac1e4 : distillation case
import json

with open("case.json") as handle:
    case = json.load(handle)

wanted = "no-copy-at-any-stage"
canonical = ""
accepted = []
for line in case["files"]["headers/response-header-cards.tsv"].splitlines():
    if not line.strip():
        continue
    fields = line.split("\t")
    if fields[0] == wanted:
        canonical = fields[1]
        accepted = [canonical] + [part for part in fields[2].split("|") if part]
        break
print(json.dumps({'expected_contains_any': accepted}))
