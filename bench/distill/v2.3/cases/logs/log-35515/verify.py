# DISTILL-CANARY-c0059e28 : distillation case
import hashlib, json
case = json.load(open("case.json"))
files = case["files"]
_pin = hashlib.sha256(json.dumps(files, ensure_ascii=False, sort_keys=True).encode()).hexdigest()
assert _pin == 'cf1de42dc06fb661a2a5b60bdb913fba23a41e322eda45042d9619ba64b5c7da', "fixture changed"
FACTS = json.loads('[{"line": "汇总（正式）", "decoy": "汇总（预跑）", "al": 442, "dl": 61}]')
ls = files['logs/风控批处理-0920.log'].split("\n")
def at(sub):
    h = [i + 1 for i, l in enumerate(ls) if sub in l]
    assert len(h) == 1, (sub, h)
    return h[0]
for f in FACTS:
    assert at(f["line"]) == f["al"] and at(f["decoy"]) == f["dl"], f
    assert f["al"] > 230 and f["dl"] < 150
print(json.dumps({"expected_number": float('342')}))
