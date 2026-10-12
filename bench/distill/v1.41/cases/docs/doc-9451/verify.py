# DISTILL-CANARY-36a32e4b : distillation case
import json
case = json.load(open("case.json"))
files = case["files"]
day = case["weather_fixture"][0]["report"]["daily"][1]
assert day["date"] == '2026-09-17'
low, high = day["temp_c"].split("~")
cond = day["condition"]
rain = day["rain_chance"]
path = "日志/出行日志.md"
assert files[path].startswith("# 出行日志") and files[path].endswith(chr(10)) and files[path].count(chr(10)) == 4
exp = {path: files[path] + "- %s 上海 %s %s°C" % (day["date"][5:], cond, day["temp_c"]) + chr(10)}
assert exp == {'日志/出行日志.md': '# 出行日志\n\n- 09-14 北京 晴 14~26°C\n- 09-15 北京 多云 15~25°C\n- 09-17 上海 小雨 18~24°C\n'}
print(json.dumps({"files": exp}, ensure_ascii=False))
