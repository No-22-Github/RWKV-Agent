# DISTILL-CANARY-90da807d : distillation case
import hashlib, json
case = json.load(open("case.json"))
files = case["files"]
_pin = hashlib.sha256(json.dumps(files, ensure_ascii=False, sort_keys=True).encode()).hexdigest()
assert _pin == '3e7eef4b445e3f2732bd367180115c09067844cdb3f3f1685b61b82be5e3b7b9', "fixture changed"
FACTS = json.loads('[{"line": "Owner: Dana Ostrowski", "decoy": "Template maintained by: Hugh Marlowe", "al": 3, "dl": 306}]')
ls = files['docs/handbook-intro-quillpad.md'].split("\n")
def at(sub):
    h = [i + 1 for i, l in enumerate(ls) if sub in l]
    assert len(h) == 1, (sub, h)
    return h[0]
for f in FACTS:
    assert at(f["line"]) == f["al"] and at(f["decoy"]) == f["dl"], f
    assert f["al"] < 60 and f["dl"] > 230
print(json.dumps({"expected_string": 'Dana Ostrowski'}, ensure_ascii=False))
