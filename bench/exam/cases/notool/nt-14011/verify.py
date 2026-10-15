# EXAM-CANARY-113d6863 : exam gap-fill case
import json

case = json.load(open("case.json", encoding="utf-8"))
prompt = " ".join(t["prompt"] for t in case["turns"]) + json.dumps(case.get("files", {}), ensure_ascii=False) + json.dumps(case.get("web_fixture", []), ensure_ascii=False)
# Source term -> what must survive in the Chinese translation.
facts = {"Kestrel": "Kestrel", "3.8": "3.8", "Lisbon": "里斯本"}
for source in facts:
    assert source in prompt, source
exp = case["turns"][-1]["expect"]
print(json.dumps({"expected": (exp.get("output_contains") or exp.get("output_contains_any") or exp.get("output_first_line_contains_any") or [""])[0]}, ensure_ascii=False))
