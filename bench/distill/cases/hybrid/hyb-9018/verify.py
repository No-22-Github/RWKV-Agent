# DISTILL-CANARY-acb86b83 : distillation case
import json
case = json.load(open("case.json"))
assert case["files"]["拍摄/通告.md"].startswith("# 外景通告")
assert "9 月 17 日" in case["files"]["拍摄/通告.md"]
day = case["weather_fixture"][0]["report"]["daily"][1]
assert day["date"] == "2026-09-17"
print(json.dumps({"expected_string": day["rain_chance"]}))
