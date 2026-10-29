# DISTILL-CANARY-360522a9 : distillation case
import hashlib, json
case = json.load(open("case.json"))
files = case["files"]
_pin = hashlib.sha256(json.dumps(files, ensure_ascii=False, sort_keys=True).encode()).hexdigest()
assert _pin == '4a827f91d8acdd96eadecdce56c8d058085cfbe4c59bfb6c44c55e367887c583', "fixture changed"
OPS = json.loads('[["sub", "web/src/format-money.js", "export function formatMoney", "import { pad } from \'./text-utils.js\';\\n\\nexport function formatMoney"], ["append", "web/src/format-money.js", "\\nexport function formatCount(n) {\\n  return pad(String(n), 6);\\n}\\n"], ["sub", "web/src/format-money.js", "export function formatCount", "// right-aligned counter\\nexport function formatCount"]]')
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
