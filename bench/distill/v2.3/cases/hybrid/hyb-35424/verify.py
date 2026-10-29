# DISTILL-CANARY-9558fda5 : distillation case
import hashlib, json
case = json.load(open("case.json"))
_pin = hashlib.sha256(json.dumps(case["files"], ensure_ascii=False, sort_keys=True).encode()).hexdigest()
assert _pin == '813ec28031865c47c0b51ac92b230f092b79d83c46d2fb01fec58408673e20c5', "fixture changed"
for path, rule in ((case.get("expect") or {}).get("files") or {}).items():
    assert rule == {"unchanged": True}, path
    assert path in case["files"]
words = []
for t in case["turns"]:
    for w in t["expect"]["output_contains_any"]:
        if w not in words:
            words.append(w)
print(json.dumps({"expected_contains_any": words}, ensure_ascii=False))
