# DISTILL-CANARY-72348cfc : distillation case
import hashlib, json
case = json.load(open("case.json"))
_pin = hashlib.sha256(json.dumps(case["files"], ensure_ascii=False, sort_keys=True).encode()).hexdigest()
assert _pin == 'dc5da72d15aae75f5dd47e53c3193f12dae08ca158f597d453bd34153cc853f8', "fixture changed"
import csv, io
ans = str(sum(int(r['amount']) for r in csv.DictReader(io.StringIO(case["files"]['sales/sales-2026-08.csv']))))
assert all(any(s in p or s in t for p, t in case["files"].items()) for s in case["turns"][0]["expect"].get("output_contains", []))
print(json.dumps({"expected_string": ans}, ensure_ascii=False))
assert '3940' in case['turns'][1]['expect']['output_contains']
assert str(ans) == '3940'
