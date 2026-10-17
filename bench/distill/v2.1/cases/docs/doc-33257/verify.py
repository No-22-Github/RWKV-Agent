# DISTILL-CANARY-0341fc4e : distillation case
import hashlib, json
case = json.load(open("case.json"))
_pin = hashlib.sha256(json.dumps(case["files"], ensure_ascii=False, sort_keys=True).encode()).hexdigest()
assert _pin == '7cceb5921a020a52963c3dbcd8f2bfe74a841363bc79dbc87930c18688347b0a', "fixture changed"
files = case["files"]
def answer(files):
    import re
    return re.search(r"离职后 (\d+) 年内，不得披露", files["法务/保密与竞业.md"]).group(1)

V = answer(files)
inc = [x for t in case["turns"] for x in t["expect"].get("output_contains", [])]
assert V in inc, (V, inc)
print(json.dumps({"expected_string": V}, ensure_ascii=False))
