# DISTILL-CANARY-0bfa00d5 : distillation case
import hashlib, json
case = json.load(open("case.json"))
_pin = hashlib.sha256(json.dumps(case["files"], ensure_ascii=False, sort_keys=True).encode()).hexdigest()
assert _pin == '3982d8e735db08a357fa60f659f1f9e37014eb744f2cd9b94ce73ebfc96afa0b', "fixture changed"
import csv, io
ans = str(sum(int(r['cost']) for r in csv.DictReader(io.StringIO(case["files"]['finance/expenses-q3.csv']))))
print(json.dumps({"expected_string": ans}, ensure_ascii=False))
assert str(ans) in case['turns'][0]['expect']['output_contains']
