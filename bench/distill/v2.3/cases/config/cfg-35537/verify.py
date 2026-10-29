# DISTILL-CANARY-8a3f3229 : distillation case
import hashlib, json
case = json.load(open("case.json"))
files = case["files"]
_pin = hashlib.sha256(json.dumps(files, ensure_ascii=False, sort_keys=True).encode()).hexdigest()
assert _pin == 'fb389d96edc020c71c5c8c732e0166fa0ebc821c5e1d97daf958658e85b5dc6f', "fixture changed"
FACTS = json.loads('[{"line": "maintainer: platform-infra@lumenstack.io", "decoy": "contact: ops-legacy@lumenstack.io", "al": 2, "dl": 320}]')
ls = files['conf/kiln-agent.ini'].split("\n")
def at(sub):
    h = [i + 1 for i, l in enumerate(ls) if sub in l]
    assert len(h) == 1, (sub, h)
    return h[0]
for f in FACTS:
    assert at(f["line"]) == f["al"] and at(f["decoy"]) == f["dl"], f
    assert f["al"] < 60 and f["dl"] > 230
print(json.dumps({"expected_string": 'platform-infra@lumenstack.io'}, ensure_ascii=False))
