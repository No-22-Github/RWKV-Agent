# DISTILL-CANARY-39103b31 : distillation case
import json
case = json.load(open("case.json"))
files = case["files"]
day = case["weather_fixture"][0]["report"]["daily"][0]
assert day["date"] == '2026-09-16'
low, high = day["temp_c"].split("~")
cond = day["condition"]
rain = day["rain_chance"]
path = "提醒/今日提醒.txt"
assert files[path] == "出门带伞" + chr(10)
exp = {path: "武汉今天：%s" % cond + chr(10) + "气温 %s°C，降水概率 %s" % (day["temp_c"], rain) + chr(10)}
assert exp == {'提醒/今日提醒.txt': '武汉今天：多云\n气温 21~30°C，降水概率 20%\n'}
print(json.dumps({"files": exp}, ensure_ascii=False))
