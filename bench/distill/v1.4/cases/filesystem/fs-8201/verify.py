# DISTILL-CANARY-ed9995b2 : distillation case
import hashlib
import json
import re

case = json.load(open("case.json"))
files = case["files"]
assert hashlib.sha256(json.dumps(files, sort_keys=True, ensure_ascii=False).encode()).hexdigest() == '127a978cba0104607df06cb5704ad8ab03d0a24aefba3b015e1e01c8da74dd5e'
ans = [p for p, t in sorted(files.items()) if "灯塔公园" in t][0]
assert ans == '纪要/0916-订场.md'
print(json.dumps({"expected_string": '0916-订场'}, ensure_ascii=False))
