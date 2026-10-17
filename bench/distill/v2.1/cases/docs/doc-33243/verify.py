# DISTILL-CANARY-fdd5ff02 : distillation case
import hashlib, json
case = json.load(open("case.json"))
_pin = hashlib.sha256(json.dumps(case["files"], ensure_ascii=False, sort_keys=True).encode()).hexdigest()
assert _pin == '9ae1eaa700c7116866f0a6b4b430dee32468a63bf3892489406c85d47d06cff8', "fixture changed"
files = case["files"]
def answer(files):
    import re
    return re.search(r"Administrator accounts: change the password every (\d+) days", files["it/security-policy.md"]).group(1)

V = answer(files)
inc = [x for t in case["turns"] for x in t["expect"].get("output_contains", [])]
assert V in inc, (V, inc)
print(json.dumps({"expected_string": V}, ensure_ascii=False))
