# WEATHERPROBE-CANARY-3b9e51a2 : weatherprobe case
import hashlib, json
case = json.load(open("case.json"))
_pin = hashlib.sha256(json.dumps(case["files"], ensure_ascii=False, sort_keys=True).encode()).hexdigest()
assert _pin == '6a72b331e9aaea1ee45349c71968828bf40cbe95868429417aacc60098e3993d', "fixture changed"
def fact(case, city, i, field):
    for e in case["weather_fixture"]:
        if e["location"] == city:
            d = e["report"]["daily"][i]
            assert d["date"] == "2026-09-%02d" % (16 + i), d
            low, high = d["temp_c"].split("~")
            return {"cond": d["condition"], "low": low, "high": high, "rain": d["rain_chance"]}[field]
    raise KeyError(city)

v = fact(case, '贵阳', 1, 'low')
print(json.dumps({"expected_number": int(v)}))
