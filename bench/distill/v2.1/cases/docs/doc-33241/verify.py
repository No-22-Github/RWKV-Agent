# DISTILL-CANARY-44c18825 : distillation case
import hashlib, json
case = json.load(open("case.json"))
_pin = hashlib.sha256(json.dumps(case["files"], ensure_ascii=False, sort_keys=True).encode()).hexdigest()
assert _pin == '211a19d22ddfd770db0a749e4c4f66836e0b50386e00cd1a9ce592eb4a324e0d', "fixture changed"
files = case["files"]
def answer(files):
    import re
    return re.search(r"Postgraduates: books (\d+) days", files["library/loan-rules.md"]).group(1)

V = answer(files)
inc = [x for t in case["turns"] for x in t["expect"].get("output_contains", [])]
assert V in inc, (V, inc)
print(json.dumps({"expected_string": V}, ensure_ascii=False))
