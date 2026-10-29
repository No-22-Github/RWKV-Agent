# DISTILL-CANARY-cf66d3d2 : distillation case
import hashlib, json
case = json.load(open("case.json"))
files = case["files"]
_pin = hashlib.sha256(json.dumps(files, ensure_ascii=False, sort_keys=True).encode()).hexdigest()
assert _pin == '2c3a96866bb0cb0f9cff4e58c73aa6da20e98cb6344699276815f0355ed14415', "fixture changed"
FACTS = json.loads('[{"line": "upstream_timeout = 27", "decoy": "upstream_timeout = 60", "al": 359, "dl": 64}]')
ls = files['配置/网关路由.ini'].split("\n")
def at(sub):
    h = [i + 1 for i, l in enumerate(ls) if sub in l]
    assert len(h) == 1, (sub, h)
    return h[0]
for f in FACTS:
    assert at(f["line"]) == f["al"] and at(f["decoy"]) == f["dl"], f
    assert f["al"] > 230 and f["dl"] < 150
print(json.dumps({"expected_number": float('27')}))
