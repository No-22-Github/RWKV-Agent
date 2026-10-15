# EXAM-CANARY-38981a6c : exam gap-fill case
import json

case = json.load(open("case.json", encoding="utf-8"))
prompt = " ".join(t["prompt"] for t in case["turns"]) + json.dumps(case.get("files", {}), ensure_ascii=False) + json.dumps(case.get("web_fixture", []), ensure_ascii=False)
facts = []
for f in facts:
    assert f in prompt, f
exp = case["turns"][-1]["expect"]
print(json.dumps({"expected_contains_any": exp["output_contains_any"]}, ensure_ascii=False))
