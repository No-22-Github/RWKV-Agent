# DISTILL-CANARY-2b8cf87b : distillation case
import json
case = json.load(open("case.json"))
fx = case["weather_fixture"][0]
day = fx["report"]["daily"][0]
assert day["date"] == '2026-09-16'
assert '漓江' not in fx["location"] and all('漓江' not in a for a in fx["aliases"])
assert case["files"]['旅行/广西.md'].startswith('# 广西行')
print(json.dumps({"expected_string": day["condition"]}, ensure_ascii=False))
