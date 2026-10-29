# DISTILL-CANARY-1d8ff3d7 : distillation case
import hashlib, json
case = json.load(open("case.json"))
files = case["files"]
_pin = hashlib.sha256(json.dumps(files, ensure_ascii=False, sort_keys=True).encode()).hexdigest()
assert _pin == 'ff7ba49fd8f1dc98632c8763e8ddfe6fe25c333cc58065dec9103888ed1d26d0', "fixture changed"
FACTS = json.loads('[{"line": "Killed process 28817", "decoy": "oom_adj changed for process 4411", "al": 452, "dl": 76}]')
ls = files['logs/syslog-dbhost-0907.log'].split("\n")
def at(sub):
    h = [i + 1 for i, l in enumerate(ls) if sub in l]
    assert len(h) == 1, (sub, h)
    return h[0]
for f in FACTS:
    assert at(f["line"]) == f["al"] and at(f["decoy"]) == f["dl"], f
    assert f["al"] > 230 and f["dl"] < 150
print(json.dumps({"expected_number": float('28817')}))
