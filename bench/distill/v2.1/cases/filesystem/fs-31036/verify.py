# DISTILL-CANARY-b16e2824 : distillation case
import hashlib, json
case = json.load(open("case.json"))
_pin = hashlib.sha256(json.dumps(case["files"], ensure_ascii=False, sort_keys=True).encode()).hexdigest()
assert _pin == '8abb86d8c5d439da35119166311d2fa410bd66c77939b3916484cfbad2e2ef11', "fixture changed"

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

OPS = json.loads('[["sub", "site/nav.md", "(about-us.md)", "(about.md)"], ["sub", "site/index.md", "(about-us.md)", "(about.md)"], ["sub", "site/footer.md", "(about-us.md)", "(about.md)"]]')
end = apply(case["files"], OPS)
print(json.dumps({"files": {p: t for p, t in end.items() if case["files"][p] != t}}, ensure_ascii=False))
