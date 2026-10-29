# DISTILL-CANARY-55d88ff0 : distillation case
import hashlib, json
case = json.load(open("case.json"))
_pin = hashlib.sha256(json.dumps(case["files"], ensure_ascii=False, sort_keys=True).encode()).hexdigest()
assert _pin == '072f1c390e3ca234825cc53b73c094608a33ddc02e1bf259cdd95af6fce8db79', "fixture changed"
rules = {'inv/库存-0916.csv': ['has', ['A-100,12,20,18', 'C-300,3,10,12', 'B-200,45,30,', 'D-400,8,8,']]}
new = {}
final = {}
for p, t in case["files"].items():
    r = rules.get(p, ["keep"])
    if r[0] == "absent":
        continue
    if r[0] == "keep":
        final[p] = t
    elif r[0] == "sub":
        assert r[1] in t, p
        final[p] = t.replace(r[1], r[2])
    elif r[0] == "has":
        final[p] = "\n".join(r[1])
exp = case["expect"]["files"]
for p, e in exp.items():
    if p in new:
        assert e == new[p], p
    elif e.get("absent"):
        assert p not in final, p
    elif e.get("unchanged"):
        assert final[p] == case["files"][p], p
    elif "contains" in e:
        assert all(x in final[p] for x in e["contains"]), p
    else:
        assert final[p] == e["equals"], p
blob = " ".join(list(case["files"]) + list(case["files"].values())).lower()
for s in ['安全库存']:
    assert s.lower() in blob or s.lower() in case["turns"][0]["prompt"].lower(), s
for p, e in new.items():
    final[p] = e["equals"] if "equals" in e else "\n".join(e["contains"])
print(json.dumps({"files": {p: final[p] for p, e in exp.items() if p in final and ("equals" in e or "contains" in e)}}, ensure_ascii=False))
