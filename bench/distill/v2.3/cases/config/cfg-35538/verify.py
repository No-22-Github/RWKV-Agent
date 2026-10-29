# DISTILL-CANARY-e25f6d5b : distillation case
import hashlib, json
case = json.load(open("case.json"))
files = case["files"]
_pin = hashlib.sha256(json.dumps(files, ensure_ascii=False, sort_keys=True).encode()).hexdigest()
assert _pin == 'b83a1c3d01dc0baba82cdb24b4be3ba8d35c8d703c14231019c29af27eb59f9b', "fixture changed"
FACTS = json.loads('[{"line": "配置负责人：韩晓梅", "decoy": "备选联系人：吕建国", "al": 2, "dl": 317}]')
ls = files['配置/调度器基线.toml'].split("\n")
def at(sub):
    h = [i + 1 for i, l in enumerate(ls) if sub in l]
    assert len(h) == 1, (sub, h)
    return h[0]
for f in FACTS:
    assert at(f["line"]) == f["al"] and at(f["decoy"]) == f["dl"], f
    assert f["al"] < 60 and f["dl"] > 230
print(json.dumps({"expected_string": '韩晓梅'}, ensure_ascii=False))
