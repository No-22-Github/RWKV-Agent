# DISTILL-CANARY-d21e270d : distillation case
import hashlib, json
case = json.load(open("case.json"))
files = case["files"]
_pin = hashlib.sha256(json.dumps(files, ensure_ascii=False, sort_keys=True).encode()).hexdigest()
assert _pin == '52881306fc4d84415f8f465ad8c1ccc506e98883e5c5b2c8f03640e322ccb771', "fixture changed"
FACTS = json.loads('[{"line": "生效日期：2026-03-01", "decoy": "第 2 版生效日期为 2025-07-15", "al": 3, "dl": 313}]')
ls = files['文档/数据治理规范-v3.md'].split("\n")
def at(sub):
    h = [i + 1 for i, l in enumerate(ls) if sub in l]
    assert len(h) == 1, (sub, h)
    return h[0]
for f in FACTS:
    assert at(f["line"]) == f["al"] and at(f["decoy"]) == f["dl"], f
    assert f["al"] < 60 and f["dl"] > 230
print(json.dumps({"expected_string": '2026-03-01'}, ensure_ascii=False))
