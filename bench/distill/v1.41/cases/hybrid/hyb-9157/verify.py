# DISTILL-CANARY-ee35f8bf : distillation case
import json
case = json.load(open("case.json"))
path = "状态/天气.txt"
before = case["files"][path]
assert before.startswith("拉萨|2026-09-16") and not before.endswith(chr(10))
day = case["weather_fixture"][0]["report"]["daily"][2]
assert day["date"] == "2026-09-18"
text = "|".join(["拉萨", day["date"], day["condition"], day["temp_c"], day["rain_chance"]])
print(json.dumps({"files": {path: text}}, ensure_ascii=False))
