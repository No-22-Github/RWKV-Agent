# DISTILL-CANARY-cc16ee54 : distillation case
import hashlib, json
case = json.load(open("case.json"))
_pin = hashlib.sha256(json.dumps({"f": case["files"], "w": case.get("weather_fixture", [])}, ensure_ascii=False, sort_keys=True).encode()).hexdigest()
assert _pin == '185c7ac484788d013058540d9ef68db4051142bfaa15e40721d55a4d80ceef8c', "fixture changed"
def compute(files, wx):
    import csv
    import io
    t = {}
    for x in csv.DictReader(io.StringIO(files["orders/categories.csv"])):
        t[x["category"]] = t.get(x["category"], 0) + int(x["amount"])
    n = sum(1 for v in t.values() if v > 11000)
    return {}, [[("num", t["图书"])], [("any", ["%d个" % n, "%d 个" % n, "%d类" % n, "%d 类" % n, "%d种" % n, "%d 种" % n, "%d 个品类" % n])]]

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
