# DISTILL-CANARY-9c48a764 : distillation case
import hashlib, json
case = json.load(open("case.json"))
_pin = hashlib.sha256(json.dumps(case["files"], ensure_ascii=False, sort_keys=True).encode()).hexdigest()
assert _pin == 'e0c95d13cd74a009c8796841b9432ec6a181ab8dfc272be8660c4c9d207df7f3', "fixture changed"
def truth(files):
    import re
    vals = [float(x) for x in re.findall(r"电费 \d+ 度 ([\d.]+) 元", files["家庭/水电气账单-2026.txt"])]
    return {"numbers": [round(sum(vals) / len(vals), 2)]}

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
