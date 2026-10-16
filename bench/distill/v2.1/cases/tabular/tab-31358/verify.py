# DISTILL-CANARY-1f665a88 : distillation case
import hashlib, json
case = json.load(open("case.json"))
_pin = hashlib.sha256(json.dumps(case["files"], ensure_ascii=False, sort_keys=True).encode()).hexdigest()
assert _pin == 'cdfddfb9058e7246507b1f4e8d9593367640f8be6ec5ca1baeb9fb4e5bbd5dcd', "fixture changed"
import csv, io
ans = str(sum(int(r['cost']) for r in csv.DictReader(io.StringIO(case["files"]['finance/expenses-q3.csv']))))
assert all(any(s in p or s in t for p, t in case["files"].items()) for s in case["turns"][0]["expect"].get("output_contains", []))
print(json.dumps({"expected_string": ans}, ensure_ascii=False))
assert '6650' in case['turns'][1]['expect']['output_contains']
assert str(ans) == '6650'
