# DISTILL-CANARY-4c0c62af : distillation case
import hashlib, json
case = json.load(open("case.json"))
_pin = hashlib.sha256(json.dumps(case["files"], ensure_ascii=False, sort_keys=True).encode()).hexdigest()
assert _pin == '44136fa355b3678a1146ad16f7e8649e94fb4fc21fe77e8310c060f61caaff8a', "fixture changed"
page = " ".join(w["content"] + " " + w["snippet"] for w in case["web_fixture"])
for turn in case["turns"]:
    for item in turn["expect"].get("output_contains", []):
        assert item in page or item in ["Kestrel Mail's help page and a tips blog disagree on the attachment size limit. Which one is the vendor's own page, which one is more recent, and what is the limit?"], item
print(json.dumps({"expected_string": "35"}, ensure_ascii=False))
