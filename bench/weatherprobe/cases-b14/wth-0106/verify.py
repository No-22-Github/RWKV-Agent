# WEATHERPROBE-CANARY-3b9e51a2 : weatherprobe case
import hashlib, json
case = json.load(open("case.json"))
_pin = hashlib.sha256(json.dumps(case["files"], ensure_ascii=False, sort_keys=True).encode()).hexdigest()
assert _pin == 'bc35fabe76f2ff64b178aa54f3d20879b529f1f5fbbc427fa383175c295c4f69', "fixture changed"
def fact(case, city, i, field):
    for e in case["weather_fixture"]:
        if e["location"] == city:
            d = e["report"]["daily"][i]
            assert d["date"] == "2026-09-%02d" % (16 + i), d
            low, high = d["temp_c"].split("~")
            return {"cond": d["condition"], "low": low, "high": high, "rain": d["rain_chance"]}[field]
    raise KeyError(city)

v = fact(case, 'Barcelona', 1, 'rain')
print(json.dumps({"expected_string": v}, ensure_ascii=False))
