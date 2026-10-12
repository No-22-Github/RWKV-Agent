# DISTILL-CANARY-9c2ed7f1 : distillation case
import json
case = json.load(open("case.json"))
path = "出行/提示.md"
assert case["files"][path].startswith("# 出行提示")
day = case["weather_fixture"][0]["report"]["daily"][1]
assert day["date"] == "2026-09-17"
low, high = day["temp_c"].split("~")
text = chr(10).join(["# 出行提示", "", "- 城市：西宁", "- 日期：" + day["date"], "- 天气：" + day["condition"],
                     "- 气温：%s~%s°C" % (low, high)]) + chr(10)
print(json.dumps({"files": {path: text}}, ensure_ascii=False))
