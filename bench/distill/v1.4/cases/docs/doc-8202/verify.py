# DISTILL-CANARY-853d813d : distillation case
import hashlib
import json
import re

case = json.load(open("case.json"))
files = case["files"]
assert hashlib.sha256(json.dumps(files, sort_keys=True, ensure_ascii=False).encode()).hexdigest() == 'a888c299d93dfbcbe4c15f299db71e0ec0e54c9e1b25b79d1974ac717578af09'
ans = re.search(r"约 (\d+) 小时", files["常见问题/补牙后.md"]).group(1)
assert ans == '2'
print(json.dumps({"expected_contains_any": ['2 小时', '2 个小时', '2小时', '2个小时']}, ensure_ascii=False))
