# WEATHERPROBE-CANARY-3b9e51a2 : weatherprobe case
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
v = fact(case, '长沙', 3, 'cond')
snippet = case["web_fixture"][0]["snippet"]
want = ["20:30", "20点30", "晚上八点半", "八点半"]
assert any(w in snippet for w in want)
print(json.dumps({"expected_contains_any": want}, ensure_ascii=False))
