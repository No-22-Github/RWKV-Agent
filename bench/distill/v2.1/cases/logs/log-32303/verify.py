# DISTILL-CANARY-637121d7 : distillation case
import hashlib, json
case = json.load(open("case.json"))
files = case["files"]
_pin = hashlib.sha256(json.dumps(files, ensure_ascii=False, sort_keys=True).encode()).hexdigest()
assert _pin == 'd9fc92713579b8830c7242d5c02693eac36e7d4ca5612614e45b0f48088b60eb', "fixture changed"
ans = sum(1 for l in files['job_runs.csv'].split('\r\n')[1:] if l.endswith(',failed'))
print(json.dumps({"expected_number": float(ans)}, ensure_ascii=False))
