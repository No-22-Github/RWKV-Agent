# DISTILL-CANARY-a0dbb44b : distillation case
import hashlib
import json

case = json.load(open("case.json"))
assert hashlib.sha256(json.dumps(case["files"], sort_keys=True, ensure_ascii=False).encode()).hexdigest().startswith('d13449a6da116e64')
print(json.dumps({"expected_contains_any": ["no new value", "not specified", "does not specify", "doesn't specify", "missing", "not provided", "no value", "pending", "tbd", "TBD", "not set", "does not exist", "doesn't exist", "not exist", "no such", "not found", "conflict", "disagree", "differ", "inconsistent", "no config", "there is no", "there isn't", "no file", "cannot find", "can't find", "couldn't find", "could not find", "not present", "no entry", "doesn’t specify", "doesn’t exist", "there isn’t", "can’t find", "couldn’t find"]}, ensure_ascii=False))
