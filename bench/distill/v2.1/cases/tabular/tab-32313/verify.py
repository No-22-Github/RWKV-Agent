# DISTILL-CANARY-4e61a31d : distillation case
import hashlib, json
case = json.load(open("case.json"))
files = case["files"]
_pin = hashlib.sha256(json.dumps(files, ensure_ascii=False, sort_keys=True).encode()).hexdigest()
assert _pin == '29633717c4198a7046ea0a090fa03c3dc11be33adbba6c2454afc2eb424b3058', "fixture changed"
ans = sum(int(l.split('\t')[2]) for l in files['sales_0915.tsv'].splitlines()[1:])
print(json.dumps({"expected_number": float(ans)}, ensure_ascii=False))
