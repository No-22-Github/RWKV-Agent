# DISTILL-CANARY-34d912a1 : distillation case
import hashlib, json
case = json.load(open("case.json"))
_pin = hashlib.sha256(json.dumps(case["files"], ensure_ascii=False, sort_keys=True).encode()).hexdigest()
assert _pin == 'f8eee938c611933d50a0a11ab0f922954ca6336e338ee49fbb424e6cda0ecdd5', "fixture changed"
def truth(files):
    import datetime
    import re
    s = re.search(r"Lease start: (\d{4}-\d\d-\d\d)", files["contracts/marlow-lease-terms.txt"]).group(1)
    return {"strings": [(datetime.date.fromisoformat(s) + datetime.timedelta(days=100)).isoformat()]}

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
