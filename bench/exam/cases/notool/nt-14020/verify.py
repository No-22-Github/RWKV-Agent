# EXAM-CANARY-37c3a611 : exam gap-fill case
import json

case = json.load(open("case.json", encoding="utf-8"))
prompt = " ".join(t["prompt"] for t in case["turns"]) + json.dumps(case.get("files", {}), ensure_ascii=False) + json.dumps(case.get("web_fixture", []), ensure_ascii=False)
facts = []
for f in facts:
    assert f in prompt, f
exp = case["turns"][-1]["expect"]
print(json.dumps({"expected": (exp.get("output_contains") or exp.get("output_contains_any") or exp.get("output_first_line_contains_any") or [""])[0]}, ensure_ascii=False))
