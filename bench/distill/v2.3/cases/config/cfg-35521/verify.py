# DISTILL-CANARY-3ecd2711 : distillation case
import hashlib, json
case = json.load(open("case.json"))
files = case["files"]
_pin = hashlib.sha256(json.dumps(files, ensure_ascii=False, sort_keys=True).encode()).hexdigest()
assert _pin == 'a21afd9a96fae9e47faa4ac2c01a8dafc9433f2c0a55239896f55978449332c3', "fixture changed"
FACTS = json.loads('[{"line": "for_minutes: 15", "decoy": "for_minutes: 5", "al": 351, "dl": 60}]')
ls = files['配置/告警规则-生产.yaml'].split("\n")
def at(sub):
    h = [i + 1 for i, l in enumerate(ls) if sub in l]
    assert len(h) == 1, (sub, h)
    return h[0]
for f in FACTS:
    assert at(f["line"]) == f["al"] and at(f["decoy"]) == f["dl"], f
    assert f["al"] > 230 and f["dl"] < 150
print(json.dumps({"expected_number": float('15')}))
