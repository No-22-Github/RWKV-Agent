# DISTILL-CANARY-474f7d5b : distillation case
import json

case = json.load(open("case.json"))
rows = case["files"]["records/loss-2026-09-30.txt"]
lines = ["- " + " ".join(r.split()) for r in rows.splitlines() if r.strip()]
print(json.dumps({"files": {"summary/2026-09-30.txt": "\n".join(lines) + "\n"}}))
