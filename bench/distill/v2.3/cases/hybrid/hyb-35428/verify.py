# DISTILL-CANARY-35ac28de : distillation case
import hashlib, json
case = json.load(open("case.json"))
_pin = hashlib.sha256(json.dumps(case["files"], ensure_ascii=False, sort_keys=True).encode()).hexdigest()
assert _pin == 'b880b79ab9ac72e8c5cf41a85b729ded24e371429849c493b176685edc72bcdf', "fixture changed"
for path, rule in ((case.get("expect") or {}).get("files") or {}).items():
    assert rule == {"unchanged": True}, path
    assert path in case["files"]
words = []
for t in case["turns"]:
    for w in t["expect"]["output_contains_any"]:
        if w not in words:
            words.append(w)
print(json.dumps({"expected_contains_any": words}, ensure_ascii=False))
