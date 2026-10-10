# DISTILL-CANARY-d62181e9 : distillation case
import hashlib
import json
import re

case = json.load(open("case.json"))
files = case["files"]
assert hashlib.sha256(json.dumps(files, sort_keys=True, ensure_ascii=False).encode()).hexdigest() == 'cd8f9677ba9e3881b3c2e941b5ac8f56558033cb1d0fa46eb82ed7a7b2594d4e'
ans = int(re.search(r"报警温度 = (\d+)", files["电站/全局.ini"]).group(1))
assert ans == 75
print(json.dumps({"expected_contains_any": ['75 度', '75度', '75 ℃', '75℃', '75°C', '75 °C']}, ensure_ascii=False))
