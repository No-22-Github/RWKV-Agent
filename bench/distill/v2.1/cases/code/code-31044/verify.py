# DISTILL-CANARY-2f9fc339 : distillation case
import hashlib, json
case = json.load(open("case.json"))
_pin = hashlib.sha256(json.dumps(case["files"], ensure_ascii=False, sort_keys=True).encode()).hexdigest()
assert _pin == '023fa29f0e5993465983b45ac5a08b104ba2871515f668c325984c27004382b6', "fixture changed"

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

OPS = json.loads('[["sub", "locales/menu.txt", "quit=退出", "exit=退出"], ["sub", "src/menu.py", "\'quit\']", "\'exit\']"], ["sub", "src/menu.py", "{\'quit\':", "{\'exit\':"], ["sub", "docs/menu.md", "open、quit。", "open、exit。"], ["sub", "docs/menu.md", "Ctrl+Q", "Ctrl+W"]]')
end = apply(case["files"], OPS)
print(json.dumps({"files": {p: t for p, t in end.items() if case["files"][p] != t}}, ensure_ascii=False))
