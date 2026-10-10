# DISTILL-CANARY-c503e174 : distillation case
import hashlib
import json
import re

case = json.load(open("case.json"))
files = case["files"]
assert hashlib.sha256(json.dumps(files, sort_keys=True, ensure_ascii=False).encode()).hexdigest() == 'b5779665053171fefa19576b36bc70cf12c32ee35d603e5303bab86c15e9d992'
ans = len({p.split("/")[0] for p in files if "/" in p})
assert ans == 5
print(json.dumps({"expected_number": 5}))
