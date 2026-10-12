# DISTILL-CANARY-ff51f3ab : distillation case
import json
case = json.load(open("case.json"))
files = case["files"]
day = case["weather_fixture"][0]["report"]["daily"][2]
assert day["date"] == '2026-09-18'
low, high = day["temp_c"].split("~")
cond = day["condition"]
rain = day["rain_chance"]
assert files["天气/海口.txt"] == "雷阵雨" + chr(10) + "27~32°C" + chr(10)
exp = dict(files)
exp["天气/南宁.txt"] = cond + chr(10) + day["temp_c"] + "°C" + chr(10)
assert exp == {'天气/海口.txt': '雷阵雨\n27~32°C\n', '天气/南宁.txt': '晴\n25~34°C\n'}
print(json.dumps({"files": exp}, ensure_ascii=False))
