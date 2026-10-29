# DISTILL-CANARY-e3349ff2 : distillation case
import hashlib, json
case = json.load(open("case.json"))
files = case["files"]
_pin = hashlib.sha256(json.dumps(files, ensure_ascii=False, sort_keys=True).encode()).hexdigest()
assert _pin == '864e946f115f15d2d55d324ca7b4bc143a134535bfa4c6ce787e701387c4dcbb', "fixture changed"
FACTS = json.loads('[{"line": "## 4.8.2 - ", "decoy": "the last entry there is 2.9.7", "al": 5, "dl": 303}]')
ls = files['docs/relnotes-orchard-sdk.md'].split("\n")
def at(sub):
    h = [i + 1 for i, l in enumerate(ls) if sub in l]
    assert len(h) == 1, (sub, h)
    return h[0]
for f in FACTS:
    assert at(f["line"]) == f["al"] and at(f["decoy"]) == f["dl"], f
    assert f["al"] < 60 and f["dl"] > 230
print(json.dumps({"expected_string": '4.8.2'}, ensure_ascii=False))
