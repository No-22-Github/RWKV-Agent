# DISTILL-CANARY-0cebddde : distillation case
import json
case = json.load(open("case.json"))
files = case["files"]
day = case["weather_fixture"][0]["report"]["daily"][1]
assert day["date"] == '2026-09-17'
low, high = day["temp_c"].split("~")
cond = day["condition"]
rain = day["rain_chance"]
path = "笔记/出行提示.txt"
assert files[path].endswith("预报：待更新") and files[path].count(chr(10)) == 2
exp = {path: files[path].replace("待更新", "%s %s°C" % (cond, day["temp_c"]))}
assert exp == {'笔记/出行提示.txt': '1. 带身份证\n2. 带充电宝\n预报：小雨 11~17°C'}
print(json.dumps({"files": exp}, ensure_ascii=False))
