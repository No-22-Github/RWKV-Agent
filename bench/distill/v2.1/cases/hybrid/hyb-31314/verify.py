# DISTILL-CANARY-7cff4316 : distillation case
import hashlib, json
case = json.load(open("case.json"))
_pin = hashlib.sha256(json.dumps(case["files"], ensure_ascii=False, sort_keys=True).encode()).hexdigest()
assert _pin == '4d68f6994f0a9564a9b65ea6f10fa7fab272a4015128d53620f2002297f6dfa9', "fixture changed"
rules = {'docs/api.md': ['sub', 'api.old-host.com', 'api.new-host.com'], 'docs/faq.md': ['sub', 'api.old-host.com', 'api.new-host.com'], 'config/client.yaml': ['sub', 'api.old-host.com', 'api.new-host.com']}
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
    else:
        final[p] = r[1]
exp = case["expect"]["files"]
for p, e in exp.items():
    if e.get("absent"):
        assert p not in final, p
    elif e.get("unchanged"):
        assert final[p] == case["files"][p], p
    elif "contains" in e:
        assert all(x in final[p] for x in e["contains"]), p
    else:
        assert final[p] == e["equals"], p
assert case['turns'][0]['expect']['forbidden_tools']
print(json.dumps({"files": {p: final[p] for p, e in exp.items() if "equals" in e or "contains" in e}}, ensure_ascii=False))

assert all(any(s in p or s in t for p, t in case['files'].items()) for s in case['turns'][0]['expect']['output_contains'])
