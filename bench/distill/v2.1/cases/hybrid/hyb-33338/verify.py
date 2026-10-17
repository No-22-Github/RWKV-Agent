# DISTILL-CANARY-bb403b02 : distillation case
import hashlib, json
case = json.load(open("case.json"))
_pin = hashlib.sha256(json.dumps(case["files"], ensure_ascii=False, sort_keys=True).encode()).hexdigest()
assert _pin == '50be332855b88d80576fb0d169b743d10101ca125f4f075f61ed59b217937620', "fixture changed"
def compute(files, web):
    import re
    fares = [w for w in web if "koyo" in w["url"]][0]["content"]
    a = int(re.search(r"Adult one-way[^:]*: ([\d,]+) JPY", fares).group(1).replace(",", ""))
    c = int(re.search(r"Child one-way: ([\d,]+) JPY", fares).group(1).replace(",", ""))
    rate = int(re.search(r"1 USD = (\d+) JPY", [w for w in web if "tradedesk" in w["url"]][0]["content"]).group(1))
    yen = (4 * a + 2 * c) * 2
    usd = round(yen / rate, 2)
    return {}, [list(dict.fromkeys(["%.2f" % usd, ("%.2f" % usd).rstrip("0").rstrip(".")]))]

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
