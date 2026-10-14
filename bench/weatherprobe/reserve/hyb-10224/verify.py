# WEATHERPROBE-CANARY-3b9e51a2 : weatherprobe case
import hashlib, json
case = json.load(open("case.json"))
_pin = hashlib.sha256(json.dumps(case["files"], ensure_ascii=False, sort_keys=True).encode()).hexdigest()
assert _pin == '8b7f150d9b018b847437730e41925bcc758a7cc9ab584e2b4a318abe2bc8070a', "fixture changed"
def fact(case, city, i, field):
    for e in case["weather_fixture"]:
        if e["location"] == city:
            d = e["report"]["daily"][i]
            assert d["date"] == "2026-09-%02d" % (16 + i), d
            low, high = d["temp_c"].split("~")
            return {"cond": d["condition"], "low": low, "high": high, "rain": d["rain_chance"]}[field]
    raise KeyError(city)

v = fact(case, '厦门', 1, 'cond')
print(json.dumps({"expected_string": v}, ensure_ascii=False))
