# DISTILL-CANARY-99e23346 : distillation case
import hashlib, json
case = json.load(open("case.json"))
files = case["files"]
_pin = hashlib.sha256(json.dumps(files, ensure_ascii=False, sort_keys=True).encode()).hexdigest()
assert _pin == '781c72d5590c74ad3bb0e6d7aca6ec4b31e0c93b16eac8dd7bc2554957bda9e3', "fixture changed"
FACTS = json.loads('[{"line": "Raised the default request timeout", "decoy": "20s idle timeout", "al": 276, "dl": 7}]')
ls = files['docs/relnotes-lumengate.md'].split("\n")
def at(sub):
    h = [i + 1 for i, l in enumerate(ls) if sub in l]
    assert len(h) == 1, (sub, h)
    return h[0]
for f in FACTS:
    assert at(f["line"]) == f["al"] and at(f["decoy"]) == f["dl"], f
    assert f["al"] > 230 and f["dl"] < 150
print(json.dumps({"expected_contains_any": ["45s", "45 s", "45-second", "45 sec"]}, ensure_ascii=False))
