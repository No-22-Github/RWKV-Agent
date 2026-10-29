# DISTILL-CANARY-1523aa59 : distillation case
import hashlib, json
case = json.load(open("case.json"))
_pin = hashlib.sha256(json.dumps(case["files"], ensure_ascii=False, sort_keys=True).encode()).hexdigest()
assert _pin == '20aa3c80a2ea71fb87b66501fbc85f824b137b84da341f656de45cd6be8391f9', "fixture changed"
for path, rule in ((case.get("expect") or {}).get("files") or {}).items():
    assert rule == {"unchanged": True}, path
    assert path in case["files"]
words = []
for t in case["turns"]:
    for w in t["expect"]["output_contains_any"]:
        if w not in words:
            words.append(w)
print(json.dumps({"expected_contains_any": words}, ensure_ascii=False))
