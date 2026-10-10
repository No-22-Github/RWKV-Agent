# DISTILL-CANARY-8127143b : distillation case
import hashlib
import json
import re

case = json.load(open("case.json"))
files = case["files"]
assert hashlib.sha256(json.dumps(files, sort_keys=True, ensure_ascii=False).encode()).hexdigest() == 'ff8049144b704d376d178a4f3dc2427b4e8de3bf9aeabf63ef4415b762942926'
ans = int(re.search(r"\[weekend\]\n每小时 = (\d+)", files["停车场/费率.toml"]).group(1))
assert ans == 9
print(json.dumps({"expected_contains_any": ['9 元', '9 块', '9元', '9块']}, ensure_ascii=False))
