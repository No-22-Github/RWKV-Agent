# DISTILL-CANARY-dcfdcc51 : distillation case
import hashlib, json
case = json.load(open("case.json"))
_pin = hashlib.sha256(json.dumps(case["files"], ensure_ascii=False, sort_keys=True).encode()).hexdigest()
assert _pin == 'e88f2f120ce6f9f437e6c39f196269d20514c8e25ae2b66c3a88d7e3d7011a31', "fixture changed"
def compute(files, web):
    ex = [l.split(",")[0] for l in files["会员/订阅.csv"].splitlines()[1:] if l.split(",")[2] < "2026-09-16"]
    return {"会员/已到期.txt": "".join(u + "\n" for u in ex)}, [[str(len(ex))]]

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
