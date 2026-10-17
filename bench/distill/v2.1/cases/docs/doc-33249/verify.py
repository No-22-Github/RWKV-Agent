# DISTILL-CANARY-e79e8a13 : distillation case
import hashlib, json
case = json.load(open("case.json"))
_pin = hashlib.sha256(json.dumps(case["files"], ensure_ascii=False, sort_keys=True).encode()).hexdigest()
assert _pin == '8772196ce0879b16040ff2352fbe296a3b234935e687ad44c92753e3f2e1fba6', "fixture changed"
files = case["files"]
def answer(files):
    import re
    return re.search(r"周末加班：按小时工资的 (\d+)%", files["制度/加班与调休.md"]).group(1)

V = answer(files)
inc = [x for t in case["turns"] for x in t["expect"].get("output_contains", [])]
assert V in inc, (V, inc)
print(json.dumps({"expected_string": V}, ensure_ascii=False))
