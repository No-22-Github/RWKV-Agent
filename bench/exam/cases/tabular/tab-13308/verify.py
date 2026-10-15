# EXAM-CANARY-9be3d206 : exam gap-fill case
import json, re, csv, io
case = json.load(open("case.json", encoding="utf-8"))
rows = [json.loads(l) for l in case["files"]["orders.jsonl"].splitlines() if l.strip()]
print(json.dumps({"expected": sum(1 for r in rows if r["date"][:7] == "2026-08" and r["pay"] == "gift_card" and r["country"] == "CA" and r["status"] == "shipped")}))
