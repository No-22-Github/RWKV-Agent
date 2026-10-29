# DISTILL-CANARY-182c0708 : distillation case
import hashlib, json
case = json.load(open("case.json"))
files = case["files"]
_pin = hashlib.sha256(json.dumps(files, ensure_ascii=False, sort_keys=True).encode()).hexdigest()
assert _pin == '7413246627611ec87e3b8af9ca809094b00d38336f6704208d29333033518f85', "fixture changed"
OPS = json.loads('[["sub", "src/checkout/totals.ts", "export function calcTotal", "export function computeTotal"], ["sub", "src/checkout/totals.ts", "const t = calcTotal(items);", "const t = computeTotal(items);"], ["sub", "src/checkout/totals.ts", "`Total: ${calcTotal(items)}`", "`Total: ${computeTotal(items)}`"], ["sub", "src/checkout/totals.ts", "return calcTotal(items) === 0;", "return computeTotal(items) === 0;"]]')
end = dict(files)
for op in OPS:
    kind, path = op[0], op[1]
    if kind == "sub":
        assert end[path].count(op[2]) == 1, (path, op[2])
        end[path] = end[path].replace(op[2], op[3])
    elif kind == "set":
        end[path] = op[2]
    else:
        t = end[path]
        end[path] = (t if t.endswith("\n") or not t else t + "\n") + op[2]
print(json.dumps({"files": {p: t for p, t in end.items() if files.get(p) != t}}, ensure_ascii=False))
