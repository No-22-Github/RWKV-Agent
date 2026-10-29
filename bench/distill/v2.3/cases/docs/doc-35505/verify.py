# DISTILL-CANARY-c76effc2 : distillation case
import hashlib, json
case = json.load(open("case.json"))
files = case["files"]
_pin = hashlib.sha256(json.dumps(files, ensure_ascii=False, sort_keys=True).encode()).hexdigest()
assert _pin == 'a663d7f828a74bca049330404f991c79cb1a1e1e59076f5419f3282c5f797b79', "fixture changed"
FACTS = json.loads('[{"line": "cutover to the new queue cluster is set", "decoy": "Tentative cutover", "al": 339, "dl": 3}, {"line": "owns the rollback plan", "decoy": "owns the capacity plan", "al": 429, "dl": 66}]')
ls = files['meetings/platform-sync-2026H1.md'].split("\n")
def at(sub):
    h = [i + 1 for i, l in enumerate(ls) if sub in l]
    assert len(h) == 1, (sub, h)
    return h[0]
for f in FACTS:
    assert at(f["line"]) == f["al"] and at(f["decoy"]) == f["dl"], f
    assert f["al"] > 230 and f["dl"] < 150
print(json.dumps({"expected_string": '2026-11-14'}, ensure_ascii=False))
