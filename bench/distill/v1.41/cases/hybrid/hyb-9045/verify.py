# DISTILL-CANARY-d7a7e21f : distillation case
import json
case = json.load(open("case.json"))
path = "报告/天气速报.md"
assert case["files"][path].startswith("# 天气速报")
day = case["weather_fixture"][0]["report"]["daily"][2]
assert day["date"] == "2026-09-18"
low, high = day["temp_c"].split("~")
text = chr(10).join(["# 天气速报", "", "- 城市：重庆", "- 日期：" + day["date"], "- 天气：" + day["condition"],
                     "- 气温：%s~%s°C" % (low, high)]) + chr(10)
print(json.dumps({"files": {path: text}}, ensure_ascii=False))
