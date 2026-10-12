# DISTILL-CANARY-0eaf77ec : distillation case
import json
case = json.load(open("case.json"))
assert case["files"] == {}
print(json.dumps({"expected_contains_any": ["饱和", "水汽", "最大"]}, ensure_ascii=False))
