# DISTILL-CANARY-ad88e4c1 : distillation case
import hashlib, json
case = json.load(open("case.json"))
files = case["files"]
_pin = hashlib.sha256(json.dumps(files, ensure_ascii=False, sort_keys=True).encode()).hexdigest()
assert _pin == 'ab619f0bd968e4e2c6ea17b9c8f28950708229fa2d6ac68e9cb6df50fa94767f', "fixture changed"
FACTS = json.loads('[{"line": "  pool_size: 96", "decoy": "  pool_size: 20", "al": 342, "dl": 57}]')
ls = files['deploy/service-mesh-overrides.yaml'].split("\n")
def at(sub):
    h = [i + 1 for i, l in enumerate(ls) if sub in l]
    assert len(h) == 1, (sub, h)
    return h[0]
for f in FACTS:
    assert at(f["line"]) == f["al"] and at(f["decoy"]) == f["dl"], f
    assert f["al"] > 230 and f["dl"] < 150
print(json.dumps({"expected_number": float('96')}))
