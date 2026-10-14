# DISTILL-CANARY-62b5ff40 : distillation case
import hashlib, json, re
case = json.load(open("case.json"))
_pin = hashlib.sha256(json.dumps(case["files"], ensure_ascii=False, sort_keys=True).encode()).hexdigest()
assert _pin == '37fe4614ad7eff867ce63fdb2c1715d7314e181affe090ea4bc5d44ebdc2d2e9', "fixture changed"
txt = case["files"]['finance/fx-notes.txt']
m = re.search('2026-09-01 EURUSD (1\\.0834)', txt)
print(json.dumps({"expected_string": m.group(1)}, ensure_ascii=False))
