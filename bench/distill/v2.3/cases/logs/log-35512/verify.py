# DISTILL-CANARY-ea22ef80 : distillation case
import hashlib, json
case = json.load(open("case.json"))
files = case["files"]
_pin = hashlib.sha256(json.dumps(files, ensure_ascii=False, sort_keys=True).encode()).hexdigest()
assert _pin == '39f399750c55023ef056516d78c7a9fb12e235657d571cdbcd3c323ed77eba3c', "fixture changed"
FACTS = json.loads('[{"line": "summary job=invoice-export", "decoy": "summary job=invoice-preview", "al": 412, "dl": 66}, {"line": "duration=412s", "decoy": "duration=38s", "al": 412, "dl": 66}]')
ls = files['logs/billing-batch-0830.log'].split("\n")
def at(sub):
    h = [i + 1 for i, l in enumerate(ls) if sub in l]
    assert len(h) == 1, (sub, h)
    return h[0]
for f in FACTS:
    assert at(f["line"]) == f["al"] and at(f["decoy"]) == f["dl"], f
    assert f["al"] > 230 and f["dl"] < 150
print(json.dumps({"expected_contains_any": ["48213", "48,213", "412s", "412 s", "412 sec"]}, ensure_ascii=False))
