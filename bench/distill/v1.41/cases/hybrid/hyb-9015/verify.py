# DISTILL-CANARY-2b6dd7a6 : distillation case
import json
case = json.load(open("case.json"))
before = case["files"]["行程/青岛.md"]
anchor = "（示例行：- 09-01 周一 晴 20~28°C）" + chr(10)
assert before.startswith("# 青岛三日行程") and anchor in before
week = ["周三", "周四", "周五"]
rows = "".join("- %s %s %s %s°C" % (d["date"][5:], w, d["condition"], d["temp_c"]) + chr(10)
               for d, w in zip(case["weather_fixture"][0]["report"]["daily"], week))
print(json.dumps({"files": {"行程/青岛.md": before.replace(anchor, anchor + rows)}}, ensure_ascii=False))
