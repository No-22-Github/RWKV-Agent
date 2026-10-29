# DISTILL-CANARY-f043f594 : distillation case
import hashlib, json
case = json.load(open("case.json"))
files = case["files"]
_pin = hashlib.sha256(json.dumps(files, ensure_ascii=False, sort_keys=True).encode()).hexdigest()
assert _pin == '92d2f161c8f878fe2e9328a7c6cec8e17a9250994c55f694b8893df7a4aeb421', "fixture changed"
FACTS = json.loads('[{"line": "全量备份失败", "decoy": "增量备份重试", "al": 402, "dl": 76}]')
ls = files['logs/备份任务-1015.log'].split("\n")
def at(sub):
    h = [i + 1 for i, l in enumerate(ls) if sub in l]
    assert len(h) == 1, (sub, h)
    return h[0]
for f in FACTS:
    assert at(f["line"]) == f["al"] and at(f["decoy"]) == f["dl"], f
    assert f["al"] > 230 and f["dl"] < 150
print(json.dumps({"expected_string": 'E4017'}, ensure_ascii=False))
