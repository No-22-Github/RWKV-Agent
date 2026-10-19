# DISTILL-CANARY-eb891264 : distillation case
import hashlib, json
case = json.load(open("case.json"))
_pin = hashlib.sha256(json.dumps(case["files"], ensure_ascii=False, sort_keys=True).encode()).hexdigest()
assert _pin == '78cfb37261e76cfe071e93a586e4d7e0e386285f9826280f82687540cdbcd6fe', "fixture changed"
files = case["files"]
corpus = "\n".join(files.values()) + "\n".join(w["content"] + " " + w["snippet"] for w in case["web_fixture"]) + "\n".join(t["prompt"] for t in case["turns"])
_val = sum(1 for l in files['周报/草稿.md'].splitlines() if l.startswith('- ') and ('已上线' in l or '已完成' in l))
assert "%g" % _val == '2', (_val, '2')
DERIVED = json.loads('["2"]')
for turn in case["turns"]:
    for item in turn["expect"].get("output_contains", []):
        assert item in corpus or item in DERIVED, item
print(json.dumps({"expected_string": "2"}, ensure_ascii=False))
