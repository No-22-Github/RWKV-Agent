# DISTILL-CANARY-96bc8868 : distillation case
import json
case = json.load(open("case.json"))
report = case["weather_fixture"][0]["report"]
day = report["daily"][1]
assert case["files"]['社团/晨跑规则.md'].startswith('# 晨跑社规则')
assert day['temp_c']
print(json.dumps({"expected_contains_any": ["早上", "早晨", "6 点", "6点"]}, ensure_ascii=False))
