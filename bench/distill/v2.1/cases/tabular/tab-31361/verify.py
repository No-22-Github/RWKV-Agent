# DISTILL-CANARY-8b68b17b : distillation case
import hashlib, json
case = json.load(open("case.json"))
_pin = hashlib.sha256(json.dumps(case["files"], ensure_ascii=False, sort_keys=True).encode()).hexdigest()
assert _pin == 'a2a7ccd3988ddf8a47da76e890cb3e60dc858c119c318e88b404c09482e34eed', "fixture changed"
import csv, io
ans = str(sum(int(r['qty']) for r in csv.DictReader(io.StringIO(case["files"]['stock/warehouse-west.csv']))))
assert all(any(s in p or s in t for p, t in case["files"].items()) for s in case["turns"][0]["expect"].get("output_contains", []))
print(json.dumps({"expected_string": ans}, ensure_ascii=False))
assert '127' in case['turns'][1]['expect']['output_contains']
assert str(ans) == '127'
