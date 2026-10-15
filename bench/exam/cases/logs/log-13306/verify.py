# EXAM-CANARY-07d9a5b2 : exam gap-fill case
import json, re, csv, io
case = json.load(open("case.json", encoding="utf-8"))
rows = [json.loads(l) for l in case["files"]["api-access.jsonl"].splitlines() if l.strip()]
print(json.dumps({"expected": len({r["user"] for r in rows if r["status"] == 429 and r["path"] == "/v2/export"})}))
