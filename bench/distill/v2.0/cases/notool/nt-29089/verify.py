# DISTILL-CANARY-d2c381d1 : distillation case
import json
case = json.load(open("case.json"))
assert case["turns"][0]["prompt"]
print(json.dumps({"expected_contains_any": ["露点", "水汽", "饱和"]}, ensure_ascii=False))
