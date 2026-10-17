# DISTILL-CANARY-94687917 : distillation case
import hashlib, json
case = json.load(open("case.json"))
_pin = hashlib.sha256(json.dumps(case["files"], ensure_ascii=False, sort_keys=True).encode()).hexdigest()
assert _pin == '44136fa355b3678a1146ad16f7e8649e94fb4fc21fe77e8310c060f61caaff8a', "fixture changed"
page = " ".join(w["content"] + " " + w["snippet"] for w in case["web_fixture"])
for turn in case["turns"]:
    for item in turn["expect"].get("output_contains", []):
        assert item in page or item in ["Read the Copperleaf Pay fee schedule and give me a short summary of what it costs.", "What's the deadline if a customer disputes a payment? Their disputes page should say."], item
print(json.dumps({"expected_string": "1.9"}, ensure_ascii=False))
