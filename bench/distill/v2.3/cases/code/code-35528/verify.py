# DISTILL-CANARY-f433c215 : distillation case
import hashlib, json
case = json.load(open("case.json"))
files = case["files"]
_pin = hashlib.sha256(json.dumps(files, ensure_ascii=False, sort_keys=True).encode()).hexdigest()
assert _pin == '298ae74cef55a7a575c43523ca0039dcfb7d852e5ec527f9655da2e992217734', "fixture changed"
FACTS = json.loads('[{"line": "EXPRESS_FLAG = \\"ff_express_checkout_v3\\"", "decoy": "GIFTCARD_FLAG = \\"ff_giftcard_redeem\\"", "al": 308, "dl": 4}]')
ls = files['src/web/checkout-flow.js'].split("\n")
def at(sub):
    h = [i + 1 for i, l in enumerate(ls) if sub in l]
    assert len(h) == 1, (sub, h)
    return h[0]
for f in FACTS:
    assert at(f["line"]) == f["al"] and at(f["decoy"]) == f["dl"], f
    assert f["al"] > 230 and f["dl"] < 150
print(json.dumps({"expected_string": 'ff_express_checkout_v3'}, ensure_ascii=False))
