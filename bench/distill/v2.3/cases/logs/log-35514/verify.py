# DISTILL-CANARY-f51dcc40 : distillation case
import hashlib, json
case = json.load(open("case.json"))
files = case["files"]
_pin = hashlib.sha256(json.dumps(files, ensure_ascii=False, sort_keys=True).encode()).hexdigest()
assert _pin == 'ff77316aeacf4f8937fe5f8978dc9793e6c116c5588aae5bf2c6e898983b57df', "fixture changed"
FACTS = json.loads('[{"line": "连接池耗尽", "decoy": "连接池使用率", "al": 422, "dl": 71}]')
ls = files['logs/订单服务-0912.log'].split("\n")
def at(sub):
    h = [i + 1 for i, l in enumerate(ls) if sub in l]
    assert len(h) == 1, (sub, h)
    return h[0]
for f in FACTS:
    assert at(f["line"]) == f["al"] and at(f["decoy"]) == f["dl"], f
    assert f["al"] > 230 and f["dl"] < 150
print(json.dumps({"expected_string": '00:36:11'}, ensure_ascii=False))
