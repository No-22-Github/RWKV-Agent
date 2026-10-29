# DISTILL-CANARY-c4222235 : distillation case
import hashlib, json
case = json.load(open("case.json"))
files = case["files"]
_pin = hashlib.sha256(json.dumps(files, ensure_ascii=False, sort_keys=True).encode()).hexdigest()
assert _pin == 'cf5f444d73132a82614a875f4e291ca9d3b041129b259b81e2e89bd5c46dc04b', "fixture changed"
FACTS = json.loads('[{"line": "一线城市住宿，每晚报销上限", "decoy": "二线城市住宿，每晚报销上限", "al": 357, "dl": 55}]')
ls = files['财务/差旅报销办法-汇编.md'].split("\n")
def at(sub):
    h = [i + 1 for i, l in enumerate(ls) if sub in l]
    assert len(h) == 1, (sub, h)
    return h[0]
for f in FACTS:
    assert at(f["line"]) == f["al"] and at(f["decoy"]) == f["dl"], f
    assert f["al"] > 230 and f["dl"] < 150
print(json.dumps({"expected_number": float('650')}))
