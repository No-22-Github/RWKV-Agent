# DISTILL-CANARY-4cf7bcfb : distillation case
import hashlib, json
case = json.load(open("case.json"))
_pin = hashlib.sha256(json.dumps(case["files"], ensure_ascii=False, sort_keys=True).encode()).hexdigest()
assert _pin == 'e0741e46a14f6eced1861c463c712b6216bc4f2d5c09876ff75ed97efa9b263c', "fixture changed"
def compute(files, web):
    import re
    pg = [w for w in web if "hengfeng" in w["url"]][0]["content"]
    rice = float(re.search(r"东北大米：([\d.]+)", pg).group(1))
    flour = float(re.search(r"特一粉）：([\d.]+)", pg).group(1))
    a = int(re.search(r"(\d+) 公斤", files["食堂/大米用量.txt"]).group(1))
    b = int(re.search(r"(\d+) 公斤", files["食堂/面粉用量.txt"]).group(1))
    x, y = round(a * rice, 2), round(b * flour, 2)
    f = lambda t: list(dict.fromkeys(["%.2f" % t, ("%.2f" % t).rstrip("0").rstrip("."), "{:,.2f}".format(t), "{:,.2f}".format(t).rstrip("0").rstrip(".")]))
    return {}, [f(x), f(y)]

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
