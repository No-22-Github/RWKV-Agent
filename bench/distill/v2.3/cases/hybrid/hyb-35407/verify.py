# DISTILL-CANARY-89481831 : distillation case
import hashlib, json
case = json.load(open("case.json"))
_pin = hashlib.sha256(json.dumps(case["files"], ensure_ascii=False, sort_keys=True).encode()).hexdigest()
assert _pin == '85bc732ee517848078a460d6c91b2ccb7c89ea1558a593f509a74e3902efda60', "fixture changed"
def truth(files):
    import re
    vals = [float(m.replace(",", "")) for m in re.findall(r": ([\d,]+\.\d\d)$", files["trip/lisbon-expenses.txt"], re.M)]
    t = sum(vals)
    return {"numbers": [round(t / 4, 2), round(t / 5, 2)]}

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
