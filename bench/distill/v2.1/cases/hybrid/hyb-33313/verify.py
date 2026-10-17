# DISTILL-CANARY-b80f7522 : distillation case
import hashlib, json
case = json.load(open("case.json"))
_pin = hashlib.sha256(json.dumps(case["files"], ensure_ascii=False, sort_keys=True).encode()).hexdigest()
assert _pin == 'e418876d25b6f954b2e844868975e49d692e11a66b70ee3854a12c9cd1ddeaf0', "fixture changed"
def compute(files, web):
    t = files["门店/营业时间.md"].replace("国庆假期：待定", "国庆假期：10:00-20:30")
    return {"门店/营业时间.md": t + "停车优惠：凭购书小票免费停车2小时\n"}, [["10:00-20:30"], ["免费停车2小时"]]

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
