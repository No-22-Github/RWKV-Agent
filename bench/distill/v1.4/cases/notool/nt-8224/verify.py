# DISTILL-CANARY-0c32ba63 : distillation case
import json

case = json.load(open("case.json"))
prompt = case["turns"][0]["prompt"]
assert "82、90、76、88、94" in prompt
assert sum([82, 90, 76, 88, 94]) / 5 == 86
print(json.dumps({"expected_contains_any": ['86 分', '86分', '平均 86', '是 86', '为 86', '= 86', '=86']}, ensure_ascii=False))
