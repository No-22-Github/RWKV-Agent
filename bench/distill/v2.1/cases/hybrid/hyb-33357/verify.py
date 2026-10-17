# DISTILL-CANARY-969f4e11 : distillation case
import hashlib, json
case = json.load(open("case.json"))
_pin = hashlib.sha256(json.dumps(case["files"], ensure_ascii=False, sort_keys=True).encode()).hexdigest()
assert _pin == '87adbe9df249355ac9a48c34785187abf4821523bc551f352eb3c4c24363d357', "fixture changed"
def compute(files, web):
    import re
    rate = float(re.search(r"美元/人民币：([\d.]+)", web[0]["content"]).group(1))
    usd = int(re.search(r"金额：(\d+) 美元", files["财务/invoice_us.txt"]).group(1))
    v = round(usd * rate, 2)
    return {"财务/折算.txt": "折算金额=%d\n" % round(v)}, [[str(int(round(v))), "{:,}".format(int(round(v)))]]

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
