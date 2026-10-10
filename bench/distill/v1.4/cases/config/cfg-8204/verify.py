# DISTILL-CANARY-f9a8937c : distillation case
import hashlib
import json
import re

case = json.load(open("case.json"))
files = case["files"]
assert hashlib.sha256(json.dumps(files, sort_keys=True, ensure_ascii=False).encode()).hexdigest() == 'b19c6a8dd0fdfe7a33eb2089e3ffec9e9412e4e811ad0062eda73558a850ffb2'
ans = int(re.search(r"取蜜间隔天=(\d+)", files["养蜂场/prod.env"]).group(1))
assert ans == 9
print(json.dumps({"expected_contains_any": ['9 天', '9 日', '9天', '9日']}, ensure_ascii=False))
