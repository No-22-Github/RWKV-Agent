# DISTILL-CANARY-69798719 : distillation case
import hashlib, json
case = json.load(open("case.json"))
files = case["files"]
_pin = hashlib.sha256(json.dumps(files, ensure_ascii=False, sort_keys=True).encode()).hexdigest()
assert _pin == '6e6b0c4b6f9fc42c9bbd79eb27ccbcdfff5ee2cc91f345e9ebb6924e040c2602', "fixture changed"
FACTS = json.loads('[{"line": "影响时长：83 分钟", "decoy": "影响时长：19 分钟", "al": 337, "dl": 49}, {"line": "影响时长：36 分钟", "decoy": "影响时长：8 分钟", "al": 436, "dl": 78}]')
ls = files['运维/故障复盘汇编-2026上半年.md'].split("\n")
def at(sub):
    h = [i + 1 for i, l in enumerate(ls) if sub in l]
    assert len(h) == 1, (sub, h)
    return h[0]
for f in FACTS:
    assert at(f["line"]) == f["al"] and at(f["decoy"]) == f["dl"], f
    assert f["al"] > 230 and f["dl"] < 150
print(json.dumps({"expected_number": float('83')}))
