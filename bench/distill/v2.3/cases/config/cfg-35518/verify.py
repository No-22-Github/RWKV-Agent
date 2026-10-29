# DISTILL-CANARY-661b5082 : distillation case
import hashlib, json
case = json.load(open("case.json"))
files = case["files"]
_pin = hashlib.sha256(json.dumps(files, ensure_ascii=False, sort_keys=True).encode()).hexdigest()
assert _pin == '6ecc8d0fec599a4d942745b74ac1cc1d699429b42ff982ea641dab92f16392fe', "fixture changed"
FACTS = json.loads('[{"line": "sync_interval = 300", "decoy": "sync_interval = 45", "al": 350, "dl": 69}]')
ls = files['conf/vault-sync.ini'].split("\n")
def at(sub):
    h = [i + 1 for i, l in enumerate(ls) if sub in l]
    assert len(h) == 1, (sub, h)
    return h[0]
for f in FACTS:
    assert at(f["line"]) == f["al"] and at(f["decoy"]) == f["dl"], f
    assert f["al"] > 230 and f["dl"] < 150
print(json.dumps({"expected_number": float('300')}))
