# DISTILL-CANARY-1a9c9cf8 : distillation case
import hashlib, json
case = json.load(open("case.json"))
_pin = hashlib.sha256(json.dumps(case["files"], ensure_ascii=False, sort_keys=True).encode()).hexdigest()
assert _pin == '52b41d232bbac32d181dee79a747fd1e8b00cd0cc232a68c9a6039b9beb47da0', "fixture changed"
import re
m = re.search('Day (\\d+): first code review', case["files"]['onboarding/checklist.md'])
assert m, "pattern"
ans = m.group(1)
assert ans in case["turns"][0]["expect"]["output_contains"]

print(json.dumps({"expected_string": ans}, ensure_ascii=False))
