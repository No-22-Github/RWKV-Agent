# DISTILL-CANARY-9ad19b21 : distillation case
import hashlib, json
case = json.load(open("case.json"))
_pin = hashlib.sha256(json.dumps(case["files"], ensure_ascii=False, sort_keys=True).encode()).hexdigest()
assert _pin == 'db3195a9f16f1e65d6fc83b8160102db27a7d818c1b9007df377e9d1fcfff3f7', "fixture changed"
text = " ".join(w["content"] + " " + w["snippet"] for w in case["web_fixture"]) + " " + " ".join(case["files"].values())
for turn in case["turns"]:
    for item in turn["expect"].get("output_contains", []):
        assert item in text or item in turn["prompt"], item
print(json.dumps({"expected_contains_any": ["2 million", "2,000,000", "2M", "200 万", "200万", "两百万"]}, ensure_ascii=False))
