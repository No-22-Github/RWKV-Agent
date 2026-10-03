# DISTILL-CANARY-9964e67f : distillation case
import json

case = json.load(open("case.json"))
text = case["files"]["docs/kpi-targets.md"]
assert text.startswith("# Support KPI targets")
assert case["files"]["docs/leads.md"].startswith("Support leads:")
new = {"Q3": "| Q3 | 2 | 30 | 91 |", "Q4": "| Q4 | 2 | 28 | 92 |"}
out = []
for l in text.splitlines(keepends=True):
    for q, row in new.items():
        if l.startswith("| %s |" % q):
            l = row + "\n"
    out.append(l)
print(json.dumps({"files": {"docs/kpi-targets.md": "".join(out)}}))
