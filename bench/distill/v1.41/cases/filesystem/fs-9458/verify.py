# DISTILL-CANARY-ac6c3355 : distillation case
import json
case = json.load(open("case.json"))
files = case["files"]
day = case["weather_fixture"][0]["report"]["daily"][1]
assert day["date"] == '2026-09-17'
low, high = day["temp_c"].split("~")
cond = day["condition"]
rain = day["rain_chance"]
assert files["日报/2026-09-17.txt"] == "天气：待填" + chr(10) and files["日报/2026-09-18.txt"] == "天气：待填" + chr(10)
exp = dict(files)
exp["日报/2026-09-17.txt"] = "天气：%s %s°C" % (cond, day["temp_c"]) + chr(10)
assert exp == {'日报/2026-09-16.txt': '天气：多云 23~29°C\n', '日报/2026-09-17.txt': '天气：雷阵雨 26~32°C\n', '日报/2026-09-18.txt': '天气：待填\n'}
print(json.dumps({"files": exp}, ensure_ascii=False))
