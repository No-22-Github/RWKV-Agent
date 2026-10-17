# DISTILL-CANARY-ec0fd015 : distillation case
import hashlib, json
case = json.load(open("case.json"))
_pin = hashlib.sha256(json.dumps({"f": case["files"], "w": case.get("weather_fixture", [])}, ensure_ascii=False, sort_keys=True).encode()).hexdigest()
assert _pin == '190f8117f27838e5c58571d463cce127ecd34410298bc0c9bcce4cf0aa4b322f', "fixture changed"
def compute(files, wx):
    import datetime
    t = datetime.date(2026, 10, 14)
    zh = "一二三四五六日"[t.weekday()]
    en = ["Monday", "Tuesday", "Wednesday", "Thursday", "Friday", "Saturday", "Sunday"][t.weekday()]
    return {}, [[("any", ["周" + zh, "星期" + zh, "礼拜" + zh, en])]]

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
