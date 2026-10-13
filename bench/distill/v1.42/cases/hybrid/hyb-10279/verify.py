# DISTILL-CANARY-b32f6979 : distillation case
def fact(case, city, i, field):
    for e in case["weather_fixture"]:
        if e["location"] == city:
            d = e["report"]["daily"][i]
            assert d["date"] == "2026-09-%02d" % (16 + i), d
            low, high = d["temp_c"].split("~")
            return {"cond": d["condition"], "low": low, "high": high, "rain": d["rain_chance"]}[field]
    raise KeyError(city)

import json
case = json.load(open("case.json"))
v = fact(case, 'Osaka', 1, 'cond')
snippet = case["web_fixture"][0]["snippet"]
want = ["20:00", "8 pm", "8pm", "8:00 pm"]
assert any(w in snippet for w in want)
print(json.dumps({"expected_contains_any": want}, ensure_ascii=False))
