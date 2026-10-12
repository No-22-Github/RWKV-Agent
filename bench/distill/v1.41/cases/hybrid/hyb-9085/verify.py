# DISTILL-CANARY-a401ed57 : distillation case
import json
case = json.load(open("case.json"))
report = case["weather_fixture"][0]["report"]
day = report["daily"][1]
assert case["files"]['球馆/开放规定.md'].startswith('# 室外球场开放规定')
assert case["files"]['球馆/说明.md'].startswith("# 说明")
assert day['temp_c']
print(json.dumps({"expected_contains_any": ["不开放", "不开", "关闭", "只开室内"]}, ensure_ascii=False))
