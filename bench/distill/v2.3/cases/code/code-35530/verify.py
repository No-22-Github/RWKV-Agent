# DISTILL-CANARY-123c646e : distillation case
import hashlib, json
case = json.load(open("case.json"))
files = case["files"]
_pin = hashlib.sha256(json.dumps(files, ensure_ascii=False, sort_keys=True).encode()).hexdigest()
assert _pin == 'bf0bf51343b2472417f7345da1b8e95b69874313a4ab4b8bbddeec58218ca61b', "fixture changed"
FACTS = json.loads('[{"line": "AUTO_CONFIRM_HOURS = 168", "decoy": "AUTO_CANCEL_MINUTES = 30", "al": 303, "dl": 4}]')
ls = files['src/订单/状态机.js'].split("\n")
def at(sub):
    h = [i + 1 for i, l in enumerate(ls) if sub in l]
    assert len(h) == 1, (sub, h)
    return h[0]
for f in FACTS:
    assert at(f["line"]) == f["al"] and at(f["decoy"]) == f["dl"], f
    assert f["al"] > 230 and f["dl"] < 150
print(json.dumps({"expected_number": float('168')}))
