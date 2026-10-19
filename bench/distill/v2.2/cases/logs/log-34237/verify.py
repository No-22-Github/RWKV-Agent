# DISTILL-CANARY-dd7a7892 : distillation case
import hashlib, json
case = json.load(open("case.json"))
_pin = hashlib.sha256(json.dumps(case["files"], ensure_ascii=False, sort_keys=True).encode()).hexdigest()
assert _pin == '93fc056e7d12c052c530dcc18e08604c0469e75bef8076abd2d86ea7aa4e44d2', "fixture changed"
files = case["files"]
corpus = "\n".join(files.values()) + "\n".join(w["content"] + " " + w["snippet"] for w in case["web_fixture"]) + "\n".join(t["prompt"] for t in case["turns"])
_val = sum(1 for l in files['logs/access.log'].splitlines() if ' 500 ' in l)
assert "%g" % _val == '5', (_val, '5')
DERIVED = json.loads('["5"]')
for turn in case["turns"]:
    for item in turn["expect"].get("output_contains", []):
        assert item in corpus or item in DERIVED, item
print(json.dumps({"expected_string": "5"}, ensure_ascii=False))
