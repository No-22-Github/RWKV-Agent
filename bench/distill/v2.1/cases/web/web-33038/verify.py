# DISTILL-CANARY-0560ef23 : distillation case
import hashlib, json
case = json.load(open("case.json"))
_pin = hashlib.sha256(json.dumps(case["files"], ensure_ascii=False, sort_keys=True).encode()).hexdigest()
assert _pin == '14a631e503b23b57057806a3fdd35f55034853bcec20224cee39cdc987cdf8f5', "fixture changed"
page = " ".join(w["content"] + " " + w["snippet"] for w in case["web_fixture"])
for turn in case["turns"]:
    for item in turn["expect"].get("output_contains", []):
        assert item in page or item in ["My package.json pins gantry-build at 2.28.4. Is that the current release, and if not what is?"], item
print(json.dumps({"expected_string": "2.31.0"}, ensure_ascii=False))
