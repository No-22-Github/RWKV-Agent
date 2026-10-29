# DISTILL-CANARY-d5902f52 : distillation case
import hashlib, json
case = json.load(open("case.json"))
files = case["files"]
_pin = hashlib.sha256(json.dumps(files, ensure_ascii=False, sort_keys=True).encode()).hexdigest()
assert _pin == 'd40908e992cb6c2cff445dbf75c98fc2684f021c9d7c9e77e00d02ed7709851b', "fixture changed"
FACTS = json.loads('[{"line": "任务启动 批次号=BATCH-20260928-07", "decoy": "上一批遗留数据 批次号=BATCH-20260927-31", "al": 1, "dl": 422}]')
ls = files['logs/对账任务-0928.log'].split("\n")
def at(sub):
    h = [i + 1 for i, l in enumerate(ls) if sub in l]
    assert len(h) == 1, (sub, h)
    return h[0]
for f in FACTS:
    assert at(f["line"]) == f["al"] and at(f["decoy"]) == f["dl"], f
    assert f["al"] < 60 and f["dl"] > 230
print(json.dumps({"expected_string": 'BATCH-20260928-07'}, ensure_ascii=False))
