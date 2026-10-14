# DISTILL-CANARY-2cdea62d : distillation case
import hashlib, json, re
case = json.load(open("case.json"))
_pin = hashlib.sha256(json.dumps(case["files"], ensure_ascii=False, sort_keys=True).encode()).hexdigest()
assert _pin == '8e70f8f9e4484c06ee87759cd7fa6b75b2f81e9a050e3510a1c64cc15f727b08', "fixture changed"
rows = [l.split(",") for l in case["files"]["销售/销量.csv"].splitlines()[1:]]
t = sum(int(x[1]) for x in rows)
print(json.dumps({"expected_number": round(int(rows[0][1]) * 100 / t, 1), "total": t}))
