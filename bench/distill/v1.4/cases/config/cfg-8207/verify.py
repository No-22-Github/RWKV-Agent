# DISTILL-CANARY-72f5ba6a : distillation case
import hashlib
import json
import re

case = json.load(open("case.json"))
files = case["files"]
assert hashlib.sha256(json.dumps(files, sort_keys=True, ensure_ascii=False).encode()).hexdigest() == 'aee717c413a91410ef10125398bee45301ad439ced6fa9fb09dfbefe8a470f6c'
ans = int(re.search(r"size: (\d+)", files["config/production.yaml"]).group(1))
assert ans == 40
print(json.dumps({"expected_number": 40}))
