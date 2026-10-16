# DISTILL-CANARY-6096a2a8 : distillation case
import hashlib, json
case = json.load(open("case.json"))
files = case["files"]
_pin = hashlib.sha256(json.dumps(files, ensure_ascii=False, sort_keys=True).encode()).hexdigest()
assert _pin == 'b3d844918af5edf1b2e94b21e89db760f1d39485080979898604d69276eb448f', "fixture changed"
import datetime
ans = sum(1 for l in files['sales_epoch.csv'].splitlines()[1:] if datetime.datetime.fromtimestamp(int(l.split(',')[1]), datetime.timezone.utc).day == 15)
print(json.dumps({"expected_number": float(ans)}, ensure_ascii=False))
