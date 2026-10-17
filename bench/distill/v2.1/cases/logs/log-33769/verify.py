# DISTILL-CANARY-9ad3b947 : distillation case
import hashlib, json
case = json.load(open("case.json"))
files = case["files"]
_pin = hashlib.sha256(json.dumps(files, ensure_ascii=False, sort_keys=True).encode()).hexdigest()
assert _pin == '7be9adc69f0910f09938c9a0f2767e704a3869e665b909c86ad447648424863c', "fixture changed"
ls=files['node.log'].splitlines()
answers=[str(sum(1 for l in ls if not l.endswith('heartbeat'))), str(sum(1 for l in ls if l.endswith('reconnect')))]
print(json.dumps({"expected_number": float(answers[0])}, ensure_ascii=False))
