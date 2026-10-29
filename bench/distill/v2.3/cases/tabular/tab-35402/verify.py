# DISTILL-CANARY-7a51eef7 : distillation case
import hashlib, json
case = json.load(open("case.json"))
_pin = hashlib.sha256(json.dumps(case["files"], ensure_ascii=False, sort_keys=True).encode()).hexdigest()
assert _pin == '24533ebd7fed480ff7a0b16aa0070914f8aea8dd373edab5fd9b2e7fdc3f59a1', "fixture changed"
def truth(files):
    rows = [l.split(",") for l in files["采购/2026q3-办公耗材申购.csv"].strip().split("\n")[1:]]
    from decimal import Decimal, ROUND_HALF_UP
    s = sum(Decimal(r[1]) * Decimal(r[2]) for r in rows) * Decimal("0.92")
    return {"numbers": [float(s.quantize(Decimal("0.01"), ROUND_HALF_UP))]}

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
