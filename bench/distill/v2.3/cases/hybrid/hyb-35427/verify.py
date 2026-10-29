# DISTILL-CANARY-a943e823 : distillation case
import hashlib, json
case = json.load(open("case.json"))
_pin = hashlib.sha256(json.dumps(case["files"], ensure_ascii=False, sort_keys=True).encode()).hexdigest()
assert _pin == '76d7f6c4cfd9c296797da56c0ab3f047db71199df2ab5ae2756969084bc12b57', "fixture changed"
for path, rule in ((case.get("expect") or {}).get("files") or {}).items():
    assert rule == {"unchanged": True}, path
    assert path in case["files"]
words = []
for t in case["turns"]:
    for w in t["expect"]["output_contains_any"]:
        if w not in words:
            words.append(w)
print(json.dumps({"expected_contains_any": words}, ensure_ascii=False))
