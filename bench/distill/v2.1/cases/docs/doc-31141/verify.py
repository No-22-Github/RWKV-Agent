# DISTILL-CANARY-6351662a : distillation case
import hashlib, json
case = json.load(open("case.json"))
_pin = hashlib.sha256(json.dumps(case["files"], ensure_ascii=False, sort_keys=True).encode()).hexdigest()
assert _pin == 'eb4dd44759c841846d443d15e98b85f7fbb4220dfd2e61c4e81fbfb5a6304c1f', "fixture changed"
def compute(files):
    ls = [l for l in files["食谱/原料.txt"].strip().split("\n") if not l.startswith("白糖")]
    return {"食谱/购物单.md": "# 购物单\n\n" + "".join("- [ ] %s\n" % l for l in sorted(ls))}

FINAL = compute(dict(case["files"]))
for path, rule in case["expect"]["files"].items():
    if "equals" in rule:
        assert FINAL[path] == rule["equals"], path
    elif "contains" in rule:
        assert all(s in FINAL[path] for s in rule["contains"]), path
    elif rule.get("unchanged"):
        assert path in case["files"] and path not in FINAL, path
print(json.dumps({"files": {k: v for k, v in FINAL.items() if k in case["expect"]["files"]}}, ensure_ascii=False))
