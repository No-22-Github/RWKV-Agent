# DISTILL-CANARY-eba9ff13 : distillation case
import hashlib, json
case = json.load(open("case.json"))
files = case["files"]
_pin = hashlib.sha256(json.dumps(files, ensure_ascii=False, sort_keys=True).encode()).hexdigest()
assert _pin == '8f12166620315e5f463234839c0a4f4bc5df79fdc81c61beb794d66eecba6d3f', "fixture changed"
ans = 'parse_quotes'
assert 'FAIL parse_quotes' in files['ci/ingest.log']

print(json.dumps({"expected_string": ans}, ensure_ascii=False))
