# DISTILL-CANARY-b2a56972 : distillation case
import hashlib, json
case = json.load(open("case.json"))
files = case["files"]
_pin = hashlib.sha256(json.dumps(files, ensure_ascii=False, sort_keys=True).encode()).hexdigest()
assert _pin == 'bfc6863e277f8552d497977c4b6e1563bc3885e151f7e0c862c3281cd7b62607', "fixture changed"
import re
ans = sum(1 for p, t in files.items() if p.startswith('ops/') and not p.startswith('ops/old') for l in t.split(chr(10)) if re.search(r'#\s*(TODO|FIXME)\b', l))
assert ans == 6, ans

print(json.dumps({"expected_number": float(ans)}))
