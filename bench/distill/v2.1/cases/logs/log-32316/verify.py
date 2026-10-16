# DISTILL-CANARY-e08d140a : distillation case
import hashlib, json
case = json.load(open("case.json"))
files = case["files"]
_pin = hashlib.sha256(json.dumps(files, ensure_ascii=False, sort_keys=True).encode()).hexdigest()
assert _pin == 'bd099ef0e98777bd9f3fabc4088b6697f228c2e1906ed4d3e59eaed696061b89', "fixture changed"
ans = sum(1 for l in files['service.log'].splitlines() if l.split()[2] == 'ERROR')
print(json.dumps({"expected_number": float(ans)}, ensure_ascii=False))
