# DISTILL-CANARY-8b46eed7 : distillation case
import hashlib, json
case = json.load(open("case.json"))
files = case["files"]
_pin = hashlib.sha256(json.dumps(files, ensure_ascii=False, sort_keys=True).encode()).hexdigest()
assert _pin == '39defb80107c9a1e10f66547874ecda4a9a720ccabfdd67d5babf0b55c0703c1', "fixture changed"
FACTS = json.loads('[{"line": "certificate expired host", "decoy": "certificate renewal scheduled", "al": 422, "dl": 81}]')
ls = files['logs/gateway-cluster-0921.log'].split("\n")
def at(sub):
    h = [i + 1 for i, l in enumerate(ls) if sub in l]
    assert len(h) == 1, (sub, h)
    return h[0]
for f in FACTS:
    assert at(f["line"]) == f["al"] and at(f["decoy"]) == f["dl"], f
    assert f["al"] > 230 and f["dl"] < 150
print(json.dumps({"expected_string": 'edge-fra-07'}, ensure_ascii=False))
