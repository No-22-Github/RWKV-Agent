# DISTILL-CANARY-19f1777f : distillation case
import hashlib, json
case = json.load(open("case.json"))
files = case["files"]
_pin = hashlib.sha256(json.dumps(files, ensure_ascii=False, sort_keys=True).encode()).hexdigest()
assert _pin == '88f4bd0571db3d25ab0a09f5d4ca870f5c02a1d3b845c18851a27d1ba1d40574', "fixture changed"
FACTS = json.loads('[{"line": "refund.client.read.timeout.ms", "decoy": "payout.client.read.timeout.ms", "al": 369, "dl": 63}]')
ls = files['conf/payments-client.properties'].split("\n")
def at(sub):
    h = [i + 1 for i, l in enumerate(ls) if sub in l]
    assert len(h) == 1, (sub, h)
    return h[0]
for f in FACTS:
    assert at(f["line"]) == f["al"] and at(f["decoy"]) == f["dl"], f
    assert f["al"] > 230 and f["dl"] < 150
print(json.dumps({"expected_contains_any": ["8500", "8,500"]}, ensure_ascii=False))
