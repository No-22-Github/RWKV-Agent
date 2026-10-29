# DISTILL-CANARY-252c6804 : distillation case
import hashlib, json
case = json.load(open("case.json"))
files = case["files"]
_pin = hashlib.sha256(json.dumps(files, ensure_ascii=False, sort_keys=True).encode()).hexdigest()
assert _pin == 'a194ccf30a4066d1fb0bf284a8520295520d3c111763bea3d4ab3b5f7d489239', "fixture changed"
FACTS = json.loads('[{"line": "schema_version: 2026.2", "decoy": "schema_version: 2025.4", "al": 2, "dl": 315}]')
ls = files['deploy/ledger-stack-defaults.yaml'].split("\n")
def at(sub):
    h = [i + 1 for i, l in enumerate(ls) if sub in l]
    assert len(h) == 1, (sub, h)
    return h[0]
for f in FACTS:
    assert at(f["line"]) == f["al"] and at(f["decoy"]) == f["dl"], f
    assert f["al"] < 60 and f["dl"] > 230
print(json.dumps({"expected_string": '2026.2'}, ensure_ascii=False))
