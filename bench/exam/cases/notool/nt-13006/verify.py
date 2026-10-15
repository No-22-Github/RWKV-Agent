# EXAM-CANARY-31ef0340 : exam gap-fill case
import json

case = json.load(open("case.json", encoding="utf-8"))
exp = case["turns"][0]["expect"]
print(json.dumps({"expected_contains_any": exp.get("output_contains_any") or []}, ensure_ascii=False))
