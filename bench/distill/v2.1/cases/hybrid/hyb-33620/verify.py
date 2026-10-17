# DISTILL-CANARY-cd1143f7 : distillation case
import hashlib, json
case = json.load(open("case.json"))
_pin = hashlib.sha256(json.dumps({"f": case["files"], "w": case.get("weather_fixture", [])}, ensure_ascii=False, sort_keys=True).encode()).hexdigest()
assert _pin == 'c4672aac0cc1dd07d264956d2da30956c5aa0cf3006e110568b17c77d61d932a', "fixture changed"
def compute(files, wx):
    import datetime
    d, n = datetime.date(2026, 9, 16), 0
    while n < 15:
        d += datetime.timedelta(days=1)
        if d.weekday() < 5:
            n += 1
    return {}, [[("any", ["%d月%d日" % (d.month, d.day), "%d月%d号" % (d.month, d.day), d.isoformat(), "%02d-%02d" % (d.month, d.day), "%d/%d" % (d.month, d.day), "Oct 7", "October 7"])]]

FINAL, ANS = compute(dict(case["files"]), case.get("weather_fixture", []))
for path, rule in case.get("expect", {}).get("files", {}).items():
    if "equals" in rule:
        assert FINAL[path] == rule["equals"], path
    elif "contains" in rule:
        assert FINAL[path] == rule["contains"], path
    elif rule.get("unchanged"):
        assert path in case["files"] and path not in FINAL, path
flat = [x for a in ANS for x in a]
nums = [v for k, v in flat if k == "num"]
alls = [v for k, v in flat if k == "all"]
anys = [x for k, v in flat if k == "any" for x in v]
for turn, a in zip(case["turns"], ANS):
    e = turn["expect"]
    for k, v in a:
        if k == "num":
            assert abs(e["expected_number"] - v) < 1e-9
        elif k == "all":
            assert e["output_contains"] == v
        else:
            assert e["output_contains_any"] == v
if FINAL:
    print(json.dumps({"files": {k: ("\n".join(v) if isinstance(v, list) else v) for k, v in FINAL.items()}}, ensure_ascii=False))
elif nums:
    print(json.dumps({"expected_number": float(nums[0])}))
elif anys:
    print(json.dumps({"expected_contains_any": anys}, ensure_ascii=False))
else:
    print(json.dumps({"expected_string": alls[0][0]}, ensure_ascii=False))
