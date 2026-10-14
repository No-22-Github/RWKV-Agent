# DISTILL-CANARY-c5a9050e : distillation case
import hashlib
import json
import re

case = json.load(open("case.json"))
files = case["files"]
assert hashlib.sha256(json.dumps(files, sort_keys=True, ensure_ascii=False).encode()).hexdigest() == 'fb0ffef3b745340254323575e92981253f9f7279461d3a3c817e768763f310a4'
ans = re.search(r"3 到 7 天，退 (\d+)%", files["营地/预订须知.md"]).group(1)
assert ans == '50'
print(json.dumps({"expected_contains_any": ['50%', '50 %', '五成', '一半', '50％', '百分之五十']}, ensure_ascii=False))
