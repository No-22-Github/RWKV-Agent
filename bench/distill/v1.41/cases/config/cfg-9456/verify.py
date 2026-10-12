# DISTILL-CANARY-a4121496 : distillation case
import json
case = json.load(open("case.json"))
files = case["files"]
day = case["weather_fixture"][0]["report"]["daily"][2]
assert day["date"] == '2026-09-18'
low, high = day["temp_c"].split("~")
cond = day["condition"]
rain = day["rain_chance"]
path = "站点/status.yaml"
assert "  date: 2026-09-18" in files[path] and "  condition: unknown" in files[path]
exp = {path: files[path].replace("condition: unknown", "condition: " + cond).replace("low: 0", "low: " + low).replace("high: 0", "high: " + high).replace("rain_chance: 0", "rain_chance: " + rain.rstrip("%"))}
assert exp == {'站点/status.yaml': 'site: 青岛海滩\nforecast:\n  date: 2026-09-18\n  condition: 多云\n  low: 18\n  high: 24\n  rain_chance: 40\nowner: ops\n'}
print(json.dumps({"files": exp}, ensure_ascii=False))
