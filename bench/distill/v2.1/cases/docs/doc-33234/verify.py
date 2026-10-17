# DISTILL-CANARY-26ffc25a : distillation case
import hashlib, json
case = json.load(open("case.json"))
_pin = hashlib.sha256(json.dumps(case["files"], ensure_ascii=False, sort_keys=True).encode()).hexdigest()
assert _pin == '3a314a0ca34337c27b6c864ab5cf9f4d837b886eaa6a53a602714b16ccff2309', "fixture changed"
files = case["files"]
def compute(files):
    ver, nums = "", []
    for l in files["RELEASES.md"].split("\n"):
        if l.startswith("## "):
            ver = l[3:]
        elif l.startswith("- fix:") and ver.startswith("3.1."):
            nums.append(l.split("(#")[1].rstrip(")"))
    return {"fixed-3.1.txt": "".join(n + "\n" for n in sorted(nums, key=int))}

FINAL = compute(dict(files))
for path, rule in case["expect"]["files"].items():
    if "equals" in rule:
        assert FINAL[path] == rule["equals"], path
    elif "contains" in rule:
        assert all(s in FINAL[path] for s in rule["contains"]), path
print(json.dumps({"files": {k: v for k, v in FINAL.items() if k in case["expect"]["files"] and "unchanged" not in case["expect"]["files"][k]}}, ensure_ascii=False))
