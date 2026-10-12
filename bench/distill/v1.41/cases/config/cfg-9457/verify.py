# DISTILL-CANARY-7e063224 : distillation case
import json
case = json.load(open("case.json"))
files = case["files"]
day = case["weather_fixture"][0]["report"]["daily"][1]
assert day["date"] == '2026-09-17'
low, high = day["temp_c"].split("~")
cond = day["condition"]
rain = day["rain_chance"]
path = "配置/app.toml"
assert files[path].count('= ""') == 2 and files[path].endswith(chr(10))
exp = {path: files[path].replace('condition = ""', 'condition = "' + cond + '"').replace('range = ""', 'range = "' + day["temp_c"] + '"')}
assert exp == {'配置/app.toml': '[app]\nname = "gateway"\nport = 8080\n\n[forecast]\ncity = "大连"\ncondition = "晴"\nrange = "17~23"\n\n[log]\nlevel = "info"\n'}
print(json.dumps({"files": exp}, ensure_ascii=False))
