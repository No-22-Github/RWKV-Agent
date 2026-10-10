# DISTILL-CANARY-4e0cc8c5 : distillation case
import hashlib
import json
import re

case = json.load(open("case.json"))
files = case["files"]
assert hashlib.sha256(json.dumps(files, sort_keys=True, ensure_ascii=False).encode()).hexdigest() == '52ed3d0808c6cf0fc9bd5926bccbbb205efcdf7cf723b2e8e1078c68e779e7a9'
ans = [p for p, t in sorted(files.items()) if "FAILED" in t][0]
assert ans == 'calibration/2026-06.txt'
print(json.dumps({"expected_string": '2026-06'}, ensure_ascii=False))
