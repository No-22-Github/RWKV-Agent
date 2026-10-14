# DISTILL-CANARY-a15458c8 : distillation case
import hashlib
import json
import re

case = json.load(open("case.json"))
files = case["files"]
assert hashlib.sha256(json.dumps(files, sort_keys=True, ensure_ascii=False).encode()).hexdigest() == '7920302e21d76008f2a2d8ef70d955bb5aa7df6fa451a235e442cba80908a0b7'
ans = int(re.search(r"mash_temp_c=(\d+)", files["recipes/stout.cfg"]).group(1))
assert ans == 67
print(json.dumps({"expected_number": 67}))
