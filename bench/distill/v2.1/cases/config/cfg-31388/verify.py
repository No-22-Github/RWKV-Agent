# DISTILL-CANARY-7b0cb208 : distillation case
import hashlib, json
case = json.load(open("case.json"))
_pin = hashlib.sha256(json.dumps(case["files"], ensure_ascii=False, sort_keys=True).encode()).hexdigest()
assert _pin == '201c7050a4705943fcabe6b2e8feb80b5475b16f362177c225d75beb8742afa6', "fixture changed"
import re
m = re.search('max_file_mb: (\\d+)\\n  allowed', case["files"]['infra/limits.yaml'])
assert m, "pattern"
ans = m.group(1)
assert ans in case["turns"][0]["expect"]["output_contains"]

print(json.dumps({"expected_string": ans}, ensure_ascii=False))
