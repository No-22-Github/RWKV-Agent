# DISTILL-CANARY-c9c2efd4 : distillation case
import hashlib, json
case = json.load(open("case.json"))
_pin = hashlib.sha256(json.dumps(case["files"], ensure_ascii=False, sort_keys=True).encode()).hexdigest()
assert _pin == '7c9680cf8ee6860f43566cffa7a237a1c49a119faee90f69f263e9b6f4a26104', "fixture changed"
import csv, io
ans = str(sum(int(r['units']) for r in csv.DictReader(io.StringIO(case["files"]['stats/sales.csv']))))
print(json.dumps({"expected_string": ans}, ensure_ascii=False))
assert str(ans) in case['turns'][0]['expect']['output_contains']
