# DISTILL-CANARY-1d67a09c : distillation case
import json
case = json.load(open("case.json"))
assert case["turns"][0]["prompt"]
print(json.dumps({"expected_contains_any": ["比热", "海水", "水的"]}, ensure_ascii=False))
