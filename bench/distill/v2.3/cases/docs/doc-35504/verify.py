# DISTILL-CANARY-aa813d00 : distillation case
import hashlib, json
case = json.load(open("case.json"))
files = case["files"]
_pin = hashlib.sha256(json.dumps(files, ensure_ascii=False, sort_keys=True).encode()).hexdigest()
assert _pin == 'ea18267dbea6a76f23dac78826722d4eb229a5eaf4e80855e0fe7cd8c46f3d5b', "fixture changed"
FACTS = json.loads('[{"line": "POST /v2/exports", "decoy": "POST /v2/imports", "al": 316, "dl": 59}, {"line": "POST /v2/reports", "decoy": "GET /v2/reports", "al": 408, "dl": 58}]')
ls = files['docs/api-reference-harbor-v2.md'].split("\n")
def at(sub):
    h = [i + 1 for i, l in enumerate(ls) if sub in l]
    assert len(h) == 1, (sub, h)
    return h[0]
for f in FACTS:
    assert at(f["line"]) == f["al"] and at(f["decoy"]) == f["dl"], f
    assert f["al"] > 230 and f["dl"] < 150
print(json.dumps({"expected_number": float('40')}))
