# DISTILL-CANARY-c7f4ebec : distillation case
import hashlib
import json
import re

case = json.load(open("case.json"))
files = case["files"]
assert hashlib.sha256(json.dumps(files, sort_keys=True, ensure_ascii=False).encode()).hexdigest() == 'cf231a114ca975cf9f27317fc244005e8968ea33a799290087493270af8d268d'
ans = re.search(r"最晚入住时间: (\S+)", files["规则/入住.yaml"]).group(1)
assert ans == '22:00'
print(json.dumps({"expected_contains_any": ['22:00', '22 点', '22点', '晚上 10 点', '晚上10点', '十点']}, ensure_ascii=False))
