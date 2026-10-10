# DISTILL-CANARY-93725e40 : distillation case
import hashlib
import json
import re

case = json.load(open("case.json"))
files = case["files"]
assert hashlib.sha256(json.dumps(files, sort_keys=True, ensure_ascii=False).encode()).hexdigest() == 'e3cedc75bf5432dd606677a3a6eda356aa3c2cbe6bf7a297de144a4ce2fa4b91'
ans = int(re.search(r"integration_retries: (\d+)", files[".ci/pipeline.yml"]).group(1))
assert ans == 2
print(json.dumps({"expected_number": 2}))
