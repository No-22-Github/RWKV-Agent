# DISTILL-CANARY-97d6c382 : distillation case
import hashlib, json
case = json.load(open("case.json"))
_pin = hashlib.sha256(json.dumps({"f": case["files"], "w": case.get("weather_fixture", [])}, ensure_ascii=False, sort_keys=True).encode()).hexdigest()
assert _pin == 'd013504b30a33cec4b92702fd1de3635ccb0dd0ae3d53990b8879e2fa651c41d', "fixture changed"
def compute(files, wx):
    import json as j
    rs = [j.loads(l) for l in files["events.jsonl"].splitlines() if l.strip()]
    n = sum(1 for x in rs if x["service"] == "api" and x["level"] == "error")
    return {}, [[("any", ["%d条" % n, "%d 条" % n, "%d次" % n, "%d 次" % n, "%d个" % n, "%d 个" % n, "%d errors" % n, "%d error" % n])]]

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
