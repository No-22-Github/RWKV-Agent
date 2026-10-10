# DISTILL-CANARY-2074f4ab : distillation case
import json
case = json.load(open("case.json"))
before = case["files"]["ops/site-visit.md"]
assert before.startswith("# Site visit: Shenzhen") and "Thursday 2026-09-17" in before
day = case["weather_fixture"][0]["report"]["daily"][1]
low, high = day["temp_c"].split("~")
line = "Weather: %s, %s-%s°C, %s chance of rain" % (day["condition"], low, high, day["rain_chance"])
print(json.dumps({"files": {"ops/site-visit.md": before + line + chr(10)}}, ensure_ascii=False))
