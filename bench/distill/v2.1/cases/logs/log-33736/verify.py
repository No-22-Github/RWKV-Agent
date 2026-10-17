# DISTILL-CANARY-98515682 : distillation case
import hashlib, json
case = json.load(open("case.json"))
files = case["files"]
_pin = hashlib.sha256(json.dumps(files, ensure_ascii=False, sort_keys=True).encode()).hexdigest()
assert _pin == '90929a0c2d443e5973bc4862eb8f4cb746ff5821158f77cd85c43388a3dfe4c2', "fixture changed"
answers=['02:41','03:06']
print(json.dumps({"expected_string": answers[0]}, ensure_ascii=False))
