# DISTILL-CANARY-d65fb820 : distillation case
import hashlib, json
case = json.load(open("case.json"))
_pin = hashlib.sha256(json.dumps(case["files"], ensure_ascii=False, sort_keys=True).encode()).hexdigest()
assert _pin == '41b06037b6e855434efc6308c9dcddbade55801c608eb9ced39f1f529582a6af', "fixture changed"
def compute(files, web):
    import re
    pg = [w for w in web if "binhai-hr" in w["url"]][0]["content"]
    c = re.search(r"上限：(\d+)", pg).group(1)
    f = re.search(r"下限：(\d+)", pg).group(1)
    t = files["payroll/params.ini"].replace("base_cap = 21800", "base_cap = " + c).replace("base_floor = 3980", "base_floor = " + f)
    return {"payroll/params.ini": t}, [[c, f]]

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
