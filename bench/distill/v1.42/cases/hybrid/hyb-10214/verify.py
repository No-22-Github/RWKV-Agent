# DISTILL-CANARY-99e520fd : distillation case
import json
case = json.load(open("case.json"))

def fact(case, city, i, field):
    for e in case["weather_fixture"]:
        if e["location"] == city:
            d = e["report"]["daily"][i]
            assert d["date"] == "2026-09-%02d" % (16 + i), d
            low, high = d["temp_c"].split("~")
            return {"cond": d["condition"], "low": low, "high": high, "rain": d["rain_chance"]}[field]
    raise KeyError(city)

v = fact(case, '重庆', 0, 'rain')
print(json.dumps({"expected_string": v}, ensure_ascii=False))
