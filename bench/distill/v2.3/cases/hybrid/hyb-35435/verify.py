# DISTILL-CANARY-5a3f4a38 : distillation case
import hashlib, json
case = json.load(open("case.json"))
_pin = hashlib.sha256(json.dumps(case["files"], ensure_ascii=False, sort_keys=True).encode()).hexdigest()
assert _pin == '54c501447689da3e44a18ff8dff5e433f100724c0b3b51d40b3a6ed47ab5c0f2', "fixture changed"
for path, rule in ((case.get("expect") or {}).get("files") or {}).items():
    assert rule == {"unchanged": True}, path
    assert path in case["files"]
words = []
for t in case["turns"]:
    for w in t["expect"]["output_contains_any"]:
        if w not in words:
            words.append(w)
print(json.dumps({"expected_contains_any": words}, ensure_ascii=False))
