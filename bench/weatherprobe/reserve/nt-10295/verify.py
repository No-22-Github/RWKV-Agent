# WEATHERPROBE-CANARY-3b9e51a2 : weatherprobe case
import json
case = json.load(open("case.json"))
assert case["turns"][0]["prompt"].strip()
print(json.dumps({"expected_contains_any": ["雾灯", "减速", "车距"]}, ensure_ascii=False))
