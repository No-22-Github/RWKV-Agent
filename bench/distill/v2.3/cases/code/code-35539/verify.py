# DISTILL-CANARY-13f465e2 : distillation case
import hashlib, json
case = json.load(open("case.json"))
files = case["files"]
_pin = hashlib.sha256(json.dumps(files, ensure_ascii=False, sort_keys=True).encode()).hexdigest()
assert _pin == 'facb9917c3cdd52a96f7176b0798a2c20ac511d38a95e0f1e7ea5c6bc22b61a4', "fixture changed"
FACTS = json.loads('[{"line": "__version__ = \\"1.14.0\\"", "decoy": "LEGACY_VERSION = \\"0.9.3\\"", "al": 3, "dl": 313}]')
ls = files['src/vault/key_rotation.py'].split("\n")
def at(sub):
    h = [i + 1 for i, l in enumerate(ls) if sub in l]
    assert len(h) == 1, (sub, h)
    return h[0]
for f in FACTS:
    assert at(f["line"]) == f["al"] and at(f["decoy"]) == f["dl"], f
    assert f["al"] < 60 and f["dl"] > 230
print(json.dumps({"expected_string": '1.14.0'}, ensure_ascii=False))
