# DISTILL-CANARY-5496b5b8 : distillation case
import hashlib, json
case = json.load(open("case.json"))
_pin = hashlib.sha256(json.dumps(case["files"], ensure_ascii=False, sort_keys=True).encode()).hexdigest()
assert _pin == 'a41560b222e533c88e779cd9aed1215d4b25c7d488ec2c9e6e6549b67ed21150', "fixture changed"
text = " ".join(w["content"] + " " + w["snippet"] for w in case["web_fixture"]) + " " + " ".join(case["files"].values())
for turn in case["turns"]:
    for item in turn["expect"].get("output_contains", []):
        assert item in text or item in turn["prompt"], item
print(json.dumps({"expected_contains_any": ["certificate", "Certificate", "expired", "Expired", "证书", "restart", "Restart", "重启"]}, ensure_ascii=False))
