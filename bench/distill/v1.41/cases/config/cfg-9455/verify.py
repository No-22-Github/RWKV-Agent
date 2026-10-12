# DISTILL-CANARY-7bac5e1a : distillation case
import json
case = json.load(open("case.json"))
files = case["files"]
day = case["weather_fixture"][0]["report"]["daily"][1]
assert day["date"] == '2026-09-17'
low, high = day["temp_c"].split("~")
cond = day["condition"]
rain = day["rain_chance"]
path = "配置/trip.env"
assert "TRIP_DATE=2026-09-17" in files[path] and files[path].count("=" + chr(10)) == 3
exp = {path: files[path].replace("TRIP_WEATHER=" + chr(10), "TRIP_WEATHER=" + cond + chr(10)).replace("TRIP_LOW=" + chr(10), "TRIP_LOW=" + low + chr(10)).replace("TRIP_HIGH=" + chr(10), "TRIP_HIGH=" + high + chr(10))}
assert exp == {'配置/trip.env': 'TRIP_CITY=杭州\nTRIP_DATE=2026-09-17\nTRIP_WEATHER=多云\nTRIP_LOW=20\nTRIP_HIGH=27\nTRIP_OWNER=ops\n'}
print(json.dumps({"files": exp}, ensure_ascii=False))
