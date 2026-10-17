# DISTILL-CANARY-9f0a2e4a : distillation case
import hashlib, json
case = json.load(open("case.json"))
files = case["files"]
_pin = hashlib.sha256(json.dumps(files, ensure_ascii=False, sort_keys=True).encode()).hexdigest()
assert _pin == '2c62fa8ed684e788e187794fa273bac539fc8da1b61b995c093685323ef6de09', "fixture changed"
answers=['.env.example']
print(json.dumps({"expected_string": answers[0]}, ensure_ascii=False))
