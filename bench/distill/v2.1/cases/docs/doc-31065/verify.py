# DISTILL-CANARY-e8a8d309 : distillation case
import hashlib, json
case = json.load(open("case.json"))
_pin = hashlib.sha256(json.dumps(case["files"], ensure_ascii=False, sort_keys=True).encode()).hexdigest()
assert _pin == 'ab91ed0c30d3bcf6650e613686aa8ae152d87318d7ff3557a1639f2d833bc056', "fixture changed"

def apply(files, ops):
    out = dict(files)
    for op in ops:
        if op[0] == "sub":
            _, path, old, new = op
            assert out[path].count(old) == 1, (path, old)
            out[path] = out[path].replace(old, new)
        elif op[0] == "app":
            out[op[1]] = out[op[1]] + op[2]
    return out

OPS = json.loads('[["sub", "table/prices.md", "| 商品 | 单价 | 库存 |\\n| --- | --- | --- |\\n| 茶叶 | 38 | 120 |\\n| 咖啡豆 | 66 | 80 |\\n| 糖 | 9 | 300 |\\n", "| 商品 | 单价 | 库存 | 备注 |\\n| --- | --- | --- | --- |\\n| 茶叶 | 38 | 120 | 新品 |\\n| 咖啡豆 | 66 | 80 |  |\\n| 糖 | 9 | 300 |  |\\n"]]')
end = apply(case["files"], OPS)
print(json.dumps({"files": {p: t for p, t in end.items() if case["files"][p] != t}}, ensure_ascii=False))
