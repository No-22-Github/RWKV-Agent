# DISTILL-CANARY-da41185c : distillation case
import json
case = json.load(open("case.json"))
assert case["files"]["周末/想法.md"].startswith("# 周末想法")
sat = case["weather_fixture"][0]["report"]["daily"][3]
title = case["web_fixture"][0]["snippet"].split("「")[1].split("」")[0]
assert sat["date"] == "2026-09-19"
print(json.dumps({"expected_string": sat["condition"] + " " + title}, ensure_ascii=False))
