# DISTILL-CANARY-9575d7f9 : distillation case
import hashlib, json
case = json.load(open("case.json"))
_pin = hashlib.sha256(json.dumps(case["files"], ensure_ascii=False, sort_keys=True).encode()).hexdigest()
assert _pin == '9a331d1746b5b6d69f0756c80c593a46ff1be1f37fd2bac6c3b9a12ad8ccd715', "fixture changed"
def compute(files, web):
    import re
    pg = [w for w in web if "fuelwatch" in w["url"]][0]["content"]
    price = float(re.search(r"95号汽油：([\d.]+)", pg).group(1))
    km = sum(int(x) for x in re.findall(r"(\d+) 公里", files["车队/本月行程.txt"]))
    v = round(km * 8.5 / 100 * price, 2)
    return {}, [list(dict.fromkeys(["%.2f" % v, ("%.2f" % v).rstrip("0").rstrip("."), "{:,.2f}".format(v)]))]

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
