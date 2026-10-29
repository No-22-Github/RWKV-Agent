# DISTILL-CANARY-86fdaf83 : distillation case
import hashlib, json
case = json.load(open("case.json"))
_pin = hashlib.sha256(json.dumps(case["files"], ensure_ascii=False, sort_keys=True).encode()).hexdigest()
assert _pin == 'ed571ebe5f2439daaed1cedfbae5d3d000c27af94fe8a16a93357304f838a4a7', "fixture changed"
def truth(files):
    from decimal import Decimal, ROUND_HALF_UP
    rows = [l.split(",") for l in files["fleet/fuel-log-q3b.csv"].strip().split("\n")[1:] if l.split(",")[1] == "TRK-14"]
    c = sum(Decimal(r[3]) for r in rows)
    li = sum(Decimal(r[2]) for r in rows)
    return {"numbers": [float(c), float((c / li).quantize(Decimal("0.01"), ROUND_HALF_UP))]}

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
