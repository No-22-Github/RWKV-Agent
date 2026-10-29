# DISTILL-CANARY-55d905e6 : distillation case
import hashlib, json
case = json.load(open("case.json"))
files = case["files"]
_pin = hashlib.sha256(json.dumps(files, ensure_ascii=False, sort_keys=True).encode()).hexdigest()
assert _pin == '84d4b23d2c605572e60cd6d3b1718a9a5c31fabc3f153cf63d8d419b9f2ec172', "fixture changed"
FACTS = json.loads('[{"line": "build=7731", "decoy": "build=7688", "al": 472, "dl": 86}]')
ls = files['logs/deploy-pipeline-1103.log'].split("\n")
def at(sub):
    h = [i + 1 for i, l in enumerate(ls) if sub in l]
    assert len(h) == 1, (sub, h)
    return h[0]
for f in FACTS:
    assert at(f["line"]) == f["al"] and at(f["decoy"]) == f["dl"], f
    assert f["al"] > 230 and f["dl"] < 150
print(json.dumps({"expected_number": float('7731')}))
