# DISTILL-CANARY-644c53e8 : distillation case
import hashlib, json
case = json.load(open("case.json"))
files = case["files"]
_pin = hashlib.sha256(json.dumps(files, ensure_ascii=False, sort_keys=True).encode()).hexdigest()
assert _pin == 'a9334631f9f9cd4b3deae171fc9e41a1e2539bb976cbfda43091c6ffc0591926', "fixture changed"
ans = 'require'
print(json.dumps({"expected_string": ans}, ensure_ascii=False))
