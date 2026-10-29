# DISTILL-CANARY-2a799cad : distillation case
import hashlib, json
case = json.load(open("case.json"))
_pin = hashlib.sha256(json.dumps(case["files"], ensure_ascii=False, sort_keys=True).encode()).hexdigest()
assert _pin == 'a654bfc1d12ae8d318ec5570cf0097d671ef5464af2d145de4178bc654289215', "fixture changed"
rules = {}
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
for s in ['worker']:
    assert s.lower() in blob or s.lower() in case["turns"][0]["prompt"].lower(), s
for p, e in new.items():
    final[p] = e["equals"] if "equals" in e else "\n".join(e["contains"])
print(json.dumps({"files": {p: final[p] for p, e in exp.items() if p in final and ("equals" in e or "contains" in e)}}, ensure_ascii=False))
