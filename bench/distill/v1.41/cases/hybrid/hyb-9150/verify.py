# DISTILL-CANARY-44443511 : distillation case
import json
case = json.load(open("case.json"))
fx = case["weather_fixture"][0]
day = fx["report"]["daily"][2]
assert day["date"] == '2026-09-18'
assert '外滩' not in fx["location"] and all('外滩' not in a for a in fx["aliases"])
assert case["files"]['旅行/上海.md'].startswith('# 上海行')
print(json.dumps({"expected_string": day["temp_c"].split("~")[1]}, ensure_ascii=False))
