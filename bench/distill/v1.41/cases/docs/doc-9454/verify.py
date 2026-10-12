# DISTILL-CANARY-0c5e1ee8 : distillation case
import json
case = json.load(open("case.json"))
files = case["files"]
day = case["weather_fixture"][0]["report"]["daily"][1]
assert day["date"] == '2026-09-17'
low, high = day["temp_c"].split("~")
cond = day["condition"]
rain = day["rain_chance"]
path = "行程/行程表.md"
assert files[path].count("| 待填 | 待填 |") == 2 and files[path].endswith(chr(10))
exp = {path: files[path].replace("| 09-17 | 成都 | 待填 | 待填 |", "| 09-17 | 成都 | %s | %s°C |" % (cond, day["temp_c"]))}
assert exp == {'行程/行程表.md': '| 日期 | 城市 | 天气 | 气温 |\n| --- | --- | --- | --- |\n| 09-16 | 长沙→成都 | 阴 | 22~28°C |\n| 09-17 | 成都 | 小雨 | 20~25°C |\n| 09-18 | 成都→重庆 | 待填 | 待填 |\n'}
print(json.dumps({"files": exp}, ensure_ascii=False))
