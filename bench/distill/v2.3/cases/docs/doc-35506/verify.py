# DISTILL-CANARY-64fa3651 : distillation case
import hashlib, json
case = json.load(open("case.json"))
files = case["files"]
_pin = hashlib.sha256(json.dumps(files, ensure_ascii=False, sort_keys=True).encode()).hexdigest()
assert _pin == '053007d8ffb2d8f282daa0cc9e26e75d5ce8cca7b403e74b75cdc813dbc683e8', "fixture changed"
FACTS = json.loads('[{"line": "不满 10 年的，每年享受", "decoy": "不满 5 年的，每年享受", "al": 344, "dl": 53}]')
ls = files['制度/员工手册-2026修订.md'].split("\n")
def at(sub):
    h = [i + 1 for i, l in enumerate(ls) if sub in l]
    assert len(h) == 1, (sub, h)
    return h[0]
for f in FACTS:
    assert at(f["line"]) == f["al"] and at(f["decoy"]) == f["dl"], f
    assert f["al"] > 230 and f["dl"] < 150
print(json.dumps({"expected_number": float('10')}))
