# DISTILL-CANARY-94ae32b4 : distillation case
import json

case = json.load(open("case.json"))
files = case["files"]
index = files["sds/INDEX.txt"].splitlines()
assert index[0] == "product | sheet | status"
body = "\n".join(index[1:])
assert "not received yet" in body and "distributor changed" in body
assert not any(p.startswith("sds/novazyme-ex.") for p in files)
assert any(p.startswith("sds/novazyme-ex-color") for p in files)
words = ["not received", "hasn't been received", "not yet received", "no sheet", "not on file", "pending"]
print(json.dumps({"expected_contains_any": words}))
