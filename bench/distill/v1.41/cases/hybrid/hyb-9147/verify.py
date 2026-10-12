# DISTILL-CANARY-26698bf2 : distillation case
import json
case = json.load(open("case.json"))
fx = case["weather_fixture"][0]
day = fx["report"]["daily"][1]
assert day["date"] == '2026-09-17'
assert '亚龙湾' not in fx["location"] and all('亚龙湾' not in a for a in fx["aliases"])
assert case["files"]['旅行/海南.md'].startswith('# 海南行')
print(json.dumps({"expected_string": day["rain_chance"]}, ensure_ascii=False))
