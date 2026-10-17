# DISTILL-CANARY-b9bc35b8 : distillation case
import hashlib, json
case = json.load(open("case.json"))
_pin = hashlib.sha256(json.dumps(case["files"], ensure_ascii=False, sort_keys=True).encode()).hexdigest()
assert _pin == 'ee57378c194394d659f6101cdc206ddf507835bf29349e740586761d8709e1a2', "fixture changed"
def compute(files, web):
    import re
    pg = [w for w in web if "tianhe-bank" in w["url"]][0]["content"]
    rate = float(re.search(r"欧元/人民币：([\d.]+)", pg).group(1))
    tot = sum(int(l.split(",")[2]) for l in files["采购/欧洲订单.csv"].splitlines()[1:]) * rate
    tot = round(tot, 2)
    v = ["%.2f" % tot, ("%.2f" % tot).rstrip("0").rstrip("."), "{:,.2f}".format(tot), "{:,.0f}".format(tot) if tot == int(tot) else "{:,.2f}".format(tot)]
    return {}, [list(dict.fromkeys(v))]

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
