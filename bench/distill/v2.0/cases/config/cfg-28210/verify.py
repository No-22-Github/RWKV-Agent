# DISTILL-CANARY-5dd54c57 : distillation case
import hashlib
import json
import re

case = json.load(open("case.json"))
files = case["files"]
assert hashlib.sha256(json.dumps(files, sort_keys=True, ensure_ascii=False).encode()).hexdigest() == '93cf950f4c1b059765ab4f44e3d5448c690c0dea13b67cec598580be8582f15b'
ans = re.search(r"quiet_start = \"(\S+)\"", files["site/summer.toml"]).group(1)
assert ans == '23:00'
print(json.dumps({"expected_contains_any": ['23:00', '11 pm', '11 PM', '11pm', '11:00 pm', '11:00 PM']}, ensure_ascii=False))
