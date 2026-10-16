# DISTILL-CANARY-ae0d0f1f : distillation case
import hashlib, json
case = json.load(open("case.json"))
files = case["files"]
_pin = hashlib.sha256(json.dumps(files, ensure_ascii=False, sort_keys=True).encode()).hexdigest()
assert _pin == 'f7b9d3a199dae7d744770428a7614e2613b9d135b2633594d3221b43f3ef4f38', "fixture changed"
ans = [l.split('\t')[2] for l in files['catalog.tsv'].splitlines()[1:] if l.split('\t')[0] == 'P108'][0]
print(json.dumps({"expected_number": float(ans)}, ensure_ascii=False))
