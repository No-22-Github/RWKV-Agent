# DISTILL-CANARY-93834713 : distillation case
import hashlib, json
case = json.load(open("case.json"))
_pin = hashlib.sha256(json.dumps(case["files"], ensure_ascii=False, sort_keys=True).encode()).hexdigest()
assert _pin == '95b107ea6fa40077450a1b14fcc0465e74bdb52c6065829486109bc96acc926c', "fixture changed"
files = case["files"]
corpus = "\n".join(files.values()) + "\n".join(w["content"] + " " + w["snippet"] for w in case["web_fixture"]) + "\n".join(t["prompt"] for t in case["turns"])
_val = sum(1 for l in files['logs/gateway.log'].splitlines() if ' 502 ' in l and '2026-09-14 20:06:39' <= l[:19] <= '2026-09-14 20:22:18')
assert "%g" % _val == '3', (_val, '3')
DERIVED = json.loads('["3"]')
for turn in case["turns"]:
    for item in turn["expect"].get("output_contains", []):
        assert item in corpus or item in DERIVED, item
print(json.dumps({"expected_string": "3"}, ensure_ascii=False))
