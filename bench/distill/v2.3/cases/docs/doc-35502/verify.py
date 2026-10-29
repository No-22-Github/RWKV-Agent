# DISTILL-CANARY-827d78f0 : distillation case
import hashlib, json
case = json.load(open("case.json"))
files = case["files"]
_pin = hashlib.sha256(json.dumps(files, ensure_ascii=False, sort_keys=True).encode()).hexdigest()
assert _pin == 'fcf932f2baa8733b4c9811cd857fcf3d17915d8f86908ae6e5ff2d30b2f2f1b5', "fixture changed"
FACTS = json.loads('[{"line": "P1 pages escalate to the secondary", "decoy": "P2 tickets escalate", "al": 338, "dl": 49}]')
ls = files['docs/oncall-escalation-handbook.md'].split("\n")
def at(sub):
    h = [i + 1 for i, l in enumerate(ls) if sub in l]
    assert len(h) == 1, (sub, h)
    return h[0]
for f in FACTS:
    assert at(f["line"]) == f["al"] and at(f["decoy"]) == f["dl"], f
    assert f["al"] > 230 and f["dl"] < 150
print(json.dumps({"expected_number": float('7')}))
