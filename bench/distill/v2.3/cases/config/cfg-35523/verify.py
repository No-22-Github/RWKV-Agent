# DISTILL-CANARY-247480ed : distillation case
import hashlib, json
case = json.load(open("case.json"))
files = case["files"]
_pin = hashlib.sha256(json.dumps(files, ensure_ascii=False, sort_keys=True).encode()).hexdigest()
assert _pin == '352e0b194c103c22ca84a5af8c234cede38edf6c9fa2bce2c60607322565facf', "fixture changed"
FACTS = json.loads('[{"line": "channel.marketing.daily_limit", "decoy": "channel.verify.daily_limit", "al": 367, "dl": 60}]')
ls = files['配置/短信通道.properties'].split("\n")
def at(sub):
    h = [i + 1 for i, l in enumerate(ls) if sub in l]
    assert len(h) == 1, (sub, h)
    return h[0]
for f in FACTS:
    assert at(f["line"]) == f["al"] and at(f["decoy"]) == f["dl"], f
    assert f["al"] > 230 and f["dl"] < 150
print(json.dumps({"expected_contains_any": ["50000", "50,000", "5万", "5 万"]}, ensure_ascii=False))
