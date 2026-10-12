# DISTILL-CANARY-4e2b8a45 : distillation case
import json
case = json.load(open("case.json"))
day = case["weather_fixture"][0]["report"]["daily"][2]
assert day["date"] == '2026-09-18' and day["condition"] == '大雾'
assert case["files"]['旅行/黄山.md'].startswith('# 黄山行')
snippet = case["web_fixture"][0]["snippet"]
assert '80' in snippet
print(json.dumps({'expected_string': '80'}, ensure_ascii=False))
