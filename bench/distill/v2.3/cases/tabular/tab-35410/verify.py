# DISTILL-CANARY-1d1597bf : distillation case
import hashlib, json
case = json.load(open("case.json"))
_pin = hashlib.sha256(json.dumps(case["files"], ensure_ascii=False, sort_keys=True).encode()).hexdigest()
assert _pin == 'ad223ec87172be373820cf96bbd0fa4f7726a3e80a86852b1266581205bd7c83', "fixture changed"
def truth(files):
    rows = [l.split(",") for l in files["仓库/出入库流水-9月.csv"].strip().split("\n")[1:] if l.split(",")[1] == "B-2207"]
    i = sum(int(r[3]) for r in rows if r[2] == "入")
    o = sum(int(r[3]) for r in rows if r[2] == "出")
    return {"numbers": [float(i), float(i - o)]}

got = truth(case["files"])
nums = got.get("numbers")
if nums is not None:
    tn = [t for t in case["turns"] if "expected_number" in t["expect"]]
    assert len(tn) == len(nums)
    for t, x in zip(tn, nums):
        assert abs(t["expect"]["expected_number"] - x) < 1e-9
for p, txt in (got.get("files") or {}).items():
    assert case["expect"]["files"][p]["equals"] == txt
for s in got.get("strings", []):
    assert any(s in t["expect"].get("output_contains", []) for t in case["turns"])
if got.get("files"):
    print(json.dumps({"files": got["files"]}, ensure_ascii=False))
elif nums is not None:
    print(json.dumps({"expected_number": float(nums[0])}))
else:
    print(json.dumps({"expected_string": got["strings"][0]}, ensure_ascii=False))
