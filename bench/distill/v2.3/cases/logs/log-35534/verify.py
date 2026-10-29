# DISTILL-CANARY-1af1a1f7 : distillation case
import hashlib, json
case = json.load(open("case.json"))
files = case["files"]
_pin = hashlib.sha256(json.dumps(files, ensure_ascii=False, sort_keys=True).encode()).hexdigest()
assert _pin == 'aec6b443da8ffadfe01c9f01308f20553446db9a6e3b1928b62af32462058600', "fixture changed"
FACTS = json.loads('[{"line": "00:00:08", "decoy": "previous segment began 2026-09-25 23:41:17", "al": 1, "dl": 401}]')
ls = files['logs/sync-agent-0926.log'].split("\n")
def at(sub):
    h = [i + 1 for i, l in enumerate(ls) if sub in l]
    assert len(h) == 1, (sub, h)
    return h[0]
for f in FACTS:
    assert at(f["line"]) == f["al"] and at(f["decoy"]) == f["dl"], f
    assert f["al"] < 60 and f["dl"] > 230
print(json.dumps({"expected_string": '00:00:08'}, ensure_ascii=False))
