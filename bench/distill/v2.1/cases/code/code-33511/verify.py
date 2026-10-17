# DISTILL-CANARY-c2489106 : distillation case
import hashlib, json
case = json.load(open("case.json"))
files = case["files"]
_pin = hashlib.sha256(json.dumps(files, ensure_ascii=False, sort_keys=True).encode()).hexdigest()
assert _pin == '0cf97c67a489c4ca6be06b6adf86b26a00662418013e5acc8b5845e43cbae541', "fixture changed"
OPS = json.loads('[["sub", "shop/pricing.py", "FREE_SHIPPING_FROM = 80\\n", "FREE_SHIPPING_FROM = 100\\n"]]')
end = dict(files)
for _, path, old, new in OPS:
    assert end[path].count(old) == 1, (path, old)
    end[path] = end[path].replace(old, new)
print(json.dumps({"files": {p: t for p, t in end.items() if files[p] != t}}, ensure_ascii=False))
