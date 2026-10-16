# DISTILL-CANARY-7dd36e7f : distillation case
import hashlib, json
case = json.load(open("case.json"))
_pin = hashlib.sha256(json.dumps(case["files"], ensure_ascii=False, sort_keys=True).encode()).hexdigest()
assert _pin == 'f2b0079f7b0d0b5ce7aaf90b434438f8459f0b524b2cf7db2144d5fe3bec2e27', "fixture changed"
import re
m = re.search('chats are kept for (\\d+) months', case["files"]['legal/retention.md'])
assert m, "pattern"
ans = m.group(1)
assert ans in case["turns"][0]["expect"]["output_contains"]

print(json.dumps({"expected_string": ans}, ensure_ascii=False))
