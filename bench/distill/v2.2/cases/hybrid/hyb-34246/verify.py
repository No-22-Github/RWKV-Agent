# DISTILL-CANARY-22f19fae : distillation case
import hashlib, json
case = json.load(open("case.json"))
_pin = hashlib.sha256(json.dumps(case["files"], ensure_ascii=False, sort_keys=True).encode()).hexdigest()
assert _pin == '6de84f494c708f4171a556c8304e91059e915b36f2bffb707689c56141624d69', "fixture changed"
files = case["files"]
corpus = "\n".join(files.values()) + "\n".join(w["content"] + " " + w["snippet"] for w in case["web_fixture"]) + "\n".join(t["prompt"] for t in case["turns"])
_val = 357/4
assert "%g" % _val == '89.25', (_val, '89.25')
_val = sum(float(l.split(',')[2]) for l in files['财务/行政采购流水.csv'].splitlines()[1:])
assert "%g" % _val == '357', (_val, '357')
DERIVED = json.loads('["357", "89.25"]')
for turn in case["turns"]:
    for item in turn["expect"].get("output_contains", []):
        assert item in corpus or item in DERIVED, item
print(json.dumps({"expected_string": "357"}, ensure_ascii=False))
