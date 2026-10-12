# DISTILL-CANARY-8354ebdf : distillation case
import json
case = json.load(open("case.json"))
fx = case["weather_fixture"][0]
day = fx["report"]["daily"][2]
assert day["date"] == '2026-09-18'
assert '北戴河' not in fx["location"] and all('北戴河' not in a for a in fx["aliases"])
assert case["files"]['周末/海边.md'].startswith('# 海边小住')
print(json.dumps({"expected_string": day["temp_c"].split("~")[0]}, ensure_ascii=False))
