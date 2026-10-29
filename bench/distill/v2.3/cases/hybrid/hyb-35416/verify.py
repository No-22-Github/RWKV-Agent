# DISTILL-CANARY-3e290fb4 : distillation case
import hashlib, json
case = json.load(open("case.json"))
_pin = hashlib.sha256(json.dumps(case["files"], ensure_ascii=False, sort_keys=True).encode()).hexdigest()
assert _pin == '92e114249d1b6512c0944ff8c3380b33cee0a394bafedd6beaef31d8be1fe7f4', "fixture changed"
def truth(files):
    import re
    return {"strings": [re.search(r"^request_timeout = (\d+)", files["service/gateway.toml"], re.M).group(1)]}

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
