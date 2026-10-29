# DISTILL-CANARY-21a81ea1 : distillation case
import hashlib, json
case = json.load(open("case.json"))
_pin = hashlib.sha256(json.dumps(case["files"], ensure_ascii=False, sort_keys=True).encode()).hexdigest()
assert _pin == '4e53e6fef7d3e24af2340ae11ade24795e0409777d1f432c39897d52cf00dfb6', "fixture changed"
text = " ".join(w["content"] + " " + w["snippet"] for w in case["web_fixture"]) + " " + " ".join(case["files"].values())
prompts = " ".join(t["prompt"] for t in case["turns"])
for turn in case["turns"]:
    for item in turn["expect"].get("output_contains", []):
        assert item in text or item in prompts, item
print(json.dumps({"expected_string": "60"}, ensure_ascii=False))
