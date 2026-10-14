# DISTILL-CANARY-5ee858b7 : distillation case
import hashlib, json, re
case = json.load(open("case.json"))
_pin = hashlib.sha256(json.dumps(case["files"], ensure_ascii=False, sort_keys=True).encode()).hexdigest()
assert _pin == '9a2ef36026815d7b5fb2e5e40a8bd7ecac8c6ae4ec69efe80addf99624b9aa63', "fixture changed"
print(json.dumps({"expected_number": sum(1 for x in case["files"]["logs/events.jsonl"].splitlines() if '"level": "warn"' in x)}))
