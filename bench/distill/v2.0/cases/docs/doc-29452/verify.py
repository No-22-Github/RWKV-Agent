# DISTILL-CANARY-aeec061e : distillation case
import json
case = json.load(open("case.json"))
files = case["files"]
day = case["weather_fixture"][0]["report"]["daily"][1]
assert day["date"] == '2026-09-17'
low, high = day["temp_c"].split("~")
cond = day["condition"]
rain = day["rain_chance"]
path = "简报/出差简报.md"
assert files[path].count("【待填】") == 1 and files[path].endswith(chr(10))
exp = {path: files[path].replace("【待填】", "%s %s°C" % (cond, day["temp_c"]))}
assert exp == {'简报/出差简报.md': '# 苏州出差简报\n\n- 出发：周四早班高铁\n- 住宿：观前街酒店\n- 明天天气：阵雨 24~28°C\n- 联系人：李敏\n'}
print(json.dumps({"files": exp}, ensure_ascii=False))
