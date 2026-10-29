# DISTILL-CANARY-1144f4ca : distillation case
import hashlib, json
case = json.load(open("case.json"))
files = case["files"]
_pin = hashlib.sha256(json.dumps(files, ensure_ascii=False, sort_keys=True).encode()).hexdigest()
assert _pin == '06dbc58046c098f0171690b1b12ac2fce35102fd4224157abf13f53ce12bd3e1', "fixture changed"
FACTS = json.loads('[{"line": "bear interest at 1.5%", "decoy": "Early-payment discount", "al": 328, "dl": 45}, {"line": "90 days\' written notice", "decoy": "14 days\' notice", "al": 424, "dl": 68}]')
ls = files['contracts/norvale-supply-terms.md'].split("\n")
def at(sub):
    h = [i + 1 for i, l in enumerate(ls) if sub in l]
    assert len(h) == 1, (sub, h)
    return h[0]
for f in FACTS:
    assert at(f["line"]) == f["al"] and at(f["decoy"]) == f["dl"], f
    assert f["al"] > 230 and f["dl"] < 150
print(json.dumps({"expected_contains_any": ["1.5%", "1.5 %", "1.5 percent"]}, ensure_ascii=False))
