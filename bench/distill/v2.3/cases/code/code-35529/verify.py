# DISTILL-CANARY-1512a9a9 : distillation case
import hashlib, json
case = json.load(open("case.json"))
files = case["files"]
_pin = hashlib.sha256(json.dumps(files, ensure_ascii=False, sort_keys=True).encode()).hexdigest()
assert _pin == '91f6279b31f19a9f44e74ab8ca2563ad3fdc2b9c268ea82f89552103c1125a28', "fixture changed"
FACTS = json.loads('[{"line": "HIGH_RISK_AMOUNT = 20000", "decoy": "LOW_RISK_AMOUNT = 500", "al": 322, "dl": 5}]')
ls = files['src/风控/规则引擎.py'].split("\n")
def at(sub):
    h = [i + 1 for i, l in enumerate(ls) if sub in l]
    assert len(h) == 1, (sub, h)
    return h[0]
for f in FACTS:
    assert at(f["line"]) == f["al"] and at(f["decoy"]) == f["dl"], f
    assert f["al"] > 230 and f["dl"] < 150
print(json.dumps({"expected_contains_any": ["20000", "20,000", "2万", "2 万"]}, ensure_ascii=False))
