# DISTILL-CANARY-cdff0eba : distillation case
import hashlib, json
case = json.load(open("case.json"))
_pin = hashlib.sha256(json.dumps({"f": case["files"], "w": case.get("weather_fixture", [])}, ensure_ascii=False, sort_keys=True).encode()).hexdigest()
assert _pin == 'aff0a96bcc4b74adfa45710be89e206b1160a5cd817c603e725089153df761a5', "fixture changed"
def compute(files, wx):
    import csv
    import io
    sy = [x for x in csv.DictReader(io.StringIO(files["climate/highs.csv"])) if x["city"] == "三亚"]
    m = max(int(x["high"]) for x in sy)
    d = [x["date"] for x in sy if int(x["high"]) == m]
    assert len(d) == 1
    y, mo, da = d[0].split("-")
    return {}, [[("any", [d[0], "%d月%d日" % (int(mo), int(da)), "%d月%d号" % (int(mo), int(da)), "%s-%s" % (mo, da), "%d/%d" % (int(mo), int(da)), "%s月%s日" % (mo, da)])]]

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
