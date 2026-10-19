# DISTILL-CANARY-5c01d0dd : distillation case
import hashlib, json
case = json.load(open("case.json"))
_pin = hashlib.sha256(json.dumps(case["files"], ensure_ascii=False, sort_keys=True).encode()).hexdigest()
assert _pin == '587035f03e5135494ab9d249396d30f232859b236af37c21f06960c8cef2bb03', "fixture changed"
text = " ".join(w["content"] + " " + w["snippet"] for w in case["web_fixture"]) + " " + " ".join(case["files"].values())
for turn in case["turns"]:
    for item in turn["expect"].get("output_contains", []):
        assert item in text or item in turn["prompt"], item
print(json.dumps({"expected_string": "25"}, ensure_ascii=False))
