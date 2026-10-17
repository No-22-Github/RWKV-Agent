# DISTILL-CANARY-94cc3330 : distillation case
import hashlib, json
case = json.load(open("case.json"))
_pin = hashlib.sha256(json.dumps(case["files"], ensure_ascii=False, sort_keys=True).encode()).hexdigest()
assert _pin == 'e642d81ced5e0cf92bf3d409e78c8dd102361c5ca49d8d40936f5d989567c1a0', "fixture changed"
def compute(files, web):
    import re
    pg = [w for w in web if "labor.state" in w["url"]][0]["content"]
    m = {"weekday": float(re.search(r"Weekday overtime: ([\d.]+)", pg).group(1)), "weekend": float(re.search(r"Weekend overtime: ([\d.]+)", pg).group(1))}
    base = int(re.search(r"\$(\d+)", files["hr/rate.txt"]).group(1))
    t = sum(int(l.split(",")[2]) * base * m[l.split(",")[1]] for l in files["hr/ot_log.csv"].splitlines()[1:])
    t = round(t, 2)
    return {}, [list(dict.fromkeys(["%.2f" % t, ("%.2f" % t).rstrip("0").rstrip("."), "{:,.2f}".format(t)]))]

FINAL, ANS = compute(dict(case["files"]), case["web_fixture"])
for path, rule in case["expect"]["files"].items():
    if "equals" in rule:
        assert FINAL[path] == rule["equals"], path
    elif "contains" in rule:
        assert all(s in FINAL[path] for s in rule["contains"]), path
    elif rule.get("unchanged"):
        assert path in case["files"] and path not in FINAL, path
for turn, a in zip(case["turns"], ANS):
    e = turn["expect"]
    assert set(a) <= set(e.get("output_contains", [])) | set(e.get("output_contains_any", [])), a
print(json.dumps({"files": {k: v for k, v in FINAL.items() if k in case["expect"]["files"]}, "answers": ANS}, ensure_ascii=False))
